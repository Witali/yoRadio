"""Run real libogg differential nil-page tests with ASan/UBSan/leak checks.

Requires installed WSL GCC/libogg on Windows. The existing vendored public
libogg headers are used when distro development headers are absent. No audio
decoder, private layout or MCU firmware is involved. Fresh ignored captures
preserve every original command, source snapshot and terminal outcome.
"""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = Path('idf/components/native_stream/include/ogg_opus_timeline.h')
HARNESS = Path('tests/native/ogg_opus_nil_page_host.c')
PUBLIC = Path('idf/components/native_vorbis_xiph/upstream/libogg')
CONFIG = Path('idf/components/native_vorbis_xiph/platform')
INPUTS = [HEADER, HARNESS, PUBLIC / 'include/ogg/ogg.h',
          PUBLIC / 'include/ogg/os_types.h', CONFIG / 'ogg/config_types.h',
          PUBLIC / 'COPYING']


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh ignored capture required')
    out.mkdir(parents=True)
    report = dict(schema=1, passed=False, state='preparing', sources=[], commands=[],
                  physical_hardware=False, decoder_executed=False,
                  host=dict(system=platform.system(), python=platform.python_version()))

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def command(name, argv, allow_nonzero=False):
        full = (['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + argv
        row = dict(name=name, argv=full, state='starting', exit_status=None)
        report['commands'].append(row)
        logs = {key: out / (name + '.' + key + '.log') for key in ('stdout', 'stderr')}
        start = time.monotonic()
        with logs['stdout'].open('wb') as stdout, logs['stderr'].open('wb') as stderr:
            child = subprocess.Popen(full, stdout=stdout, stderr=stderr, shell=False)
            row.update(pid=child.pid, state='running')
            save()
            try:
                status = child.wait(timeout=120)
            except subprocess.TimeoutExpired:
                child.kill()
                status = child.wait()
                row['timed_out'] = True
            row.update(state='complete', exit_status=status,
                       elapsed_seconds=round(time.monotonic() - start, 3))
        for key, path in logs.items():
            row[key] = dict(path=path.name, bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
        save()
        need(not row.get('timed_out') and (allow_nonzero or status == 0), 'terminal zero required: ' + name)
        return logs['stdout'].read_bytes(), status

    save()
    try:
        for relative in [Path(__file__).resolve().relative_to(ROOT)] + INPUTS:
            body = (ROOT / relative).read_bytes()
            frozen = out / 'sources' / relative
            frozen.parent.mkdir(parents=True, exist_ok=True)
            frozen.write_bytes(body)
            report['sources'].append(dict(path=relative.as_posix(), snapshot=frozen.relative_to(out).as_posix(),
                                          bytes=len(body), sha256=sha(body)))
        save()
        version, _ = command('compiler-version', ['/usr/bin/gcc', '--version'])
        report['compiler_version'] = version.decode().splitlines()[0]
        compiler, _ = command('compiler-realpath', ['/usr/bin/readlink', '-f', '/usr/bin/gcc'])
        compiler = compiler.decode().strip()
        need(compiler.startswith('/usr/') and '\n' not in compiler, 'resolved compiler path')
        compiler_hash, _ = command('compiler-sha256', ['/usr/bin/sha256sum', compiler])
        report['compiler_binary'] = compiler_hash.decode().strip()
        library, _ = command('libogg-realpath', ['/usr/bin/readlink', '-f', '/lib/x86_64-linux-gnu/libogg.so.0'])
        library = library.decode().strip()
        need(library.startswith('/usr/lib/') and '\n' not in library, 'installed public libogg library')
        library_hash, _ = command('libogg-sha256', ['/usr/bin/sha256sum', library])
        report['libogg_binary'] = library_hash.decode().strip()
        library_version, _ = command('libogg-version', ['/usr/bin/dpkg-query', '-W', '-f=${Version}\n', 'libogg0:amd64'])
        report['libogg_version'] = library_version.decode().strip()
        binary = out / 'ogg-opus-nil-page-host'
        report['state'] = 'building'
        command('build', ['/usr/bin/gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                          '-Wpedantic', '-Wshadow', '-Wformat=2', '-Wstrict-prototypes',
                          '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                          '-I' + host((out / 'sources' / HEADER).parent),
                          '-I' + host(out / 'sources' / PUBLIC / 'include'),
                          '-I' + host(out / 'sources' / CONFIG),
                          host(out / 'sources' / HARNESS), library, '-o', host(binary)])
        report['binary'] = dict(path=binary.name, bytes=binary.stat().st_size,
                                sha256=sha(binary.read_bytes()), local_only=True)
        report['state'] = 'running'
        stdout, status = command('test', ['/usr/bin/env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                                         'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', host(binary)], True)
        rows = [json.loads(line) for line in stdout.decode().splitlines()]
        report['test_records'] = rows
        need(rows and rows[-1].get('suite') == 'ogg-opus-nil-page-host', 'complete actual test summary')
        need(rows[-1]['cases'] == 24 and rows[-1]['negative_cases'] == 4 and
             rows[-1]['schedules'] == 140 and len(rows) == 141, 'full differential inventory')
        post_hash, _ = command('libogg-post-sha256', ['/usr/bin/sha256sum', library])
        need(post_hash == library_hash, 'unchanged public reference library')
        for row in report['sources']:
            need(sha((ROOT / row['path']).read_bytes()) == row['sha256'] and
                 sha((out / row['snapshot']).read_bytes()) == row['sha256'], 'unchanged canonical/frozen sources')
        report['all_source_bindings_unchanged'] = True
        need(status == 0 and all(row['passed'] for row in rows), 'nil-page differential mismatch or sanitizer failure')
        report.update(passed=True, state='complete')
        save()
        print(json.dumps(dict(capture=out.relative_to(ROOT).as_posix(), **rows[-1])))
        return 0
    except Exception as error:
        report.update(passed=False, state='nonpass', failure=dict(type=type(error).__name__, reason=str(error)))
        save()
        print(json.dumps(dict(passed=False, capture=out.relative_to(ROOT).as_posix(), failure=report['failure'])))
        return 1


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())
