"""Complete raw434/public owned synthesis on pinned native ESP32/C3 QEMU.

The original31 contract remains unchanged: all738560 PCM bytes, error<=2,
all14 relations, original packet spans, no alignment/scale/channel fitting.
"""
import argparse
import hashlib
import io
import json
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
PROJECT = ROOT / 'tests/target/vorbis_synthesis_qemu'
COMPONENTS = ('native_vorbis_numeric', 'native_vorbis_setup_owner', 'native_vorbis_packet_frame',
    'native_vorbis_floor1_product', 'native_vorbis_floor0_spectrum', 'native_vorbis_transform',
    'native_vorbis_window', 'native_vorbis_window_exact', 'native_vorbis_pcm_exact',
    'native_vorbis_timing', 'native_vorbis_synthesis')
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
QEMU_SHA = {'esp32': '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d',
            'esp32c3': 'a74f3324430b306618aa88a52649dbb93c32eac6d0b87926d335754346abbf0b'}
ORIGINAL_SHA = '32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'
ORIGINAL_ARCHIVE_SHA = '3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea'
REFERENCE_ARCHIVE_SHA = 'f31167f2a52e8e8a8f01e20cbadb3597d1394931bd2dfd2ac67a0381e2d6985b'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def original_inputs():
    archive = (ROOT / 'tests/results/vorbis-floor1-product-20261026/captures.zip').read_bytes()
    need(sha(archive) == ORIGINAL_ARCHIVE_SHA, 'pinned original source archive')
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        body = source.read('frame03/sources/original31.json')
    need(sha(body) == ORIGINAL_SHA, 'unchanged original31 raw model')
    model = json.loads(body)
    rows = model['cases']
    need(len(rows) == 31 and [r['case'] for r in rows] == list(range(31)), 'complete ordered31')
    need(model['policy']['max_abs_error'] == 2 and len(model['relations']) == 14, 'unchanged bound and relations')
    need(sum(r['pcm_bytes'] for r in rows) == 738560 and sum(len(r['frames']) for r in rows) == 434,
         'complete original PCM and packets')
    reference_archive = (ROOT / 'tests/results/vorbis-xiph-packets-20261026/captures.zip').read_bytes()
    need(sha(reference_archive) == REFERENCE_ARCHIVE_SHA, 'pinned retained reference archive')
    references = {}
    with zipfile.ZipFile(io.BytesIO(reference_archive)) as source:
        for row in rows:
            reference = source.read('host/sources/cases/' + row['reference_path'])
            need(len(reference) == row['pcm_bytes'] and sha(reference) == row['reference_pcm_sha256'],
                 'complete original reference: ' + row['id'])
            need(row['channels'] == 2 and row['long_block'] <= 2048 and row['frames'][0] == 0 and
                 len(row['offsets']) == 15 and len(row['granules']) == len(row['modes']) == 14,
                 'original bounded stereo shape')
            need(row['offsets'][0] == 0 and row['offsets'][-1] == len(bytes.fromhex(row['audio_hex'])) and
                 all(a < b for a, b in zip(row['offsets'], row['offsets'][1:])), 'exact packet byte extents')
            need([sum(row['frames'][:i+1]) for i in range(14)] == row['granules'], 'original packet granules')
            references[row['id']] = reference
    need(sum(len(bytes.fromhex(r[k + '_hex'])) for r in rows for k in ('identification', 'setup', 'audio')) == 7376 and
         sum(len(bytes.fromhex(r['comment_hex'])) for r in rows) == 1798, 'all raw header/audio bytes')
    return body, model, references


def header(model):
    lines = ['#pragma once', '#include "vorbis_synthesis_pipeline.h"', '#define SYN_CASE_COUNT 31']
    for i, row in enumerate(model['cases']):
        for key in ('identification', 'setup', 'audio'):
            lines.append('static const uint8_t syn_' + key + str(i) + '[]={' +
                         ','.join(str(x) for x in bytes.fromhex(row[key + '_hex'])) + '};')
        for key, ctype in (('offsets', 'uint32_t'), ('granules', 'int64_t')):
            lines.append('static const ' + ctype + ' syn_' + key + str(i) + '[]={' +
                         ','.join(str(x) for x in row[key]) + '};')
    lines.append('static const char *const syn_names[SYN_CASE_COUNT]={' +
                 ','.join('"' + r['id'] + '"' for r in model['cases']) + '};')
    lines.append('static const vorbis_synthesis_pipeline_case_t syn_cases[SYN_CASE_COUNT]={')
    for i, row in enumerate(model['cases']):
        fields = ['syn_' + k + str(i) for k in ('identification', 'setup', 'audio')]
        fields += [str(len(bytes.fromhex(row[k + '_hex']))) for k in ('identification', 'setup', 'audio')]
        fields += ['syn_offsets' + str(i), 'syn_granules' + str(i), '14']
        lines.append('{' + ','.join(fields) + '},')
    return ('\n'.join(lines + ['};', ''])).encode('ascii')


def validate_log(log, model, references, target, output=None):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out',
                       log, re.I), 'native panic/corruption/timeout')
    need(not any('SYN_' in line and not line.startswith('SYN_') for line in log.splitlines()), 'foreign/torn synthesis event')
    events = iter(line for line in log.splitlines() if line.startswith('SYN_'))
    core = 1 if target == 'esp32' else 0
    event_count = 0

    def take(kind, fixed, extra=()):
        nonlocal event_count
        line = next(events, None)
        need(line is not None, 'missing synthesis event')
        fields = line.split(' ')
        need(fields[0] == 'SYN_' + kind and all(x.count('=') == 1 for x in fields[1:]), 'ordered synthesis event syntax')
        row = dict(x.split('=') for x in fields[1:])
        need(len(row) + 1 == len(fields) and set(row) == set(fixed) | set(extra) and
             all(row[key] == str(value) for key, value in fixed.items()), 'unique exact event fields: ' + kind)
        event_count += 1
        return row

    def integer(text, maximum=(1 << 64) - 1):
        need(re.fullmatch(r'0|[1-9][0-9]*', text) is not None, 'canonical unsigned integer')
        value = int(text)
        need(value <= maximum, 'bounded integer extent')
        return value

    take('BEGIN', dict(cases=31, coordinator=0, worker=core, data=ORIGINAL_SHA))
    take('WORKER', dict(core=core, priority=3, stack=16384))
    captured, metrics = {}, []
    for index, case in enumerate(model['cases']):
        take('CASE', dict(row=index, id=case['id'], core=core))
        data = bytearray()
        previous_block = 0
        floor0 = 2 if case['id'].startswith('floor0-') else 0
        for ordinal, count in enumerate(case['frames']):
            block = case['long_block'] if case['modes'][ordinal] else case['short_block']
            available = (previous_block + block) // 4 if ordinal else 0
            metadata = take('PACKET', dict(row=index, packet=ordinal, block=block, channels=2,
                floor0=floor0, floor1=2-floor0, available=available, discard_start=0,
                discard_end=available-count, frames=count, position=1, end=case['granules'][ordinal],
                samples=count*2, core=core), ('bits', 'eop'))
            need(integer(metadata['bits']) <= (case['offsets'][ordinal+1]-case['offsets'][ordinal])*8 and
                 metadata['eop'] in ('0', '1'), 'actual bounded packet bit-reader metadata')
            position = 0
            while position < count * 2:
                n = min(128, count*2-position)
                payload = take('PCM', dict(row=index, packet=ordinal, start=position, count=n, core=core), ('runs',))
                expanded, previous = [], None
                for run in payload['runs'].split(','):
                    match = re.fullmatch(r'([0-9a-f]{4}):([1-9][0-9]*)', run)
                    need(match is not None, 'literal S16 RLE witness')
                    value, length = int(match[1], 16), integer(match[2], 128)
                    need(value != previous and 0 < length <= n-len(expanded), 'maximal bounded RLE')
                    expanded.extend([value] * length)
                    previous = value
                need(len(expanded) == n, 'complete lossless PCM chunk')
                data.extend(struct.pack('<' + 'H'*n, *expanded))
                position += n
            previous_block = block
        end = take('END', dict(row=index, status=0, packets=14, frames=sum(case['frames']),
            samples=sum(case['frames'])*2, floor0=floor0*14, floor1=(2-floor0)*14,
            live_allocations=0, live_bytes=0, core=core),
            ('allocations', 'releases', 'peak_allocations', 'peak_bytes', 'stack_free', 'heap_free', 'heap_min'))
        values = {key: integer(end[key], (1 << 32)-1) for key in
                  ('allocations', 'releases', 'peak_allocations', 'peak_bytes', 'stack_free', 'heap_free', 'heap_min')}
        need(0 < values['allocations'] == values['releases'] and
             0 < values['peak_allocations'] <= values['allocations'] and values['peak_bytes'] > 0 and
             0 < values['stack_free'] <= 16384 and 0 < values['heap_min'] <= values['heap_free'],
             'cleanup and cumulative native resource observations')
        data = bytes(data)
        need(len(data) == case['pcm_bytes'], 'every original PCM byte captured')
        captured[case['id']] = data
        if output is not None:
            (output / (str(index).zfill(2) + '-' + case['id'] + '.s16le')).write_bytes(data)
        metrics.append(dict(id=case['id'], pcm_bytes=len(data), pcm_sha256=sha(data), **values))
    take('COMPLETE', dict(cases=31, packets=434, frames=184640, samples=369280, core=core))
    take('STOP', dict(status='CAPTURED'))
    need(next(events, None) is None, 'no extra synthesis events')
    max_error = 0
    for case, metric in zip(model['cases'], metrics):
        observed, reference = captured[case['id']], references[case['id']]
        errors = [abs(a[0]-b[0]) for a, b in zip(struct.iter_unpack('<h', observed), struct.iter_unpack('<h', reference))]
        metric['maximum_absolute_error'] = max(errors, default=0)
        metric['changed_samples'] = sum(error != 0 for error in errors)
        max_error = max(max_error, metric['maximum_absolute_error'])
        need(metric['maximum_absolute_error'] <= 2, 'unchanged PCM error2 contract: ' + case['id'])
    for relation in model['relations']:
        values = [captured[name] for name in relation['cases']]
        need((all(value == values[0] for value in values[1:])) if relation['kind'] == 'equal'
             else any(value != values[0] for value in values[1:]), 'all original relation identities')
    return dict(passed=True, cases=31, packets=434, pcm_bytes=738560, pcm_samples=369280,
                maximum_absolute_error=max_error, relations=14, rows=metrics, protocol_lines=event_count,
                pcm_sha256=sha(b''.join(captured[row['id']] for row in model['cases'])),
                coordinator_core=0, worker_core=core)


def protocol_controls(model, references, target):
    core = 1 if target == 'esp32' else 0
    lines = [f'SYN_BEGIN cases=31 coordinator=0 worker={core} data={ORIGINAL_SHA}',
             f'SYN_WORKER core={core} priority=3 stack=16384']
    def event(kind, **values):
        lines.append('SYN_' + kind + ' ' + ' '.join(str(k)+'='+str(v) for k, v in values.items()))
    for i, row in enumerate(model['cases']):
        event('CASE', row=i, id=row['id'], core=core)
        at = previous = 0
        floor0 = 2 if row['id'].startswith('floor0-') else 0
        for p, frames in enumerate(row['frames']):
            block = row['long_block'] if row['modes'][p] else row['short_block']
            available = (previous+block)//4 if p else 0
            event('PACKET', row=i, packet=p, block=block, channels=2, floor0=floor0, floor1=2-floor0,
                  bits=1, eop=0, available=available, discard_start=0, discard_end=available-frames,
                  frames=frames, position=1, end=row['granules'][p], samples=frames*2, core=core)
            pcm = references[row['id']][at:at+frames*4]
            words = [x[0] for x in struct.iter_unpack('<H', pcm)]
            for start in range(0, len(words), 128):
                chunk, runs, j = words[start:start+128], [], 0
                while j < len(chunk):
                    stop = j+1
                    while stop < len(chunk) and chunk[stop] == chunk[j]: stop += 1
                    runs.append(f'{chunk[j]:04x}:{stop-j}'); j = stop
                event('PCM', row=i, packet=p, start=start, count=len(chunk), core=core, runs=','.join(runs))
            at += frames*4; previous = block
        event('END', row=i, status=0, packets=14, frames=sum(row['frames']), samples=sum(row['frames'])*2,
              floor0=floor0*14, floor1=(2-floor0)*14, allocations=1, releases=1, live_allocations=0,
              live_bytes=0, peak_allocations=1, peak_bytes=1, stack_free=1, heap_free=1, heap_min=1, core=core)
    event('COMPLETE', cases=31, packets=434, frames=184640, samples=369280, core=core)
    event('STOP', status='CAPTURED')
    valid = '\n'.join(lines)+'\n'
    validate_log(valid, model, references, target)
    malformed = [valid.replace(f'worker={core}', f'worker={1-core}', 1), valid.rsplit('SYN_STOP', 1)[0],
                 valid+'SYN_STOP status=CAPTURED\n', valid.replace('SYN_CASE ', 'prefix SYN_CASE ', 1),
                 valid.replace('count=128 ', 'count=127 ', 1), valid.replace('runs=', 'runs=0000:129,', 1),
                 valid.replace('live_bytes=0', 'live_bytes=1', 1), valid+'watchdog\n',
                 valid.replace('SYN_PACKET ', 'SYN_ERROR ', 1)]
    first_pcm = next(line for line in lines if line.startswith('SYN_PCM '))
    match = re.search(r'runs=([0-9a-f]{4}):', first_pcm)
    altered_pcm = first_pcm[:match.start(1)] + f'{int(match[1],16)^0x8000:04x}' + first_pcm[match.end(1):]
    malformed.append(valid.replace(first_pcm, altered_pcm, 1))
    first_packet = next(line for line in lines if line.startswith('SYN_PACKET '))
    malformed.append(valid.replace(first_packet, first_packet+'\n'+first_packet, 1))
    for index, text in enumerate(malformed):
        try: validate_log(text, model, references, target)
        except ValueError: continue
        raise ValueError('malformed protocol accepted: '+str(index))
    return dict(valid_full_corpus=True, malformed_refused=len(malformed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=SDK_HEAD, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--protocol-only', action='store_true')
    parser.add_argument('--qemu-timeout', type=int, default=1200)
    args = parser.parse_args()
    need(sys.platform == 'win32' and 1 <= args.qemu_timeout <= 1200, 'pinned native Windows launcher')
    out = args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out != ROOT/'.build' and not out.exists(), 'fresh local campaign')
    out.mkdir(parents=True)
    report = dict(completed=False, passed=False, target=args.target, commands=[], inputs={}, tools={},
                  target_executed=False, production_firmware=False, physical_device=False,
                  Xiph_decoder_executed=False, deferred_scopes_resumed=False, numerical_qualified=False)
    def save():
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    def freeze(path, relative):
        target = out/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(Path(path).read_bytes())
        report['inputs'][str(Path(path).resolve())] = dict(snapshot=target.relative_to(out).as_posix(), sha256=file_sha(target))
        return target
    private_executables = set()
    def run(name, argv, timeout=60):
        argv = list(map(str, argv))
        row = dict(name=name, argv=[('runtime-path-redacted:'+Path(v).name) if v in private_executables else v for v in argv],
                   state='starting', timeout_seconds=timeout)
        report['commands'].append(row); save()
        child = None; started = time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as stdout, (out/(name+'.stderr.log')).open('xb') as stderr:
                child = subprocess.Popen(argv, cwd=out, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                if name == 'qemu': report['target_executed'] = True
                row.update(state='running', pid=child.pid); save()
                child.wait(timeout=timeout)
                row.update(state='complete', exit_status=child.returncode)
        except BaseException as error:
            row.update(state='failed', error_type=type(error).__name__)
            raise RuntimeError('owned native command failed: '+name) from None
        finally:
            if child is not None and child.poll() is None:
                stopped = subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                                         timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='forced_stop_nonpass', tree_stop_returncode=stopped.returncode)
                if child.poll() is None: child.kill()
                child.wait(timeout=15)
            row['elapsed_seconds'] = time.monotonic()-started
            for stream in ('stdout', 'stderr'):
                path = out/(name+'.'+stream+'.log')
                row[stream+'_sha256'] = file_sha(path) if path.exists() else None
            if child is not None: row['exit_status'] = child.poll()
            save()
        need(row['state'] == 'complete' and row['exit_status'] == 0, 'native command terminal0: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8', errors='replace').replace('\r\n', '\n')
    save()
    try:
        original, model, references = original_inputs()
        (out/'original31.json').write_bytes(original)
        (out/'cases.h').write_bytes(header(model))
        (out/'reference').mkdir()
        for row in model['cases']:
            (out/'reference'/Path(row['reference_path']).name).write_bytes(references[row['id']])
        report['protocol_controls'] = protocol_controls(model, references, args.target)
        report.update(original_sha256=ORIGINAL_SHA, original_archive_sha256=ORIGINAL_ARCHIVE_SHA,
                      reference_archive_sha256=REFERENCE_ARCHIVE_SHA, cases=31, packets=434,
                      pcm_bytes=738560, original_relations=14, max_abs_error_bound=2)
        if args.protocol_only:
            report.update(completed=True, protocol_only=True); save()
            print(json.dumps(report['protocol_controls'])); return 0
        freeze(Path(__file__), Path('controller.py'))
        for name in COMPONENTS:
            for path in sorted((ROOT/'idf/components'/name).rglob('*')):
                if path.is_file(): freeze(path, Path('components')/name/path.relative_to(ROOT/'idf/components'/name))
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file(): freeze(path, Path('project')/path.relative_to(PROJECT))
        for suffix in ('c', 'h'):
            freeze(ROOT/('tests/native/vorbis_synthesis_pipeline.'+suffix), Path('helper')/('vorbis_synthesis_pipeline.'+suffix))
        shutil.copytree(out/'sources/project', out/'project')
        shutil.copyfile(out/'cases.h', out/'project/main/cases.h')
        for path in (out/'sources/helper').iterdir(): shutil.copyfile(path, out/'project/main'/path.name)
        shutil.copyfile(out/'project'/('sdkconfig.'+args.target+'.defaults'), out/'project/sdkconfig.defaults')
        report.update(prepared=True, cases_header_sha256=file_sha(out/'cases.h')); save()
        if args.prepare_only:
            print(json.dumps(dict(prepared=True, cases=31, packets=434))); return 0
        if args.target == 'esp32':
            sdk = REPO/'.idf/v6.0.2'; tools = REPO/'.idf/tools-v6.0.2'
            py = tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
            qemu = ROOT/'.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
        else:
            sdk = REPO/'.idf/v6.1-9a97f6c54ec6'; tools = REPO/'.idf/tools-v6.1'
            py = tools/'python_env/idf6.1_py3.12_env/Scripts/python.exe'
            qemu = Path('C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe')
        ps = Path(shutil.which('pwsh.exe') or '')
        git = Path(shutil.which('git.exe') or shutil.which('git') or '')
        rom = Path('C:/Work/QEMU-ESP32/pc-bios')
        for alias, path in (('powershell', ps), ('python', py), ('qemu', qemu), ('git', git)):
            need(path.is_file(), 'installed native tool: '+alias)
            private = bool(re.search(r'(?i)[/\\]Users[/\\]', str(path)))
            if private: private_executables.add(str(path))
            report['tools'][alias] = dict(sha256=file_sha(path), path='runtime-path-redacted' if private else str(path),
                                         personal_path_redacted=private)
        need(file_sha(qemu) == QEMU_SHA[args.target], 'pinned target QEMU executable')
        report['roms'] = {p.name: file_sha(p) for p in sorted(rom.glob(args.target+'*rom*.bin'))}
        need(report['roms'], 'explicit target ROM')
        need(run('sdk-head', [git, '-c', 'core.longpaths=true', '-C', sdk, 'rev-parse', 'HEAD']).strip() == SDK_HEAD[args.target],
             'pinned SDK revision')
        need(not run('sdk-clean', [git, '-c', 'core.longpaths=true', '-C', sdk, 'status', '--porcelain', '--untracked-files=no']).strip(),
             'clean SDK')
        report['sdk_revision'] = SDK_HEAD[args.target]
        run('build', [ps, '-NoProfile', '-NonInteractive', '-File', out/'sources/project/sdk-build.ps1', '-Campaign', out,
            '-SdkDirectory', sdk, '-ToolsDirectory', tools, '-PythonExecutable', py, '-Target', args.target,
            '-CasesSha256', ORIGINAL_SHA, '-CasesHeaderSha256', file_sha(out/'cases.h')], 1200)
        child = json.loads((out/'sdk-child.json').read_text('utf-8-sig'))
        need(child['exit_status'] == 0 and child['pid'] > 0, 'actual SDK child terminal')
        report['sdk_child'] = child
        build = out/'build'; description = json.loads((build/'project_description.json').read_bytes())
        elf = build/description['app_elf']; elf_body = elf.read_bytes()
        need(elf.resolve().is_relative_to(build) and elf_body[:6] == b'\x7fELF\x01\x01' and
             int.from_bytes(elf_body[18:20], 'little') == (94 if args.target == 'esp32' else 243), 'native ELF32 machine')
        compiler = Path(description['c_compiler']); nm = compiler.with_name(compiler.name.replace('gcc', 'nm'))
        report['tools']['compiler'] = dict(path=str(compiler), sha256=file_sha(compiler))
        report['tools']['nm'] = dict(path=str(nm), sha256=file_sha(nm))
        database = json.loads((build/'compile_commands.json').read_bytes())
        selected = [row for row in database if Path(row['file']).resolve().is_relative_to(out/'sources/components') or
                    Path(row['file']).resolve().is_relative_to(out/'project/main')]
        need(len(selected) >= 20, 'all public pipeline compile units')
        need(all(all(flag in row['command'] for flag in ('-fstack-usage', '-fno-fast-math', '-ffp-contract=off'))
                 for row in selected), 'actual numeric compiler flags')
        report['compile_rows'] = selected
        symbols = run('symbols', [nm, '-n', '-S', elf])
        for symbol in ('vorbis_synthesis_pipeline_run', 'native_vorbis_setup_owner_replace', 'native_vorbis_frame_decode',
                       'native_vorbis_frame_floor0_prepare', 'native_vorbis_imdct_transform_binary64', 'native_vorbis_synthesis_push',
                       'native_vorbis_pcm_s16_product_pair'):
            need(re.search(r'\b'+symbol+r'$', symbols, re.M), 'linked exercised symbol: '+symbol)
        need(not re.search(r'\b(?:vorbis_synthesis|esp_vorbis_dec_open)$', symbols, re.M), 'owned public decoder only')
        usage = []
        for row in selected:
            path = build/Path(row['output']).with_suffix('.su')
            need(path.is_file(), 'actual stack record'); usage.append(path)
        report['stack_records'] = {p.relative_to(out).as_posix(): p.read_text('utf-8').splitlines() for p in usage}
        recipe = json.loads((build/'flasher_args.json').read_bytes())
        need(recipe['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'), 'isolated DIO profile')
        flashes = {int(offset, 0): (build/name).resolve() for offset, name in recipe['flash_files'].items()}
        need(set(flashes) == ({4096, 32768, 65536} if args.target == 'esp32' else {0, 32768, 65536}) and
             all(path.is_relative_to(build) for path in flashes.values()), 'bounded image recipe')
        flash = out/'qemu-flash.bin'
        argv = [py, '-m', 'esptool', '--chip', args.target, 'merge-bin', '--output', flash,
                '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(flashes.items()): argv += [hex(offset), path]
        run('merge', argv+['--pad-to-size', '4MB'])
        config = (out/'sdkconfig').read_text()
        need(bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (args.target == 'esp32c3'), 'native core profile')
        for setting in ('CONFIG_ESP_TASK_WDT_EN=y', 'CONFIG_ESP_TASK_WDT_INIT=y', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=y'):
            need(setting in config, 'watchdog and idle0 remain enabled')
        if args.target == 'esp32': need('CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y' in config, 'idle1 remains enabled')
        qargs = [qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet'] if args.target == 'esp32' else [qemu, '-M', 'esp32c3']
        qargs += ['-smp', '2' if args.target == 'esp32' else '1', '-L', rom, '-display', 'none', '-monitor', 'none',
                  '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none', '-drive', 'file='+str(flash)+',if=mtd,format=raw']
        report['target_launch_attempted'] = True; save()
        log = run('qemu', qargs, args.qemu_timeout)
        (out/'pcm').mkdir()
        measured = validate_log(log+'\n'+(out/'qemu.stderr.log').read_text('utf-8', errors='replace'),
                                model, references, args.target, out/'pcm')
        (out/'measurement.json').write_text(json.dumps(measured, indent=2)+'\n', encoding='utf-8')
        need(all(file_sha(path) == pin['sha256'] == file_sha(out/pin['snapshot']) for path, pin in report['inputs'].items()),
             'all original and frozen source inputs unchanged')
        outputs = [elf, elf.with_suffix('.map'), flash, out/'sdkconfig', out/'sdk-child.json', *usage, *flashes.values()]
        outputs += [build/name for name in ('compile_commands.json', 'project_description.json', 'flasher_args.json',
                    'CMakeCache.txt', 'config/sdkconfig.h', 'build.ninja', 'CMakeFiles/rules.ninja')]
        outputs += [p for p in build.rglob('*.obj') if p.is_file()]
        report['build_outputs'] = {p.relative_to(out).as_posix(): file_sha(p) for p in outputs}
        report.update(completed=True, passed=True, numerical_qualified=True,
                      measurements={k: v for k, v in measured.items() if k != 'rows'},
                      measurement_sha256=file_sha(out/'measurement.json'))
        save(); print(json.dumps(dict(completed=True, target=args.target, **report['measurements']))); return 0
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=str(error)); save(); raise


if __name__ == '__main__':
    raise SystemExit(main())
