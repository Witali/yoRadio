"""Capture owned VQ quantization and exact affine handoff; qualify no PCM.

The independent Decimal comparison is a separate step with a predeclared policy.
Exit0 means complete guarded math capture, not numerical reference acceptance.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT/'tests/target/vorbis_quantization_qemu'
COMPONENT = ROOT/'idf/components/native_vorbis_numeric'
PARTS = {'source': 'floor0.c', 'header': 'include/native_vorbis_floor0.h', 'quant-source': 'quant.c',
         'quant-header': 'include/native_vorbis_quant.h', 'component': 'CMakeLists.txt'}
DEPENDENCIES = ('codebook.c', 'include/native_vorbis_codebook.h', 'setup.c', 'include/native_vorbis_setup.h',
                'floor_packet.c', 'include/native_vorbis_floor_packet.h')
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
OPS = {'vector': 1, 'floor': 2, 'affine': 3, 'scalar': 4}
AFFINE = ('minimum_bits', 'delta_bits', 'minimum_multiplier', 'delta_multiplier')
LAYOUT = ('dimensions', 'entries', 'lookup_type', 'minimum_bits', 'delta_bits', 'value_bits', 'sequence_p',
          'multiplicand_count', 'start_bit', 'multiplicand_bit', 'end_bit')
PUBLIC = ('quantization_count', 'quantization_measure', 'quantization_materialize', 'quantization_vector',
          'quantization_scalar', 'floor0_lsp_from_entries', 'floor0_denominator_from_affine',
          'floor0_gain_from_affine', 'floor0_gain_from_denominator')


def need(ok, reason):
    if not ok: raise ValueError(reason)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def normalize(value): return str(value).replace('\\', '/').rstrip('/')


def number(bits):
    need(isinstance(bits, str) and re.fullmatch('[0-9a-f]{16}', bits), 'exact IEEE binary64 bits')
    return struct.unpack('>d', bytes.fromhex(bits))[0]


def sequence(body, pattern):
    matches, cursor = list(pattern.finditer(body)), 0
    for index, match in enumerate(matches):
        need(re.fullmatch(r'\s*' if not index else r'\s*,\s*', body[cursor:match.start()]), 'literal C comma separators')
        cursor = match.end()
    need(re.fullmatch(r'\s*,?\s*', body[cursor:]), 'literal C array tail')
    return matches


def packet_model(row):
    data = bytes.fromhex(row['packet_hex']); value = int.from_bytes(data, 'little'); position = row['start_bit']
    def field(width):
        nonlocal position
        need(width <= row['packet_bits']-position, 'complete scientific quantization packet')
        result = (value >> position) & ((1 << width)-1); position += width; return result
    lookup = field(4); need(lookup in (1, 2), 'scientific VQ lookup1/2, lookup0 in API controls')
    minimum, delta, width, seq = field(32), field(32), field(4)+1, field(1)
    if lookup == 2: count = row['dimensions']*row['entries']
    elif row['dimensions'] >= row['entries'].bit_length(): count = 1
    else:
        low, high = 1, row['entries']
        while low < high:
            mid = (low+high+1)//2
            if pow(mid, row['dimensions']) <= row['entries']: low = mid
            else: high = mid-1
        count = low
    need(count <= 255, 'bounded target multiplicand storage')
    first = position; weights = [field(width) for _ in range(count)]
    return dict(zip(LAYOUT, (row['dimensions'], row['entries'], lookup, minimum, delta, width, seq,
                            count, row['start_bit'], first, position))), weights


def validate_cases(document, header):
    need(document['schema'] == 'native-vorbis-quantization-cases-v1' and isinstance(document['cases'], list) and
         1 <= len(document['cases']) <= 512, 'finite mixed quantization corpus')
    rows, ids = document['cases'], set()
    keys = {'id', 'operation', 'dimensions', 'entries', 'start_bit', 'packet_bits', 'packet_hex', 'entry_numbers',
            'length', 'component', 'affine', 'bridge', 'bin', 'map_size', 'raw_amplitude', 'amplitude_bits', 'amplitude_offset'}
    for row in rows:
        need(set(row) == keys and re.fullmatch('[A-Za-z0-9_-]{1,63}', row['id']) and row['id'] not in ids and row['operation'] in OPS, 'unique exact case identity/shape')
        ids.add(row['id'])
        ints = ('dimensions', 'entries', 'length', 'component', 'bin', 'map_size', 'amplitude_bits', 'amplitude_offset')
        need(all(type(row[k]) is int and 0 <= row[k] <= 0xffffffff for k in ints) and
             all(type(row[k]) is int and 0 <= row[k] <= 0xffffffffffffffff for k in ('packet_bits', 'start_bit')),
             'unsigned metadata fields')
        need(row['dimensions'] <= 65535 and row['entries'] <= 0xffffff and row['length'] <= 255 and type(row['bridge']) is bool and
             isinstance(row['raw_amplitude'], str) and re.fullmatch('0|[1-9][0-9]*', row['raw_amplitude']) and
             row['amplitude_bits'] <= 63 and row['amplitude_offset'] <= 255 and int(row['raw_amplitude']) < 1 << row['amplitude_bits'], 'bounded target/public amplitude metadata')
        need(isinstance(row['packet_hex'], str) and re.fullmatch('(?:[0-9a-f]{2})*', row['packet_hex']) and len(row['packet_hex']) <= 2048 and
             row['start_bit'] <= row['packet_bits'] <= 4*len(row['packet_hex']), 'exact bounded packet bit extent')
        need(isinstance(row['entry_numbers'], list) and len(row['entry_numbers']) <= 255 and
             all(type(x) is int and 0 <= x <= 0xffffffff for x in row['entry_numbers']) and isinstance(row['affine'], list), 'entry/affine arrays')
        need(len(row['affine']) <= 255 and all(set(x) == set(AFFINE) and all(type(x[k]) is int and 0 <= x[k] <= 0xffffffff for k in AFFINE) for x in row['affine']), 'four exact affine uint32 values')
        if row['operation'] == 'affine':
            need(row['length'] == len(row['affine']) and not row['entry_numbers'] and not row['packet_hex'] and
                 all(row[k] == 0 for k in ('dimensions', 'entries', 'packet_bits', 'start_bit', 'component')), 'direct-affine input only')
        else:
            need(row['dimensions'] > 0 and row['entries'] > 0 and not row['affine'] and all(x < row['entries'] for x in row['entry_numbers']), 'scientific VQ metadata')
            packet_model(row)
            if row['operation'] == 'floor': need(1 <= row['length'] <= 255 and len(row['entry_numbers']) == (row['length']-1)//row['dimensions']+1 and row['component'] == 0, 'complete floor prefix entries')
            elif row['operation'] == 'scalar': need(row['length'] == 1 and len(row['entry_numbers']) == 1 and row['component'] < row['dimensions'], 'single scalar component')
            else: need(row['length'] <= row['dimensions'] and len(row['entry_numbers']) == 1 and row['component'] == 0, 'valid vector prefix')
        if row['bridge']: need(row['length'] > 0 and 1 <= row['map_size'] <= 65535 and row['bin'] < row['map_size'], 'valid optional floor bridge')
    need(re.findall(r'^#define\s+QUANTIZATION_CASE_COUNT\s+(\d+)\s*$', header, re.M) == [str(len(rows))], 'one exact C case count')
    specifications = [('uint8_t', 'quant_packet_', re.compile(r'UINT8_C\(0x([0-9a-f]{2})\)'), lambda m: int(m[1], 16)),
        ('uint32_t', 'quant_entries_', re.compile(r'UINT32_C\((\d+)\)'), lambda m: int(m[1])),
        ('native_vorbis_affine_t', 'quant_affine_', re.compile(r'\{'+r'\s*,\s*'.join([r'\s*UINT32_C\((\d+)\)\s*']*4)+r'\}'), lambda m: dict(zip(AFFINE, map(int, m.groups()))))]
    recovered = []
    for type_name, prefix, item, convert in specifications:
        found = {}
        for match in re.finditer(r'static\s+const\s+'+type_name+r'\s+'+prefix+r'(\d+)\[\]\s*=\s*\{(.*?)\};', header, re.S):
            index = int(match[1]); need(index not in found, 'unique materialized input array')
            found[index] = [convert(m) for m in sequence(match[2], item)]
        recovered.append(found)
    expected_arrays = [{i:list(bytes.fromhex(r['packet_hex'])) for i,r in enumerate(rows) if r['packet_hex']},
                       {i:r['entry_numbers'] for i,r in enumerate(rows) if r['entry_numbers']}, {i:r['affine'] for i,r in enumerate(rows) if r['affine']}]
    need(recovered == expected_arrays, 'every packet byte/entry/exact affine field recovered')
    arrays = re.findall(r'quantization_cases\[[^]]*\]\s*=\s*\{(.*?)\};', header, re.S); need(len(arrays) == 1, 'one descriptor array')
    matches = sequence(arrays[0], re.compile(r'\{([^{}]*)\}')); need(len(matches) == len(rows), 'complete descriptor count')
    for i,(row,match) in enumerate(zip(rows,matches)):
        pointer = lambda prefix, present: prefix+str(i) if present else 'NULL'
        expected = ['"'+row['id']+'"',str(OPS[row['operation']]),str(row['dimensions']),str(row['entries']),
            'UINT64_C('+str(row['packet_bits'])+')','UINT64_C('+str(row['start_bit'])+')',pointer('quant_packet_',row['packet_hex']),str(len(row['packet_hex'])//2),
            pointer('quant_entries_',row['entry_numbers']),str(len(row['entry_numbers'])),str(row['length']),str(row['component']),pointer('quant_affine_',row['affine']),str(len(row['affine'])),
            str(int(row['bridge'])),str(row['bin']),str(row['map_size']),'UINT64_C('+row['raw_amplitude']+')',str(row['amplitude_bits']),str(row['amplitude_offset'])]
        need([re.sub(r'\s+','',x) for x in match[1].split(',')] == expected, 'all twenty literal descriptor fields')
    return rows


def validate_log(log, rows, target, data_sha256):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out', log, re.I), 'target panic/corruption/timeout')
    prefix = 'QUANTIZATION_'; lines = log.splitlines()
    need(not any(prefix in line and not line.startswith(prefix) for line in lines), 'foreign/truncated numeric event')
    events = [line for line in lines if line.startswith(prefix)]; core = 1 if target == 'esp32' else 0
    cursor, captured = 0, []
    def take(kind, expected, extra=()):
        nonlocal cursor
        need(cursor < len(events), 'missing ordered event'); tokens = events[cursor].split(' '); cursor += 1
        need(tokens[0] == prefix+kind and all(t.count('=') == 1 for t in tokens[1:]), 'event kind/syntax')
        fields = dict(t.split('=') for t in tokens[1:])
        need(set(fields) == set(expected)|set(extra) and len(fields)+1 == len(tokens) and
             all(fields[k] == str(v) for k,v in expected.items()), 'exact unique ordered event fields')
        return fields
    def integer(value, maximum=0xffffffffffffffff):
        need(re.fullmatch('0|-?[1-9][0-9]*', value), 'canonical integer'); n=int(value)
        need(-2147483648 <= n <= maximum, 'bounded event integer'); return n
    take('BEGIN',dict(cases=len(rows),coordinator=0,worker=core,data=data_sha256)); take('WORKER',dict(core=core,priority=3,stack=16384)); take('CONTROLS',dict(checks=152,core=core))
    for index,row in enumerate(rows):
        status=-99 if row['operation']=='affine' else 0
        take('CASE',dict(case=index,id=row['id'],operation=OPS[row['operation']],length=row['length'],bridge=int(row['bridge']),measure_status=status,materialize_status=status,decode_status=status,core=core))
        layout, multiplicands = None, []
        if row['operation'] != 'affine':
            fields=take('LAYOUT',dict(case=index,core=core),LAYOUT); layout={}
            for key in LAYOUT:
                if key in ('minimum_bits','delta_bits'): need(re.fullmatch('[0-9a-f]{8}',fields[key]), 'exact packed uint32 bits'); layout[key]=int(fields[key],16)
                else: layout[key]=integer(fields[key],0xffffffff if key in LAYOUT[:7] else 0xffffffffffffffff); need(layout[key]>=0, 'unsigned layout field')
            fields=take('MULT',dict(case=index,core=core),('count','hex')); count=integer(fields['count'],255)
            need(count>=0 and count==layout['multiplicand_count'] and (fields['hex']=='-' if not count else re.fullmatch('[0-9a-f]{'+str(4*count)+'}',fields['hex'])), 'complete raw multiplicands')
            multiplicands=[int(fields['hex'][4*i:4*i+4],16) for i in range(count)]
        fields=take('VALUES',dict(case=index,count=row['length'],core=core),('hex',)); count=row['length']
        need(fields['hex']=='-' if not count else re.fullmatch('[0-9a-f]{'+str(32*count)+'}',fields['hex']), 'complete raw affine values')
        values=[dict(zip(AFFINE,[int(fields['hex'][32*i+8*j:32*i+8*j+8],16) for j in range(4)])) for i in range(count)]
        fields=take('MATH',dict(case=index,core=core),('ds','denominator_bits','denominator_exponent','gs','kind','log2_bits','log2_exponent'))
        math_row={key:(value if key.endswith('_bits') else integer(value,2147483647)) for key,value in fields.items() if key not in ('case','core')}
        if row['bridge']:
            need(math_row['ds']==math_row['gs']==0 and 0<=math_row['kind']<=3, 'successful finite affine bridge')
            for bit_key,exp_key in (('denominator_bits','denominator_exponent'),('log2_bits','log2_exponent')):
                value,exp=number(math_row[bit_key]),math_row[exp_key]
                need(math.isfinite(value) and ((value==0 and exp==0) or .5<=abs(value)<1), 'normalized finite scaled output')
            need(number(math_row['denominator_bits'])>=0 and (math_row['kind']==0 or (number(math_row['log2_bits'])==0 and math_row['log2_exponent']==0)), 'public bridge result shape')
        else: need(math_row==dict(ds=-99,gs=-99,kind=-99,denominator_bits='0'*16,denominator_exponent=0,log2_bits='0'*16,log2_exponent=0), 'bridge not called')
        take('END',dict(case=index,guards=1,unchanged=1,core=core))
        captured.append(dict(case=index,id=row['id'],operation=row['operation'],measure_status=status,materialize_status=status,decode_status=status,
                             layout=layout,multiplicands=multiplicands,values=values,**math_row,guards=1,unchanged=1,core=core))
    take('COMPLETE',dict(cases=len(rows),controls=152,core=core)); take('STOP',dict(status='CAPTURED')); need(cursor==len(events),'no extra/trailing events')
    return dict(cases=len(rows),protocol_lines=len(events),metadata_controls=152,coordinator_core=0,worker_core=core,priority=3,configured_stack=16384,rows=captured)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=SDK_HEAD, required=True)
    for name in ('output', 'cases', 'idf', 'idf-tools', 'powershell', 'sdk-python', 'qemu', 'rom'):
        parser.add_argument('--'+name, type=Path, required=True)
    pins = (*PARTS, 'cases', 'cases-header', 'qemu')
    for name in pins: parser.add_argument('--'+name+'-sha256', required=True)
    a = parser.parse_args(); need(sys.platform == 'win32', 'pinned Windows SDK launcher')
    pin = {name: getattr(a, name.replace('-', '_')+'_sha256') for name in pins}
    need(all(re.fullmatch('[0-9a-f]{64}', value) for value in pin.values()), 'explicit lowercase source/data/tool hashes')
    out, cases, sdk, tools, ps, py, qemu, rom = [getattr(a, name).resolve() for name in
        ('output', 'cases', 'idf', 'idf_tools', 'powershell', 'sdk_python', 'qemu', 'rom')]
    git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    required = [*[COMPONENT/name for name in PARTS.values()], cases/'cases.json', cases/'cases.h',
                sdk/'export.ps1', sdk/'tools/idf.py', ps, py, qemu, git]
    need(all(path.is_file() for path in required) and rom.is_dir() and any(rom.glob(a.target+'*rom*.bin')), 'required source/tool/ROM files')
    need(out.is_relative_to(ROOT/'.build') and out != ROOT/'.build' and not out.exists(), 'fresh task-local output')
    need(not any(out == path or out.is_relative_to(path) or path.is_relative_to(out) for path in
                 (COMPONENT, PROJECT, cases, sdk, tools, ps.parent, py.parent, qemu.parent, rom)), 'source/runtime/output separation')
    for path, key in [(COMPONENT/name, part) for part, name in PARTS.items()]+[(cases/'cases.json', 'cases'), (cases/'cases.h', 'cases-header'), (qemu, 'qemu')]:
        need(sha(path) == pin[key], 'reviewed identity '+str(path))
    rows = validate_cases(json.loads((cases/'cases.json').read_bytes()), (cases/'cases.h').read_text(encoding='ascii'))
    out.mkdir(parents=True)
    report = dict(completed=False, passed=False, target=a.target, result='NONPASS', math_capture_completed=False,
                  numerical_reference_compared=False, numerical_qualified=False, full_floor0_qualified=False,
                  decoder_executed=False, production_firmware=False, physical_device=False,
                  whole_module_compiled=False, source_inputs_unchanged=False, sdk_revision=SDK_HEAD[a.target],
                  commands=[], inputs={}, tools={}, build_outputs={}, rows=[], source_sha256=pin,
                  input_domain='Original packed Vorbis quantization metadata, integer multiplicands and exact affine VQ values; optional floor math')
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0')

    def save(): (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    def freeze(path, relative):
        dest = out/'sources'/relative; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(path.read_bytes())
        report['inputs'][str(path.resolve())] = dict(snapshot=dest.relative_to(out).as_posix(), bytes=dest.stat().st_size, sha256=sha(dest))
    def current():
        need(all(sha(path) == value['sha256'] == sha(out/value['snapshot']) for path, value in report['inputs'].items()), 'original/frozen source changed')
        need(all(sha(path) == value for path, value in report['tools'].items()), 'recorded tools changed')
        need(all(sha(out/path) == value for path, value in report.get('project_sources', {}).items()), 'configured fixture changed')

    def run(name, argv, timeout=60):
        argv = list(map(str, argv)); row = dict(name=name, argv=argv, cwd=str(out), state='starting', timeout_seconds=timeout, timed_out=False, interrupted=False)
        report['commands'].append(row); save(); so, se = out/(name+'.stdout.log'), out/(name+'.stderr.log')
        child, start = None, time.monotonic()
        try:
            with so.open('xb') as stdout, se.open('xb') as stderr:
                child = subprocess.Popen(argv, cwd=out, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(pid=child.pid, state='running'); save(); child.wait(timeout=timeout)
                row.update(state='complete', exit_status=child.returncode)
        except BaseException as error:
            row.update(state='failed', error=repr(error), timed_out=isinstance(error, subprocess.TimeoutExpired), interrupted=isinstance(error, KeyboardInterrupt)); raise
        finally:
            if child is not None and child.poll() is None:
                row['state'] = 'forced_stop_nonpass'
                try:
                    stopped = subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'], capture_output=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
                    row['tree_stop_returncode'] = stopped.returncode
                except Exception as error: row['tree_stop_error'] = repr(error)
                finally:
                    if child.poll() is None: child.kill()
                    child.wait(timeout=15)
            row.update(elapsed_seconds=time.monotonic()-start, stdout_sha256=sha(so) if so.is_file() else None, stderr_sha256=sha(se) if se.is_file() else None)
            if child is not None: row['exit_status'] = child.poll()
            save()
        need(row['state'] == 'complete' and row['exit_status'] == 0, name+' did not terminate normally/successfully')
        return so.read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')

    save()
    try:
        for path in (py, ps, qemu, git, *sorted(rom.glob(a.target+'*rom*.bin'))): report['tools'][str(path)] = sha(path)
        need(run('sdk-head', [git, '-c', 'core.longpaths=true', '-C', sdk, 'rev-parse', 'HEAD']).strip() == SDK_HEAD[a.target], 'SDK revision')
        need(not run('sdk-clean', [git, '-c', 'core.longpaths=true', '-C', sdk, 'status', '--porcelain', '--untracked-files=no']).strip(), 'SDK clean')
        for name in PARTS.values(): freeze(COMPONENT/name, Path('components/native_vorbis_numeric')/name)
        for name in DEPENDENCIES:
            if (COMPONENT/name).is_file(): freeze(COMPONENT/name, Path('components/native_vorbis_numeric')/name)
        freeze(Path(__file__), Path('controller.py'))
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file(): freeze(path, Path('project')/path.relative_to(PROJECT))
        for name in ('cases.json', 'cases.h'): freeze(cases/name, Path('cases')/name)
        shutil.copytree(out/'sources/project', out/'project'); shutil.copyfile(out/'sources/cases/cases.h', out/'project/main/cases.h')
        shutil.copyfile(out/'sources/project'/('sdkconfig.'+a.target+'.defaults'), out/'project/sdkconfig.defaults')
        report['project_sources'] = {path.relative_to(out).as_posix(): sha(path) for path in (out/'project').rglob('*') if path.is_file()}
        current()
        run('build', [ps, '-NoProfile', '-NonInteractive', '-File', out/'sources/project/sdk-build.ps1', '-Campaign', out,
            '-SdkDirectory', sdk, '-ToolsDirectory', tools, '-PythonExecutable', py, '-Target', a.target,
            '-SourceSha256', pin['source'], '-HeaderSha256', pin['header'], '-QuantSourceSha256', pin['quant-source'],
            '-QuantHeaderSha256', pin['quant-header'], '-ComponentSha256', pin['component'], '-CasesSha256', pin['cases']], 1200)
        child = json.loads((out/'sdk-child.json').read_text(encoding='utf-8-sig'))
        need(type(child['pid']) is int and child['pid'] > 0 and child['exit_status'] == 0, 'actual SDK child terminal'); report['sdk_child'] = child
        build = out/'build'; description = json.loads((build/'project_description.json').read_bytes()); elf = build/description['app_elf']
        need(elf.resolve().is_relative_to(build) and struct.unpack_from('<H', elf.read_bytes(), 18)[0] == (94 if a.target == 'esp32' else 243), 'native ELF machine')
        report['elf_machine'] = 94 if a.target == 'esp32' else 243; (out/'elf-header.bin').write_bytes(elf.read_bytes()[:52])
        compiler = Path(description['c_compiler']); nm = compiler.with_name(compiler.name.replace('gcc', 'nm'))
        make = re.findall(r'^CMAKE_MAKE_PROGRAM:FILEPATH=(.+)$', (build/'CMakeCache.txt').read_text(encoding='utf-8'), re.M)
        need(len(make) == 1, 'one configured Ninja'); ninja = Path(make[0].strip())
        for path in (compiler, nm, ninja): need(path.is_file(), 'actual configured tool'); report['tools'][str(path)] = sha(path)
        database = json.loads((build/'compile_commands.json').read_bytes()); selected = {}
        for name, source in (('fixture', out/'project/main/main.c'), ('floor', out/'sources/components/native_vorbis_numeric/floor0.c'),
                             ('quant', out/'sources/components/native_vorbis_numeric/quant.c')):
            found = [row for row in database if Path(row['file']).resolve() == source]
            need(len(found) == 1, 'exact native compile row '+name); selected[name] = found[0]
        report['compile_rows'] = selected
        need(all('-fno-fast-math' in selected[name]['command'] and '-fstack-usage' in selected[name]['command']
                 for name in ('floor', 'quant')), 'actual whole module floating/stack compiler flags')
        objects = [normalize(selected[name]['output']) for name in ('fixture', 'floor', 'quant')]
        need(all((build/path).is_file() for path in objects), 'actual compiled objects')
        dependencies = normalize(run('dependencies', [ninja, '-C', build, '-t', 'deps', *objects])).casefold()
        for source in (*[out/'sources/components/native_vorbis_numeric'/PARTS[name] for name in ('source', 'header', 'quant-source', 'quant-header')], out/'project/main/cases.h'):
            need(normalize(source).casefold() in dependencies, 'actual module/header/data dependency')
        report['whole_module_compiled'] = True
        symbols = run('symbols', [nm, '-n', '-S', elf])
        need(all(re.search(r'\bnative_vorbis_'+name+r'$', symbols, re.M) for name in PUBLIC), 'actual quantization and affine comparison API symbols')
        need(not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_(?:open|decode)$', symbols, re.M), 'no stream decoder symbol')
        map_file = elf.with_suffix('.map'); need(map_file.is_file() and b'libesp_audio_codec.a' not in map_file.read_bytes(), 'no vendor codec archive')
        usage = [build/Path(selected[name]['output']).with_suffix('.su') for name in ('floor', 'quant')]
        need(len(set(usage)) == 2 and all(path.is_file() for path in usage), 'both actual module stack-usage files')
        frames = []
        for path in usage:
            for line in path.read_text(encoding='utf-8').splitlines():
                fields = line.rsplit('\t', 2); need(len(fields) == 3 and fields[1].isdigit(), 'actual GCC stack-usage row')
                frames.append(dict(function=fields[0].rsplit(':', 1)[-1], bytes=int(fields[1]), qualifier=fields[2], path=path.relative_to(out).as_posix()))
        need(all(any(row['function'] == 'native_vorbis_'+name for row in frames) for name in PUBLIC), 'stack estimates for exercised quantization and affine comparison APIs')
        report['stack_usage'] = dict(paths=[path.relative_to(out).as_posix() for path in usage], rows=frames, scope='Compiler per-function frames only; no callee/libm/task high-water or physical-performance claim.')
        recipe = json.loads((build/'flasher_args.json').read_bytes())
        need(recipe['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'), 'isolated flash profile')
        flash_files = {int(offset, 0): (build/name).resolve() for offset, name in recipe['flash_files'].items()}
        need(set(flash_files) == ({4096, 32768, 65536} if a.target == 'esp32' else {0, 32768, 65536}) and all(path.is_relative_to(build) for path in flash_files.values()), 'isolated native boot/image recipe')
        flash = out/'qemu-flash.bin'; argv = [py, '-m', 'esptool', '--chip', a.target, 'merge-bin', '--output', flash, '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(flash_files.items()): argv += [hex(offset), path]
        run('merge', argv+['--pad-to-size', '4MB'])
        config = (out/'sdkconfig').read_text(encoding='utf-8')
        need(bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (a.target == 'esp32c3') and
             re.search(r'^CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ='+str(240 if a.target == 'esp32' else 160)+'$', config, re.M), 'native CPU/core profile')
        qargs = [qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet'] if a.target == 'esp32' else [qemu, '-M', 'esp32c3']
        qargs += ['-smp', '2' if a.target == 'esp32' else '1', '-L', rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none', '-drive', 'file='+str(flash)+',if=mtd,format=raw']
        current(); log = run('qemu', qargs, 300)
        observed = validate_log(log+'\n'+(out/'qemu.stderr.log').read_text(encoding='utf-8', errors='replace'), rows, a.target, pin['cases'])
        report['rows'] = observed.pop('rows'); report['observed'] = observed
        need(run('sdk-head-after', [git, '-c', 'core.longpaths=true', '-C', sdk, 'rev-parse', 'HEAD']).strip() == SDK_HEAD[a.target], 'SDK revision after')
        need(not run('sdk-clean-after', [git, '-c', 'core.longpaths=true', '-C', sdk, 'status', '--porcelain', '--untracked-files=no']).strip(), 'SDK clean after')
        files = [elf, map_file, flash, *usage, out/'sdkconfig', out/'elf-header.bin', out/'sdk-child.json',
                 out/'sdk-build.stdout.log', out/'sdk-build.stderr.log', *flash_files.values()]
        files += [build/name for name in ('compile_commands.json', 'project_description.json', 'flasher_args.json', 'CMakeCache.txt', 'config/sdkconfig.h', 'build.ninja', 'CMakeFiles/rules.ninja')]
        report['build_outputs'] = {path.relative_to(out).as_posix(): sha(path) for path in files}
        report['build_warning_lines'] = [line for name in ('sdk-build.stdout.log', 'sdk-build.stderr.log') for line in (out/name).read_text(encoding='utf-8', errors='replace').splitlines() if re.search(r'\bwarning:', line)]
        current(); need(all(sha(out/path) == digest for path, digest in report['build_outputs'].items()), 'selected actual build bytes changed')
        report.update(completed=True, math_capture_completed=True, source_inputs_unchanged=True, result='CHECKED_QUANTIZATION_CAPTURED',
                      limitations='Raw quantization/affine values and API/guard checks captured; independent Fraction/Decimal comparison pending. No complete floor0/synthesis/PCM/radio/real-time/QMP EOF/physical qualification or full SDK dependency closure.')
        save(); print(json.dumps(dict(completed=True, math_capture_completed=True, target=a.target, cases=len(rows), numerical_qualified=False, result=report['result']))); return 0
    except BaseException as error:
        report.update(completed=False, math_capture_completed=False, result='NONPASS', error=repr(error)); save(); raise


if __name__ == '__main__': sys.exit(main())
