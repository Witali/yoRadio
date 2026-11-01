"""Qualify verified Ogg page ownership and raw-frame PCM clipping on the host.

No production integration or Espressif synthesis is claimed. Native commands,
source snapshots, logs and terminal statuses remain in a fresh ignored capture.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
HEADERS = Path('idf/components/native_stream/include')
HARNESS = Path('tests/native/ogg_page_input_host.c')
FIXTURES = [Path('tests/fixtures/esp32c3_calibration/opus-510.ogg'),
            Path('tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg')]
PINS = ['53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11',
        'b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679']


def sha(body):
    return hashlib.sha256(body).hexdigest()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh task-local capture required')
    out.mkdir(parents=True)
    report = dict(schema=1, passed=False, state='preparing', production_integrated=False,
                  physical_hardware=False, commands=[], sources=[])

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def command(name, argv, timeout=240):
        full = (['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + argv
        row = dict(name=name, argv=full, state='starting', exit_status=None)
        report['commands'].append(row)
        start = time.monotonic()
        with (out / (name + '.stdout.log')).open('wb') as stdout, (out / (name + '.stderr.log')).open('wb') as stderr:
            child = subprocess.Popen(full, stdout=stdout, stderr=stderr, shell=False)
            row.update(pid=child.pid, state='running')
            save()
            try:
                status = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill()
                status = child.wait()
                row['timed_out'] = True
            row.update(state='complete', exit_status=status, elapsed_seconds=round(time.monotonic() - start, 3))
        for channel in ('stdout', 'stderr'):
            path = out / (name + '.' + channel + '.log')
            row[channel] = dict(path=path.name, bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
        save()
        need(status == 0 and not row.get('timed_out'), 'terminal zero required: ' + name)
        return (out / (name + '.stdout.log')).read_bytes()

    save()
    try:
        inputs = [Path(__file__).resolve().relative_to(ROOT), HARNESS,
                  Path('tests/native/ogg_opus_timeline_host.c'),
                  *[HEADERS / name for name in ('ogg_page_input.h', 'opus_pcm_trim.h', 'ogg_opus_timeline.h')],
                  *FIXTURES]
        for relative in inputs:
            body = (ROOT / relative).read_bytes()
            snapshot = out / 'sources' / relative
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(body)
            report['sources'].append(dict(path=relative.as_posix(), snapshot=snapshot.relative_to(out).as_posix(),
                                          bytes=len(body), sha256=sha(body)))
        need(all(sha((ROOT / path).read_bytes()) == pin for path, pin in zip(FIXTURES, PINS)), 'complete fixture identities')
        save()
        report['compiler_version'] = command('compiler-version', ['/usr/bin/gcc', '--version']).decode().splitlines()[0]
        compiler = command('compiler-path', ['readlink', '-f', '/usr/bin/gcc']).decode().strip()
        need(compiler.startswith('/usr/') and '\n' not in compiler, 'resolved system compiler')
        report['compiler_identity'] = command('compiler-sha256', ['sha256sum', compiler]).decode().strip()
        library = command('libopus-path', ['/usr/bin/gcc', '-print-file-name=libopus.so.0']).decode().strip()
        need(library.startswith('/usr/') and '\n' not in library, 'resolved installed reference library')
        report['libopus_identity'] = command('libopus-sha256', ['sha256sum', library]).decode().strip()
        binary = out / 'ogg-page-input-host'
        command('build', ['/usr/bin/gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                          '-Wpedantic', '-Wshadow', '-Wformat=2', '-Wstrict-prototypes',
                          '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                          '-I' + host(out / 'sources' / HEADERS), host(out / 'sources' / HARNESS),
                          '-l:libopus.so.0', '-o', host(binary)])
        report['binary'] = dict(path=binary.name, bytes=binary.stat().st_size,
                                sha256=sha(binary.read_bytes()), local_only=True)
        report['state'] = 'running'
        stdout = command('test', ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                                  'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', host(binary),
                                  *[host(out / 'sources' / path) for path in FIXTURES]])
        rows = [json.loads(line) for line in stdout.decode().splitlines()]
        need(len(rows) == 15 and all(row.get('passed') is True for row in rows), 'complete original and new test records')
        summary = rows[-1]
        need(summary['suite'] == 'ogg-page-input-host' and summary['page_cases'] > 200 and
             summary['trim_cases'] >= 200 and summary['allocation_refusals'] > 0 and
             summary['max_page_bytes'] == 65307 and summary['production_integrated'] is False,
             'required page/trim/ownership/allocation coverage')
        need(command('libopus-post-sha256', ['sha256sum', library]).decode().strip() == report['libopus_identity'],
             'reference library unchanged')
        for row in report['sources']:
            need(sha((ROOT / row['path']).read_bytes()) == row['sha256'] and
                 sha((out / row['snapshot']).read_bytes()) == row['sha256'], 'source unchanged during run')
        report.update(passed=True, state='complete', all_source_bindings_unchanged=True, test_records=rows)
        save()
        print(json.dumps(dict(capture=out.relative_to(ROOT).as_posix(), **summary)))
        return 0
    except Exception as error:
        report.update(state='nonpass', failure=dict(type=type(error).__name__, reason=str(error)))
        save()
        print(json.dumps(dict(passed=False, capture=out.relative_to(ROOT).as_posix(), failure=report['failure'])))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
