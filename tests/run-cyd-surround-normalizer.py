"""Compare a shared multichannel envelope with independent public stereo owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
NORMALIZER = Path('yoRadio/src/audioI2S')
ADAPTER = Path('idf/components/native_audio_normalizer')
HARNESS = Path('tests/native/cyd_surround_normalizer.cpp')


def need(value, why):
    if not value:
        raise ValueError(why)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--baseline', action='store_true', help='Characterize the original first-two-only block API.')
    args = parser.parse_args()
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh ignored capture')
    out.mkdir(parents=True)
    report = dict(passed=False, baseline=args.baseline, production_selected=False,
                  physical_hardware=False, sources=[], commands=[])

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def execute(name, argv):
        row = dict(name=name, argv=(['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + argv, state='starting')
        report['commands'].append(row)
        start = time.monotonic()
        with (out / (name + '.stdout.log')).open('wb') as stdout, (out / (name + '.stderr.log')).open('wb') as stderr:
            process = subprocess.Popen(row['argv'], stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, shell=False)
            row.update(pid=process.pid, state='running')
            save()
            try:
                status = process.wait(timeout=180)
            except subprocess.TimeoutExpired:
                process.kill(); status = process.wait(); row['timed_out'] = True
            row.update(state='complete', exit_status=status, elapsed_seconds=round(time.monotonic() - start, 3))
        for stream in ('stdout', 'stderr'):
            path = out / (name + '.' + stream + '.log')
            row[stream] = dict(path=path.name, bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
        save()
        need(status == 0 and not row.get('timed_out'), 'terminal zero: ' + name)
        return (out / (name + '.stdout.log')).read_bytes()

    save()
    try:
        paths = [Path(__file__).resolve().relative_to(ROOT), HARNESS,
                 *[NORMALIZER / name for name in ('AudioNormalizer.cpp', 'AudioNormalizer.h')],
                 *[ADAPTER / name for name in ('native_audio_normalizer.cpp', 'native_audio_normalizer.h')]]
        for path in paths:
            body = (ROOT / path).read_bytes()
            copy = out / 'sources' / path
            copy.parent.mkdir(parents=True, exist_ok=True); copy.write_bytes(body)
            report['sources'].append(dict(path=path.as_posix(), snapshot=copy.relative_to(out).as_posix(), bytes=len(body), sha256=sha(body)))
        save()
        report['compiler_version'] = execute('compiler-version', ['/usr/bin/g++', '--version']).decode().splitlines()[0]
        compiler = execute('compiler-realpath', ['/usr/bin/readlink', '-f', '/usr/bin/g++']).decode().strip()
        need(compiler.startswith('/usr/') and '\n' not in compiler, 'actual compiler path')
        report['compiler_identity'] = execute('compiler-sha256', ['/usr/bin/sha256sum', compiler]).decode().strip()
        source = out / 'sources'
        binary = out / 'surround-normalizer'
        execute('build', ['/usr/bin/g++', '-std=c++17', '-O2', '-g', '-Wall', '-Wextra', '-Werror', '-Wpedantic',
                          '-Wshadow', '-Wformat=2', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                          '-fno-pie', '-no-pie', *(['-DTEST_LEGACY_BLOCK=1'] if args.baseline else []),
                          '-I' + host(source / NORMALIZER), '-I' + host(source / ADAPTER),
                          host(source / HARNESS), host(source / NORMALIZER / 'AudioNormalizer.cpp'),
                          host(source / ADAPTER / 'native_audio_normalizer.cpp'), '-o', host(binary)])
        report['binary'] = dict(bytes=binary.stat().st_size, sha256=sha(binary.read_bytes()), local_only=True)
        body = execute('test', ['/usr/bin/env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                                'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
        result = json.loads(body)
        need(result['passed'] and result['streams'] == 128 and result['samples'] == 2359296, 'all channel/configuration/partition cases')
        if args.baseline:
            need(result['mode'] == 'legacy_characterization' and result['legacy_multichannel_gaps'] == 72 and result['differences'] > 0, 'original all-channel gap observed')
        else:
            need(result['mode'] == 'all_channels' and result['legacy_multichannel_gaps'] == result['differences'] == 0, 'exact all-channel envelope/output and original mono/stereo behavior')
        need(all(sha((ROOT / row['path']).read_bytes()) == row['sha256'] for row in report['sources']), 'all frozen sources unchanged')
        report.update(passed=True, all_source_bindings_current=True, results=result)
        save(); print(json.dumps(dict(baseline=args.baseline, **result)))
        return 0
    except Exception as error:
        report['failure'] = dict(type=type(error).__name__, reason=str(error))
        save(); print(json.dumps(dict(passed=False, failure=report['failure'])))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
