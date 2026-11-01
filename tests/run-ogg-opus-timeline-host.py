"""Build and run the bounded metadata observer with host ASan/UBSan/leak checks.

This does not decode audio, run an SDK/QEMU target, or implement playback trim.
Each invocation requires a fresh ignored capture directory and preserves failed
builds/runs, frozen inputs, exact commands, terminal statuses and raw logs.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
HEADER = Path('idf/components/native_stream/include/ogg_opus_timeline.h')
HARNESS = Path('tests/native/ogg_opus_timeline_host.c')
SHORT = Path('tests/fixtures/esp32c3_calibration/opus-510.ogg')
LONG = Path('tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg')
SHORT_AUDIT = Path('tests/verify-cyd-opus-direct-checkpoint.py')
LONG_AUDIT = Path('tests/fixtures/opus_ogg_long_packets/generate.py')
EXPECTED_FIXTURES = {
    SHORT.as_posix(): '53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11',
    LONG.as_posix(): 'b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679',
}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build'), 'capture must be under this worktree .build')
    need(not out.exists(), 'capture directory already exists; preserve it and choose a fresh one')
    out.mkdir(parents=True)
    report = {
        'schema': 1, 'passed': False, 'state': 'preparing',
        'physical_hardware': False, 'decoder_executed': False,
        'playback_trim_implemented': False, 'sources': [], 'commands': [],
        'host': {'system': platform.system(), 'python': platform.python_version()},
    }
    report_path = out / 'report.json'

    def save():
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def command(name, argv, timeout=180):
        full = (['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + argv
        row = {'name': name, 'argv': full, 'state': 'starting', 'exit_status': None}
        report['commands'].append(row)
        stdout_path, stderr_path = out / (name + '.stdout.log'), out / (name + '.stderr.log')
        start = time.monotonic()
        with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
            child = subprocess.Popen(full, stdout=stdout, stderr=stderr, shell=False)
            row.update(pid=child.pid, state='running')
            save()
            try:
                status = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill()
                status = child.wait()
                row['timed_out'] = True
            row.update(state='complete', exit_status=status,
                       elapsed_seconds=round(time.monotonic() - start, 3))
        row['stdout'] = {'path': stdout_path.name, 'bytes': stdout_path.stat().st_size,
                         'sha256': sha(stdout_path.read_bytes())}
        row['stderr'] = {'path': stderr_path.name, 'bytes': stderr_path.stat().st_size,
                         'sha256': sha(stderr_path.read_bytes())}
        save()
        need(not row.get('timed_out') and status == 0, 'terminal zero required: ' + name)
        return stdout_path.read_bytes()

    save()
    try:
        inputs = [Path(__file__).resolve().relative_to(ROOT), HEADER, HARNESS,
                  SHORT, LONG, SHORT_AUDIT, LONG_AUDIT]
        for relative in inputs:
            body = (ROOT / relative).read_bytes()
            snapshot = out / 'sources' / relative
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(body)
            row = {'path': relative.as_posix(), 'snapshot': snapshot.relative_to(out).as_posix(),
                   'bytes': len(body), 'sha256': sha(body)}
            report['sources'].append(row)
            if relative.as_posix() in EXPECTED_FIXTURES:
                need(row['sha256'] == EXPECTED_FIXTURES[relative.as_posix()], 'exact real fixture binding')
        save()
        short_audit = module(out / 'sources' / SHORT_AUDIT, 'timeline_short_audit')
        long_audit = module(out / 'sources' / LONG_AUDIT, 'timeline_long_audit')
        report['fixture_audits'] = {
            '20ms': short_audit.fixture_accounting((out / 'sources' / SHORT).read_bytes()),
            '120ms': long_audit.audit((out / 'sources' / LONG).read_bytes()),
        }
        save()
        compiler_version = command('compiler-version', ['/usr/bin/gcc', '--version'])
        report['compiler_version'] = compiler_version.decode('utf-8').splitlines()[0]
        compiler = command('compiler-realpath', ['readlink', '-f', '/usr/bin/gcc']).decode().strip()
        need(compiler.startswith('/usr/') and '\n' not in compiler, 'resolved system compiler path')
        report['compiler_binary'] = command('compiler-sha256', ['sha256sum', compiler]).decode().strip()
        report['compiler_target'] = command('compiler-target', ['/usr/bin/gcc', '-dumpmachine']).decode().strip()
        library = command('libopus-path', ['/usr/bin/gcc', '-print-file-name=libopus.so.0']).decode().strip()
        need(library.startswith('/usr/') and '\n' not in library, 'resolved public reference library path')
        library = command('libopus-realpath', ['readlink', '-f', library]).decode().strip()
        report['libopus_binary'] = command('libopus-sha256', ['sha256sum', library]).decode().strip()
        binary = out / 'ogg-opus-timeline-host'
        report['state'] = 'building'
        command('build', ['/usr/bin/gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra',
                          '-Werror', '-Wpedantic', '-Wshadow', '-Wformat=2',
                          '-Wstrict-prototypes', '-fsanitize=address,undefined',
                          '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                          '-I' + host((out / 'sources' / HEADER).parent),
                          host(out / 'sources' / HARNESS), '-l:libopus.so.0', '-o', host(binary)])
        report['binary'] = {'path': binary.name, 'bytes': binary.stat().st_size,
                            'sha256': sha(binary.read_bytes()), 'local_only': True}
        report['state'] = 'running'
        stdout = command('test', ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                                  'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
                                  host(binary), host(out / 'sources' / SHORT),
                                  host(out / 'sources' / LONG)])
        rows = [json.loads(line) for line in stdout.decode('utf-8').splitlines()]
        need(len(rows) == 12 and all(row.get('passed') is True for row in rows), 'complete test records')
        need(rows[-2].get('reference') == 'libopus' and
             rows[-2]['duration_comparisons'] >= 150 and
             rows[-2]['version'].startswith('libopus '), 'independent public packet-duration reference')
        need(rows[-1].get('suite') == 'ogg-opus-timeline-host' and
             rows[-1]['fixture_runs'] == 10 and rows[-1]['state_bytes'] <= 768 and
             rows[-1]['cases'] >= 480 and rows[-1]['reset_positions'] >= 400,
             'bounded state and required test inventory')
        for name, raw, size in [('20ms', 528960, 706319), ('120ms', 529920, 707097)]:
            fixtures = [row for row in rows[:-1] if row.get('fixture') == name]
            need(len(fixtures) == 5 and {row['split'] for row in fixtures} ==
                 {'whole', '4096', '257', '1', 'seeded'}, 'all required real-fixture splits')
            need(len({row['digest'] for row in fixtures}) == 1 and all(
                row['raw_frames'] == raw and row['bytes'] == size and row['raw_end'] == 528312
                and row['pre_skip'] == 312 for row in fixtures), 'split-invariant fixture timeline')
        report['test_records'] = rows
        need(command('libopus-post-sha256', ['sha256sum', library]).decode().strip() ==
             report['libopus_binary'], 'reference library changed during execution')
        for row in report['sources']:
            need(sha((ROOT / row['path']).read_bytes()) == row['sha256'], 'canonical source changed during execution')
            need(sha((out / row['snapshot']).read_bytes()) == row['sha256'], 'frozen source changed during execution')
        report['all_source_bindings_unchanged'] = True
        report.update(passed=True, state='complete')
        save()
        print(json.dumps({'passed': True, 'capture': out.relative_to(ROOT).as_posix(), **rows[-1]}))
        return 0
    except Exception as error:
        report.update(state='nonpass', failure={'type': type(error).__name__, 'reason': str(error)})
        save()
        print(json.dumps({'passed': False, 'capture': out.relative_to(ROOT).as_posix(),
                          'failure': report['failure']}))
        return 1


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
