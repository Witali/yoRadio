"""Capture public owned floor0 arithmetic on native ESP32/C3; qualify no PCM.

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
PROJECT = ROOT/'tests/target/vorbis_floor0_numeric_qemu'
COMPONENT = ROOT/'idf/components/native_vorbis_numeric'
PARTS = {'source': 'floor0.c', 'header': 'include/native_vorbis_floor0.h', 'component': 'CMakeLists.txt'}
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
API = ('prepare_valid', 'prepare_in_place', 'prepare_invalid', 'denominator_invalid',
       'gain_invalid', 'gain_absent', 'gain_pole', 'gain_indeterminate', 'gain_unity',
       'gain_at_cosine_absent', 'bark_valid', 'bark_invalid', 'bin_cardinals',
       'bin_invalid', 'gain_at_bin_valid', 'gain_at_bin_invalid')
PUBLIC = ('prepare_cosines', 'denominator', 'gain_from_denominator', 'gain_at_cosine',
          'bark_map', 'bin_cosine', 'gain_at_bin')


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


def validate_cases(document, header):
    need(document['schema'] == 'native-vorbis-floor0-numeric-cases-v1' and
         isinstance(document['cases'], list) and 1 <= len(document['cases']) <= 512, 'finite coefficient/gain corpus')
    rows, ids = document['cases'], set()
    fields = {'id', 'operation', 'raw_amplitude', 'amplitude_bits', 'amplitude_offset',
              'coefficients_hex', 'w_hex', 'denominator_mantissa_hex', 'denominator_exponent'}
    for row in rows:
        need(set(row) == fields and isinstance(row['id'], str) and re.fullmatch('[A-Za-z0-9_-]{1,63}', row['id']) and
             row['id'] not in ids and row['operation'] in ('curve', 'gain'), 'unique exact case fields/id/operation')
        ids.add(row['id'])
        need(isinstance(row['raw_amplitude'], str) and re.fullmatch('0|[1-9][0-9]*', row['raw_amplitude']), 'decimal uint64 amplitude')
        raw = int(row['raw_amplitude'])
        need(all(type(row[k]) is int for k in ('amplitude_bits', 'amplitude_offset', 'denominator_exponent')) and
             0 <= row['amplitude_bits'] <= 63 and 0 <= row['amplitude_offset'] <= 255 and
             0 <= raw <= (1 << row['amplitude_bits'])-1 and -2147483648 <= row['denominator_exponent'] <= 2147483647,
             'complete public amplitude/exponent domains')
        coefficients = row['coefficients_hex']
        need(isinstance(coefficients, list) and ((1 <= len(coefficients) <= 255) if row['operation'] == 'curve' else not coefficients), 'declared coefficient order')
        values = [number(value) for value in coefficients]+[number(row['w_hex'])]
        need(all(math.isfinite(value) and -2 <= value <= 2 for value in values), 'finite exact coefficient/cosine input domain')
        d = number(row['denominator_mantissa_hex'])
        if row['operation'] == 'gain':
            need(math.isfinite(d) and ((d == 0 and row['denominator_exponent'] == 0) or 0.5 <= d < 1), 'normalized nonnegative direct denominator')
    counts = re.findall(r'^#define\s+FLOOR0_NUMERIC_CASE_COUNT\s+(\d+)[Uu]?\s*$', header, re.M)
    need(counts == [str(len(rows))], 'one exact materialized case count')
    coefficient_arrays = {}
    for match in re.finditer(r'static\s+const\s+uint64_t\s+floor0_coefficients_(\d+)\s*\[\s*(\d*)\s*\]\s*=\s*\{(.*?)\};', header, re.S):
        index, capacity, body = int(match[1]), match[2], match[3]
        need(index not in coefficient_arrays, 'unique coefficient array')
        values = [item[1] for item in sequence(body, re.compile(r'UINT64_C\(\s*0x([0-9a-f]{16})\s*\)'))]
        need(not capacity or int(capacity) == len(values), 'coefficient array capacity')
        coefficient_arrays[index] = values
    need(set(coefficient_arrays) == {i for i, row in enumerate(rows) if row['operation'] == 'curve'}, 'exact complete coefficient-array inventory')
    arrays = re.findall(r'floor0_numeric_cases\s*\[[^]]*\]\s*=\s*\{(.*?)\};', header, re.S)
    need(len(arrays) == 1, 'one complete descriptor array')
    integer = r'(\d+)[Uu]?'
    u64 = r'UINT64_C\(\s*(0x[0-9a-f]+|[0-9]+)\s*\)'
    pattern = re.compile(r'\{\s*"([A-Za-z0-9_-]+)"\s*,\s*'+integer+r'\s*,\s*'+u64+r'\s*,\s*'+
                         integer+r'\s*,\s*'+integer+r'\s*,\s*'+integer+r'\s*,\s*'+u64+
                         r'\s*,\s*(floor0_coefficients_\d+|NULL)\s*,\s*'+u64+r'\s*,\s*(?:INT32_C\(\s*(-?\d+)\s*\)|(-?\d+))\s*\}')
    actual = sequence(arrays[0], pattern)
    need(len(actual) == len(rows), 'complete C descriptor count')
    for index, (row, match) in enumerate(zip(rows, actual)):
        values = match.groups(); operation = 1 if row['operation'] == 'curve' else 2
        pointer = 'floor0_coefficients_'+str(index) if operation == 1 else 'NULL'
        expect = (row['id'], operation, int(row['raw_amplitude']), row['amplitude_bits'], row['amplitude_offset'],
                  len(row['coefficients_hex']), int(row['w_hex'], 16), pointer,
                  int(row['denominator_mantissa_hex'], 16), row['denominator_exponent'])
        parsed = (values[0], int(values[1]), int(values[2], 16 if values[2].startswith('0x') else 10),
                  int(values[3]), int(values[4]), int(values[5]), int(values[6], 16 if values[6].startswith('0x') else 10),
                  values[7], int(values[8], 16 if values[8].startswith('0x') else 10), int(values[9] if values[9] is not None else values[10]))
        need(parsed == expect and (operation != 1 or coefficient_arrays[index] == row['coefficients_hex']), 'every exact C descriptor/coefficient bit')
    return rows


def validate_log(log, rows, target, data_sha256):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out', log, re.I), 'target panic/corruption/timeout')
    prefix = 'FLOOR0_NUMERIC_'; lines = log.splitlines()
    need(not any(prefix in line and not line.startswith(prefix) for line in lines), 'foreign/truncated numeric event')
    events = [line for line in lines if line.startswith(prefix)]; core = 1 if target == 'esp32' else 0
    expected = [f'{prefix}BEGIN cases={len(rows)} coordinator=0 worker={core} data={data_sha256}',
                f'{prefix}WORKER core={core} priority=3 stack=16384']
    expected += [f'{prefix}API index={i} name={name} ok=1 core={core}' for i, name in enumerate(API)]
    need(events[:len(expected)] == expected and len(events) == len(expected)+len(rows)+2, 'ordered worker/API groups and exact event count')
    captured = []
    keys = {'case', 'id', 'operation', 'order', 'ds', 'denominator_bits', 'denominator_exponent', 'gs', 'kind',
            'log2_bits', 'log2_exponent', 'guards', 'unchanged', 'core'}
    for index, (row, event) in enumerate(zip(rows, events[len(expected):])):
        tokens = event.split(' '); need(tokens[0] == prefix+'CASE' and all(t.count('=') == 1 for t in tokens[1:]), 'case event syntax')
        fields = dict(token.split('=') for token in tokens[1:]); need(set(fields) == keys and len(fields)+1 == len(tokens), 'exact unique case fields')
        for key in keys-{'id', 'denominator_bits', 'log2_bits'}:
            need(re.fullmatch('0|-?[1-9][0-9]*', fields[key]), 'canonical event integer'); fields[key] = int(fields[key])
        need(fields['case'] == index and fields['id'] == row['id'] and fields['operation'] == (1 if row['operation'] == 'curve' else 2) and
             fields['order'] == len(row['coefficients_hex']) and fields['ds'] == (0 if row['operation'] == 'curve' else -99) and
             fields['gs'] == 0 and 0 <= fields['kind'] <= 3 and fields['guards'] == fields['unchanged'] == 1 and fields['core'] == core,
             'complete original ordered guarded math case')
        for bit_key, exponent_key in (('denominator_bits', 'denominator_exponent'), ('log2_bits', 'log2_exponent')):
            value, exponent = number(fields[bit_key]), fields[exponent_key]
            need(math.isfinite(value) and -2147483648 <= exponent <= 2147483647 and
                 ((value == 0 and exponent == 0) or 0.5 <= abs(value) < 1), 'normalized finite scaled capture')
        need(number(fields['denominator_bits']) >= 0 and (fields['kind'] == 0 or
             (number(fields['log2_bits']) == 0 and fields['log2_exponent'] == 0)), 'finite public result shape, without reference qualification')
        if row['operation'] == 'gain':
            need(fields['denominator_bits'] == row['denominator_mantissa_hex'] and fields['denominator_exponent'] == row['denominator_exponent'], 'direct denominator is input only/not called')
        fields['operation'] = row['operation']; captured.append(fields)
    need(events[-2:] == [f'{prefix}COMPLETE cases={len(rows)} api={len(API)} core={core}', f'{prefix}STOP status=CAPTURED'], 'controlled complete capture stop')
    return dict(cases=len(rows), protocol_lines=len(events), api_groups=len(API), coordinator_core=0,
                worker_core=core, priority=3, configured_stack=16384, rows=captured)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=SDK_HEAD, required=True)
    for name in ('output', 'cases', 'idf', 'idf-tools', 'powershell', 'sdk-python', 'qemu', 'rom'):
        parser.add_argument('--'+name, type=Path, required=True)
    pins = ('source', 'header', 'component', 'cases', 'cases-header', 'qemu')
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
                  commands=[], inputs={}, tools={}, build_outputs={}, rows=[], source_sha256=pin)
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
            '-SourceSha256', pin['source'], '-HeaderSha256', pin['header'], '-ComponentSha256', pin['component'], '-CasesSha256', pin['cases']], 1200)
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
        for name, source in (('fixture', out/'project/main/main.c'), ('module', out/'sources/components/native_vorbis_numeric/floor0.c')):
            found = [row for row in database if Path(row['file']).resolve() == source]
            need(len(found) == 1, 'exact native compile row '+name); selected[name] = found[0]
        report['compile_rows'] = selected
        need('-fno-fast-math' in selected['module']['command'] and '-fstack-usage' in selected['module']['command'], 'actual module floating/stack compiler flags')
        objects = [normalize(selected[name]['output']) for name in ('fixture', 'module')]
        need(all((build/path).is_file() for path in objects), 'actual compiled objects')
        dependencies = normalize(run('dependencies', [ninja, '-C', build, '-t', 'deps', *objects])).casefold()
        for source in (out/'sources/components/native_vorbis_numeric/floor0.c', out/'sources/components/native_vorbis_numeric/include/native_vorbis_floor0.h', out/'project/main/cases.h'):
            need(normalize(source).casefold() in dependencies, 'actual module/header/data dependency')
        report['whole_module_compiled'] = True
        symbols = run('symbols', [nm, '-n', '-S', elf])
        need(all(re.search(r'\bnative_vorbis_floor0_'+name+r'$', symbols, re.M) for name in PUBLIC), 'all seven actual public numerical symbols')
        need(not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_(?:open|decode)$', symbols, re.M), 'no stream decoder symbol')
        map_file = elf.with_suffix('.map'); need(map_file.is_file() and b'libesp_audio_codec.a' not in map_file.read_bytes(), 'no vendor codec archive')
        usage = list(build.rglob('*floor0*.su')); need(len(usage) == 1, 'one actual whole-module stack-usage file')
        frames = []
        for line in usage[0].read_text(encoding='utf-8').splitlines():
            fields = line.rsplit('\t', 2); need(len(fields) == 3 and fields[1].isdigit(), 'actual GCC stack-usage row')
            frames.append(dict(function=fields[0].rsplit(':', 1)[-1], bytes=int(fields[1]), qualifier=fields[2]))
        need(all(any(row['function'] == 'native_vorbis_floor0_'+name for row in frames) for name in PUBLIC), 'stack estimates for all public module functions')
        report['stack_usage'] = dict(path=usage[0].relative_to(out).as_posix(), rows=frames, scope='Compiler per-function frames only; no callee/libm/task high-water or physical-performance claim.')
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
        files = [elf, map_file, flash, usage[0], out/'sdkconfig', out/'elf-header.bin', out/'sdk-child.json',
                 out/'sdk-build.stdout.log', out/'sdk-build.stderr.log', *flash_files.values()]
        files += [build/name for name in ('compile_commands.json', 'project_description.json', 'flasher_args.json', 'CMakeCache.txt', 'config/sdkconfig.h', 'build.ninja', 'CMakeFiles/rules.ninja')]
        report['build_outputs'] = {path.relative_to(out).as_posix(): sha(path) for path in files}
        report['build_warning_lines'] = [line for name in ('sdk-build.stdout.log', 'sdk-build.stderr.log') for line in (out/name).read_text(encoding='utf-8', errors='replace').splitlines() if re.search(r'\bwarning:', line)]
        current(); need(all(sha(out/path) == digest for path, digest in report['build_outputs'].items()), 'selected actual build bytes changed')
        report.update(completed=True, math_capture_completed=True, source_inputs_unchanged=True, result='CHECKED_MATH_CAPTURED',
                      limitations='Math values and finite API/guard checks only; independent Decimal comparison pending. No complete floor0/synthesis/PCM/radio/real-time/QMP EOF/physical qualification or full SDK dependency closure.')
        save(); print(json.dumps(dict(completed=True, math_capture_completed=True, target=a.target, cases=len(rows), numerical_qualified=False, result=report['result']))); return 0
    except BaseException as error:
        report.update(completed=False, math_capture_completed=False, result='NONPASS', error=repr(error)); save(); raise


if __name__ == '__main__': sys.exit(main())
