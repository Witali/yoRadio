"""Qualify wide family1 speaker matrices without selecting a production caller."""
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
HEADER = Path('idf/components/native_stream/include/pcm_speaker_mix.h')
HARNESS = Path('tests/native/pcm_speaker_mix_host.c')


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def reference(channels, precision):
    # Independent exact formula evaluation from RFC7845 figures4-9.
    with localcontext() as context:
        context.prec = precision
        a = Decimal(1) / Decimal(2).sqrt()
        b = Decimal(3).sqrt() / 2
        z, one, half = Decimal(0), Decimal(1), Decimal('0.5')
        if channels == 1:
            return [one], [one]
        if channels == 2:
            return [one, z], [z, one]
        if channels == 3:
            l, r = [one, a, z], [z, a, one]
            factor = one / (one + a)
        elif channels == 4:
            l, r = [one, z, b, half], [z, one, half, b]
            factor = one / (one + b + half)
        elif channels == 5:
            l, r = [one, a, z, b, half], [z, a, one, half, b]
            factor = 2 / (one + a + b + half)
        elif channels == 6:
            l, r = [one, a, z, b, half, a], [z, a, one, half, b, a]
            factor = 2 / (one + 2 * a + b + half)
        elif channels == 7:
            l, r = [one, a, z, b, half, a * b, a], [z, a, one, half, b, a * b, a]
            factor = 2 / (one + 2 * a + b + half + a * b)
        else:
            need(channels == 8, 'declared family1 channel range')
            l, r = [one, a, z, b, half, b, half, a], [z, a, one, half, b, half, b, a]
            factor = 2 / (2 + 2 * a + 2 * b)
        return [v * factor for v in l], [v * factor for v in r]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh ignored output directory')
    out.mkdir(parents=True)
    report = dict(passed=False, production_selected=False, hardware_executed=False,
                  source=[], commands=[], decimal_precisions=[100, 160])

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def execute(name, argv):
        full = (['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + argv
        row = dict(name=name, argv=full, state='starting')
        report['commands'].append(row)
        start = time.monotonic()
        with (out / (name + '.stdout.log')).open('wb') as stdout, (out / (name + '.stderr.log')).open('wb') as stderr:
            process = subprocess.Popen(full, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, shell=False)
            row.update(pid=process.pid, state='running')
            save()
            try:
                status = process.wait(timeout=120)
            except subprocess.TimeoutExpired:
                process.kill()
                status = process.wait()
                row['timed_out'] = True
            row.update(state='complete', exit_status=status, elapsed_seconds=round(time.monotonic() - start, 3))
        for stream in ('stdout', 'stderr'):
            path = out / (name + '.' + stream + '.log')
            row[stream] = dict(path=path.name, bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
        save()
        need(status == 0 and not row.get('timed_out'), 'terminal zero: ' + name)
        return (out / (name + '.stdout.log')).read_bytes()

    save()
    try:
        for path in (Path(__file__).resolve().relative_to(ROOT), HEADER, HARNESS):
            body = (ROOT / path).read_bytes()
            target = out / 'sources' / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
            report['source'].append(dict(path=path.as_posix(), snapshot=target.relative_to(out).as_posix(), bytes=len(body), sha256=sha(body)))
        save()
        report['compiler'] = execute('compiler-version', ['/usr/bin/gcc', '--version']).decode().splitlines()[0]
        compiler = execute('compiler-realpath', ['/usr/bin/readlink', '-f', '/usr/bin/gcc']).decode().strip()
        need(compiler.startswith('/usr/') and '\n' not in compiler, 'actual compiler path')
        report['compiler_identity'] = execute('compiler-sha256', ['/usr/bin/sha256sum', compiler]).decode().strip()
        binary = out / 'pcm-speaker-mix-host'
        execute('build', ['/usr/bin/gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-Wpedantic',
                          '-Wshadow', '-Wformat=2', '-Wstrict-prototypes', '-fsanitize=address,undefined',
                          '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                          '-I' + host(out / 'sources' / HEADER.parent), host(out / 'sources' / HARNESS), '-lm', '-o', host(binary)])
        report['binary'] = dict(bytes=binary.stat().st_size, sha256=sha(binary.read_bytes()), local_only=True)
        raw = execute('test', ['/usr/bin/env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                               'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
        rows = [json.loads(line) for line in raw.splitlines()]
        need(rows[-1] == dict(passed=True, impulses=36, controls=104, production_selected=False), 'complete native assertions')
        coefficients = [row for row in rows[:-1] if 'index' in row]
        need([(row['channels'], row['index']) for row in coefficients] == [(c, i) for c in range(1, 9) for i in range(c)], 'all family1 speaker positions')
        for row in coefficients:
            pairs = [reference(row['channels'], precision) for precision in (100, 160)]
            expected = [[float(side[row['index']]) for side in pair] for pair in pairs]
            need(expected[0] == expected[1], 'independent precision-stable binary64 coefficients')
            left, right = expected[0]
            need(float.fromhex(row['left']) == left and float.fromhex(row['right']) == right, 'exact nearest binary64 formula coefficients')
            need(float.fromhex(row['impulse']) == 32767 * (0.5 * left + 0.5 * right), 'actual unrounded linear mono impulse')
        headroom = [row for row in rows[:-1] if 'wide' in row]
        need([row['channels'] for row in headroom] == list(range(1, 9)) and
             all(row['headroom_preserved'] and float.fromhex(row['wide']) > 32767 for row in headroom), 'no intermediate S16 clipping')
        need(all(sha((ROOT / row['path']).read_bytes()) == row['sha256'] for row in report['source']), 'frozen source unchanged')
        report.update(passed=True, all_sources_current=True, exact_coefficients=72,
                      native_summary=rows[-1], headroom=headroom, coefficients=coefficients,
                      final_s16_rounding_qualified=False, enabled_normalizer_qualified=False)
        save()
        print(json.dumps(dict(passed=True, exact_coefficients=72, channel_impulses=36, controls=104,
                              production_selected=False, final_s16_rounding_qualified=False)))
        return 0
    except Exception as error:
        report['failure'] = dict(type=type(error).__name__, reason=str(error))
        save()
        print(json.dumps(dict(passed=False, failure=report['failure'])))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
