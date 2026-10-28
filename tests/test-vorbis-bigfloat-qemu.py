"""Actual frozen public bigfloat fixture on pinned ESP32/C3 SDK and QEMU."""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
PROJECT = ROOT / 'tests/target/vorbis_bigfloat_qemu'
HOST_READER_SHA = 'ea384976d4556ae95604b27a0072a732ae53e9558558f868730b3826bf12d7d7'
FIXTURE_SHA = 'a07ae74869e64a4a008a5dd420bec305479fde6b8e420b721b6f973320809c79'
REFERENCE_CONTROLLER_SHA = '4f658393b24aa250a669f17732f12cc159db8d38c0102fe81b33fcda695a4ae9'
HOST_ARCHIVE_SHA = 'f15f8ccdac3fed71bb5a51b037698c8e2bf083e7adaf64a54c6c02cf849d8f90'
HOST_MANIFEST_SHA = 'f9c9969b58f54e6c617b092f2bedd52c78d34ee307eeac5e47560071ea0ed1a7'
HOST32_SHA = 'b2fed430a10930dd928a440615ad2dc44018ae3de95a3a353d62d51fe65177c9'
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
QEMU_SHA = {'esp32': '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d',
            'esp32c3': 'a74f3324430b306618aa88a52649dbb93c32eac6d0b87926d335754346abbf0b'}


def need(ok, reason):
    if not ok: raise ValueError(reason)


def sha(body): return hashlib.sha256(body).hexdigest()
def file_sha(path): return sha(Path(path).read_bytes())


def readers():
    path = ROOT / 'tests/test-vorbis-bigfloat.py'
    need(file_sha(path) == HOST_READER_SHA and file_sha(ROOT / 'tests/native/vorbis_bigfloat_host.c') == FIXTURE_SHA,
         'frozen independent Fraction reader and original C fixture')
    spec = importlib.util.spec_from_file_location('native_bigfloat_fraction_live', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def original_inputs(host):
    folder = ROOT / 'tests/results/vorbis-bigfloat-20261028'
    body, mb = (folder / 'captures.zip').read_bytes(), (folder / 'manifest.json').read_bytes()
    need(sha(body) == HOST_ARCHIVE_SHA and sha(mb) == HOST_MANIFEST_SHA, 'sealed full host arithmetic checkpoint')
    manifest = json.loads(mb); pins = {row['path']: row for row in manifest['files']}
    physical = {}
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        need(len(archive.infolist()) == len(pins) == 147 and set(archive.namelist()) == set(pins), 'complete physical host archive')
        for info in archive.infolist():
            name = info.filename; p = PurePosixPath(name)
            need(p.as_posix() == name and not p.is_absolute() and '..' not in p.parts and '\\' not in name and ':' not in name,
                 'canonical saved host member')
            content = archive.read(info)
            need(len(content) == pins[name]['bytes'] and sha(content) == pins[name]['sha256'], 'every saved host physical byte')
            physical[name] = content
    aliases = {row['path']: row for row in manifest['logical_files']}
    need(len(aliases) == len(manifest['logical_files']) == 274, 'complete logical host archive')
    def take(name):
        row = aliases['host05/' + name]; content = physical[row['blob']]
        need(sha(content) == row['sha256'] and len(content) == row['bytes'], 'actual saved host05 bytes')
        return content
    case_bytes, input_bytes, capture, report_bytes = (take(name) for name in
        ('cases.json', 'input.txt', 'execute-limb32.stdout.log', 'report.json'))
    rows, report = json.loads(case_bytes), json.loads(report_bytes)
    need(rows == json.loads(json.dumps(host.corpus(8192))) and len(rows) == 701 and host.encode(rows) == input_bytes,
         'unchanged complete701 corpus and exact input bytes')
    need(report['passed'] and report['completed'] and report['case_count'] == 701 and
         sha(capture) == HOST32_SHA, 'qualified actual host32 capture')
    measured = host.compare(capture, rows, 32)
    need(measured == report['measurements']['limb32'], 'every saved host32 term agrees with Fraction/isqrt')
    return rows, input_bytes, case_bytes, capture, report_bytes


def header(input_bytes):
    lines = ['#pragma once', '#define BFQ_CASES 701U', '#define BFQ_INPUT_SHA256 "' + sha(input_bytes) + '"',
             '#define BFQ_FIXTURE_SHA256 "' + FIXTURE_SHA + '"', 'static const unsigned char bfq_input[]={']
    lines += [','.join(map(str, input_bytes[start:start + 32])) + ',' for start in range(0, len(input_bytes), 32)]
    return ('\n'.join(lines + ['};', ''])).encode('ascii')


def validate_log(log, rows, host, host32, target, output=None):
    """Pure when output=None: compare every original and recovery mathematical term."""
    need(target in SDK_HEAD, 'explicit native arithmetic target')
    log = log.replace('\r\n', '\n')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog|stack overflow|timed out', log, re.I),
         'native panic/watchdog/corruption/timeout')
    need(not any(re.search(r'BF(?:Q_|BEGIN |ROW |OOM |GUARD |END )', line) and not line.startswith('BF')
                 for line in log.splitlines()), 'no foreign/torn BF record')
    events = [line for line in log.splitlines() if line.startswith('BF')]
    core = 1 if target == 'esp32' else 0
    def metadata(line, tag, fixed, extra=()):
        parts = line.split(' ')
        need(parts[0] == tag and all(x.count('=') == 1 for x in parts[1:]), 'strict native metadata syntax')
        record = dict(x.split('=') for x in parts[1:])
        need(len(record) == len(parts) - 1 and set(record) == set(fixed) | set(extra) and
             all(record[key] == str(value) for key, value in fixed.items()), 'exact native metadata fields: ' + tag)
        return record
    need(len(events) >= 5, 'complete native arithmetic protocol')
    metadata(events[0], 'BFQ_BEGIN', dict(target=target, cases=701, data=sha(host.encode(rows)),
        fixture=FIXTURE_SHA, coordinator=0, worker=core))
    fixed = dict(status=0, core=core, priority=3, stack=16384, idle0=0,
                 idle1=0 if target == 'esp32' else -1, heap_integrity=1)
    extra = ('flushes', 'stack_free', 'heap_free', 'heap_min', 'largest')
    initial = metadata(events[1], 'BFQ_WORKER', fixed, extra)
    terminal = metadata(events[-2], 'BFQ_COMPLETE', fixed, extra)
    metadata(events[-1], 'BFQ_STOP', dict(status='CAPTURED'))
    for record in (initial, terminal):
        for key in extra:
            need(re.fullmatch(r'0|[1-9][0-9]*', record[key]), 'canonical native resource field')
            record[key] = int(record[key])
        need(0 < record['stack_free'] <= 16384 and 0 < record['heap_min'] <= record['heap_free'] and
             0 < record['largest'] <= record['heap_free'], 'observed actual stack/heap bounds')
    capture = ('\n'.join(events[2:-2]) + '\n').encode('ascii')
    measured = host.compare(capture, rows, 32)
    need(initial['flushes'] == 0 and terminal['flushes'] == 1 + 701 + measured['allocation_refusals'],
         'yield exactly after every original completed flush record')
    reference = {int(line.split()[1]): line.split()[2:8] for line in host32.decode('ascii').splitlines() if line.startswith('BFROW ')}
    primary = recovered = 0
    for line in capture.decode('ascii').splitlines():
        p = line.split(' ')
        if p[0] == 'BFROW':
            need(p[2:8] == reference[int(p[1])], 'actual native primary status/dyadic/floor equals actual host32')
            primary += 1
        elif p[0] == 'BFOOM':
            need(p[9:14] == reference[int(p[1])][1:], 'every actual native recovery equals actual host32 dyadic/floor')
            recovered += 1
    need(primary == 701 and recovered == measured['allocation_refusals'], 'all native primary and OOM-recovery terms compared')
    if output is not None:
        Path(output).write_bytes(capture)
    return dict(passed=True, cases=701, capture_sha256=sha(capture), capture_bytes=len(capture),
        primary_host32_equal=primary, recovery_host32_equal=recovered, actual_native_allocations=True,
        initial=initial, terminal=terminal, measurements=measured,
        scope='retained native basic arithmetic; no transcendental gain or universal MCU-fit certificate')


def protocol_controls(rows, host, host32, target):
    """Synthetic parser controls only; never labelled actual native execution."""
    core = 1 if target == 'esp32' else 0
    count = host.compare(host32, rows, 32)['allocation_refusals']
    common = f'status=0 core={core} priority=3 stack=16384'
    resources = f'stack_free=15000 heap_free=200000 heap_min=190000 largest=180000 idle0=0 idle1={0 if core else -1} heap_integrity=1'
    valid = (f'BFQ_BEGIN target={target} cases=701 data={sha(host.encode(rows))} fixture={FIXTURE_SHA} coordinator=0 worker={core}\n'
             f'BFQ_WORKER {common} flushes=0 {resources}\n' + host32.decode('ascii') +
             f'BFQ_COMPLETE {common} flushes={702 + count} {resources}\nBFQ_STOP status=CAPTURED\n')
    validate_log(valid, rows, host, host32, target)
    changed = [valid.replace(f'worker={core}', f'worker={1-core}', 1),
        valid.replace('priority=3', 'priority=4', 1), valid.rsplit('BFQ_STOP', 1)[0],
        valid + 'BFQ_STOP status=CAPTURED\n', valid.replace('BFROW ', 'prefix BFROW ', 1),
        valid.replace(f'flushes={702 + count}', f'flushes={703 + count}', 1),
        valid.replace('idle0=0', 'idle0=1', 1), valid.replace('data=' + sha(host.encode(rows)), 'data=' + '0' * 64, 1),
        valid + 'watchdog\n', valid.replace('heap_integrity=1', 'heap_integrity=0', 1)]
    for index, candidate in enumerate(changed):
        need(candidate != valid, 'actual parser-control mutation')
        try: validate_log(candidate, rows, host, host32, target)
        except ValueError: continue
        raise ValueError('malformed native arithmetic protocol accepted: ' + str(index))
    return dict(valid_full_corpus=True, malformed_refused=10, synthetic_protocol_only=True,
                native_arithmetic_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=SDK_HEAD, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--protocol-only', action='store_true')
    parser.add_argument('--qemu-timeout', type=int, default=1200)
    args = parser.parse_args()
    need(sys.platform == 'win32' and 1 <= args.qemu_timeout <= 1200, 'pinned Windows launcher and bounded native run')
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and out != ROOT / '.build' and not out.exists(), 'fresh native campaign')
    out.mkdir(parents=True)
    report = dict(completed=False, passed=False, target=args.target, commands=[], inputs={}, tools={},
        target_executed=False, production_firmware=False, physical_device=False, numerical_qualified=False,
        source_only=False, private_codec_executed=False, deferred_scopes_resumed=False,
        transcendental_gain_certified=False, production_selected=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    def freeze(path, relative):
        path = Path(path); target = out / 'sources' / relative
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(path.read_bytes())
        report['inputs'][str(path.resolve())] = dict(snapshot=target.relative_to(out).as_posix(),
            sha256=file_sha(target), bytes=target.stat().st_size)
        return target
    private_executables = set()
    def run(name, argv, timeout=60):
        argv = list(map(str, argv))
        row = dict(name=name, argv=[('runtime-path-redacted:' + Path(v).name) if v in private_executables else v for v in argv],
            state='starting', timeout_seconds=timeout)
        report['commands'].append(row); save(); child = None; started = time.monotonic()
        try:
            with (out / (name + '.stdout.log')).open('xb') as so, (out / (name + '.stderr.log')).open('xb') as se:
                child = subprocess.Popen(argv, cwd=out, stdin=subprocess.DEVNULL, stdout=so, stderr=se,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                if name == 'qemu': report['target_executed'] = True
                row.update(state='running', pid=child.pid); save(); child.wait(timeout=timeout)
                row.update(state='complete', exit_status=child.returncode)
        except BaseException as error:
            row.update(state='failed', error_type=type(error).__name__, winerror=getattr(error, 'winerror', None))
            raise RuntimeError('owned arithmetic native command failed: ' + name) from None
        finally:
            if child is not None and child.poll() is None:
                stopped = subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                    timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='forced_stop_nonpass', tree_stop_returncode=stopped.returncode)
                if child.poll() is None: child.kill()
                child.wait(timeout=15)
            row['elapsed_seconds'] = time.monotonic() - started
            for stream in ('stdout', 'stderr'):
                path = out / (name + '.' + stream + '.log')
                row[stream + '_sha256'] = file_sha(path) if path.exists() else None
            if child is not None: row['exit_status'] = child.poll()
            save()
        need(row['state'] == 'complete' and row['exit_status'] == 0, 'native command terminal0: ' + name)
        return (out / (name + '.stdout.log')).read_text('utf-8', errors='replace').replace('\r\n', '\n')
    save()
    try:
        host = readers(); rows, data, cases, host32, host_report = original_inputs(host)
        for name, body in [('input.txt', data), ('cases.json', cases), ('host32-reference.txt', host32),
                           ('host-report.json', host_report), ('corpus.h', header(data))]:
            (out / name).write_bytes(body)
        report.update(case_count=701, input_sha256=sha(data), cases_sha256=sha(cases), fixture_sha256=FIXTURE_SHA,
            Fraction_reader_sha256=HOST_READER_SHA, host_archive_sha256=HOST_ARCHIVE_SHA,
            host_manifest_sha256=HOST_MANIFEST_SHA, host32_capture_sha256=HOST32_SHA,
            host_report_sha256=sha(host_report), corpus_header_sha256=file_sha(out / 'corpus.h'),
            runtime_profile=dict(coordinator_core=0, worker_core=1 if args.target == 'esp32' else 0,
                worker_priority=3, worker_stack_bytes=16384, watchdog_enabled=True, idle_watchdog_enabled=True,
                record_yield_policy='real fflush then one tick, only existing completed-record calls'))
        report['protocol_controls'] = protocol_controls(rows, host, host32, args.target)
        freeze(Path(__file__), Path('controller.py'))
        reference = ROOT / 'tests/test-vorbis-decoder-qemu.py'
        need(file_sha(reference) == REFERENCE_CONTROLLER_SHA, 'proven frozen SDK/QEMU recipe source')
        freeze(reference, Path('design-reference/decoder-controller.py'))
        freeze(ROOT / 'tests/test-vorbis-bigfloat.py', Path('readers/test-vorbis-bigfloat.py'))
        freeze(ROOT / 'tests/native/vorbis_bigfloat_host.c', Path('native/vorbis_bigfloat_host.c'))
        for path in sorted((ROOT / 'idf/components/native_vorbis_bigfloat').rglob('*')):
            if path.is_file(): freeze(path, Path('components/native_vorbis_bigfloat') / path.relative_to(ROOT / 'idf/components/native_vorbis_bigfloat'))
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file(): freeze(path, Path('project') / path.relative_to(PROJECT))
        component = out / 'sources/components/native_vorbis_bigfloat'
        need(file_sha(component / 'bigfloat.c') == host.COMPONENT_SHA and
             file_sha(component / 'include/native_vorbis_bigfloat.h') == host.HEADER_SHA and
             file_sha(component / 'portable/libbf.c') == host.PORTABLE_SHA and
             file_sha(component / 'upstream-manifest.json') == host.MANIFEST_SHA and
             file_sha(component / 'portability.patch') == host.PATCH_SHA, 'frozen final public foundation bytes')
        shutil.copytree(out / 'sources/project', out / 'project')
        shutil.copyfile(out / 'corpus.h', out / 'project/main/corpus.h')
        shutil.copyfile(out / 'sources/native/vorbis_bigfloat_host.c', out / 'project/main/vorbis_bigfloat_host.c')
        shutil.copyfile(out / 'project' / ('sdkconfig.' + args.target + '.defaults'), out / 'project/sdkconfig.defaults')
        report['prepared'] = True; save()
        if args.protocol_only:
            report.update(completed=True, passed=True, protocol_only=True); save()
            print(json.dumps(report['protocol_controls'])); return 0
        if args.prepare_only:
            print(json.dumps(dict(prepared=True, cases=701, input_bytes=len(data)))); return 0
        if args.target == 'esp32':
            sdk, tools = REPO / '.idf/v6.0.2', REPO / '.idf/tools-v6.0.2'
            py = tools / 'python_env/idf6.0_py3.12_env/Scripts/python.exe'
            qemu = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe'
        else:
            sdk, tools = REPO / '.idf/v6.1-9a97f6c54ec6', REPO / '.idf/tools-v6.1'
            py = tools / 'python_env/idf6.1_py3.12_env/Scripts/python.exe'
            qemu = Path('C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe')
        ps, git = Path(shutil.which('pwsh.exe') or ''), Path(shutil.which('git.exe') or shutil.which('git') or '')
        rom = Path('C:/Work/QEMU-ESP32/pc-bios')
        for alias, path in [('powershell', ps), ('python', py), ('qemu', qemu), ('git', git)]:
            need(path.is_file(), 'installed actual native tool: ' + alias)
            private = bool(re.search(r'(?i)[/\\]Users[/\\]', str(path)))
            if private: private_executables.add(str(path))
            report['tools'][alias] = dict(sha256=file_sha(path), path='runtime-path-redacted' if private else str(path), personal_path_redacted=private)
        need(file_sha(qemu) == QEMU_SHA[args.target], 'pinned target QEMU executable')
        report['roms'] = {p.name: file_sha(p) for p in sorted(rom.glob(args.target + '*rom*.bin'))}
        need(report['roms'], 'explicit target ROM')
        need(run('sdk-head', [git, '-c', 'core.longpaths=true', '-C', sdk, 'rev-parse', 'HEAD']).strip() == SDK_HEAD[args.target], 'pinned SDK revision')
        need(not run('sdk-clean', [git, '-c', 'core.longpaths=true', '-C', sdk, 'status', '--porcelain', '--untracked-files=no']).strip(), 'clean installed SDK')
        report['sdk_revision'] = SDK_HEAD[args.target]
        run('build', [ps, '-NoProfile', '-NonInteractive', '-File', out / 'sources/project/sdk-build.ps1',
            '-Campaign', out, '-SdkDirectory', sdk, '-ToolsDirectory', tools, '-PythonExecutable', py,
            '-Target', args.target, '-InputSha256', sha(data), '-CorpusHeaderSha256', file_sha(out / 'corpus.h'),
            '-FixtureSha256', FIXTURE_SHA], 1200)
        child = json.loads((out / 'sdk-child.json').read_text('utf-8-sig'))
        need(child['exit_status'] == 0 and child['pid'] > 0, 'actual SDK child terminal0')
        report['sdk_child'] = child
        build = out / 'build'; description = json.loads((build / 'project_description.json').read_bytes())
        elf = build / description['app_elf']; elf_body = elf.read_bytes()
        need(elf.resolve().is_relative_to(build) and elf_body[:6] == b'\x7fELF\x01\x01' and
             int.from_bytes(elf_body[18:20], 'little') == (94 if args.target == 'esp32' else 243), 'actual native ELF32 machine')
        compiler = Path(description['c_compiler'])
        nm, size = [compiler.with_name(compiler.name.replace('gcc', tool)) for tool in ('nm', 'size')]
        for name, path in [('compiler', compiler), ('nm', nm), ('size', size)]:
            report['tools'][name] = dict(path=str(path), sha256=file_sha(path))
        database = json.loads((build / 'compile_commands.json').read_bytes())
        selected = [row for row in database if Path(row['file']).resolve().is_relative_to(out / 'sources/components') or
                    Path(row['file']).resolve().is_relative_to(out / 'project/main')]
        need(len(selected) == 4 and {Path(row['file']).name for row in selected} == {'bigfloat.c', 'libbf.c', 'cutils.c', 'main.c'}, 'all actual foundation and fixture units')
        need(all(all(flag in row['command'] for flag in ('-fstack-usage', '-fno-fast-math', '-ffp-contract=off', '-UNDEBUG')) for row in selected), 'actual checked arithmetic compiler flags')
        for row in selected:
            command = row['command']; name = Path(row['file']).name
            if name in ('libbf.c', 'cutils.c'):
                need(all(flag in command for flag in ('-Wsign-compare', '-Wunused-parameter',
                     '-Wno-error=sign-compare', '-Wno-error=unused-parameter')), 'creator diagnostics visible and narrowly nonfatal')
                need(('-Wno-error=format' in command) == (name == 'libbf.c'), 'format downgrade only for portable creator unit')
            else:
                need('-Werror' in command and '-Wno-error=format' not in command and
                     '-Wno-error=sign-compare' not in command, 'adapter/main strict warning policy unchanged')
        report['compile_rows'] = selected
        symbols = run('symbols', [nm, '-n', '-S', elf])
        required = ['native_vorbis_bigfloat_fixture_run', 'native_vorbis_bigfloat_import', 'native_vorbis_bigfloat_add',
            'native_vorbis_bigfloat_sub', 'native_vorbis_bigfloat_mul', 'native_vorbis_bigfloat_div',
            'native_vorbis_bigfloat_sqrt', 'native_vorbis_bigfloat_export_dyadic', 'native_vorbis_bigfloat_export_floor',
            'bf_mul', 'bf_div', 'bf_sqrt', 'bfq_record_flush']
        for symbol in required:
            need(re.search(r'\b' + symbol + r'(?:\.[A-Za-z0-9_.]+)?$', symbols, re.M), 'linked actual exercised symbol: ' + symbol)
        report['required_symbols'] = required
        # bf_const_free is legitimate context cleanup, even though generators
        # and transcendental entry points must be absent from this image.
        excluded = (r'\b(?:bf_(?:const_(?:pi[A-Za-z0-9_]*|log2[A-Za-z0-9_]*|get)|(?:exp|log|pow|sin|cos|tan|asin|acos|atan)[A-Za-z0-9_]*|'
                    r'[af]toa[A-Za-z0-9_]*|print_str|get_float64|set_si|add_si|mul_si)|bfdec_[A-Za-z0-9_]+|'
                    r'dump_limbs|mp_print_str[A-Za-z0-9_]*)(?:\.[A-Za-z0-9_.]+)?$')
        need(not re.search(excluded, symbols, re.M), 'excluded debug/decimal/string/transcendental helpers absent from linked image')
        linkmap = elf.with_suffix('.map').read_text(errors='replace').replace('\r\n', '\n')
        discarded = linkmap.split('Memory Configuration', 1)[0]
        need('Discarded input sections' in discarded and all('.text.' + name in discarded for name in
             ('bf_print_str', 'bfdec_print_str', 'bf_cos', 'bf_get_float64')) and
             '--gc-sections' in (build / 'build.ninja').read_text(), 'actual function-section collection and discarded excluded helpers')
        report['excluded_symbol_pattern'] = excluded
        report['section_gc_verified'] = True
        report['section_sizes'] = run('size', [size, '-A', elf])
        usage = []
        for row in selected:
            path = build / Path(row['output']).with_suffix('.su'); need(path.is_file(), 'actual native stack report'); usage.append(path)
        report['stack_records'] = {p.relative_to(out).as_posix(): p.read_text().splitlines() for p in usage}
        recipe = json.loads((build / 'flasher_args.json').read_bytes())
        need(recipe['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'), 'isolated DIO image settings')
        flashes = {int(offset, 0): (build / name).resolve() for offset, name in recipe['flash_files'].items()}
        need(set(flashes) == ({4096, 32768, 65536} if args.target == 'esp32' else {0, 32768, 65536}) and
             all(p.is_relative_to(build) for p in flashes.values()), 'bounded native image recipe')
        flash = out / 'qemu-flash.bin'
        argv = [py, '-m', 'esptool', '--chip', args.target, 'merge-bin', '--output', flash, '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(flashes.items()): argv += [hex(offset), path]
        run('merge', argv + ['--pad-to-size', '4MB'])
        config = (out / 'sdkconfig').read_text().replace('\r\n', '\n')
        need(bool(re.search(r'^CONFIG_FREERTOS_UNICORE=y$', config, re.M)) == (args.target == 'esp32c3'), 'actual target core configuration')
        for setting in ['CONFIG_ESP_TASK_WDT_EN=y', 'CONFIG_ESP_TASK_WDT_INIT=y', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=y'] + (['CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y'] if args.target == 'esp32' else []):
            need(re.search(r'^' + re.escape(setting) + r'$', config, re.M), 'watchdog/IDLE preserved: ' + setting)
        # Preserve images/objects/config even if the following actual native run
        # refuses or fails. QEMU's -snapshot does not modify these source images.
        outputs = [elf, elf.with_suffix('.map'), flash, out / 'sdkconfig', out / 'sdk-child.json', *usage, *flashes.values()]
        outputs += [build / name for name in ('compile_commands.json', 'project_description.json', 'flasher_args.json', 'CMakeCache.txt', 'config/sdkconfig.h', 'build.ninja', 'CMakeFiles/rules.ninja')]
        outputs += [p for p in build.rglob('*.obj') if p.is_file()]
        report['build_outputs'] = {p.relative_to(out).as_posix(): file_sha(p) for p in outputs}
        save()
        qargs = [qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet'] if args.target == 'esp32' else [qemu, '-M', 'esp32c3']
        qargs += ['-smp', '2' if args.target == 'esp32' else '1', '-L', rom, '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none', '-drive', 'file=' + str(flash) + ',if=mtd,format=raw']
        report['target_launch_attempted'] = True; save()
        log = run('qemu', qargs, args.qemu_timeout)
        measured = validate_log(log + '\n' + (out / 'qemu.stderr.log').read_text(errors='replace'), rows, host, host32, args.target, out / 'capture.txt')
        (out / 'measurement.json').write_text(json.dumps(measured, indent=2) + '\n', encoding='utf-8', newline='\n')
        report['corruption_controls'] = host.corruption_controls((out / 'capture.txt').read_bytes(), rows, 32)
        for path, pin in report['inputs'].items():
            need(file_sha(out / pin['snapshot']) == pin['sha256'] and
                 (path.endswith('.md') or file_sha(path) == pin['sha256']), 'frozen/live executable input immutability')
        report.update(completed=True, passed=True, numerical_qualified=True,
            measurements={k: v for k, v in measured.items() if k != 'measurements'},
            arithmetic={k: v for k, v in measured['measurements'].items() if k not in ('rows', 'refusals')},
            measurement_sha256=file_sha(out / 'measurement.json'))
        save(); print(json.dumps(dict(completed=True, target=args.target, **report['arithmetic']))); return 0
    except BaseException as error:
        report.update(error_type=type(error).__name__, error=str(error)); save(); raise


if __name__ == '__main__': raise SystemExit(main())
