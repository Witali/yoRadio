"""Observe public creator aggregate versus elementary code0 decode cadence.

This new control consumes unchanged complete mode-corpus packets. Integer and
float output are measured separately; soft/hard conversion observations are
application policies, not a numeric conformance tolerance or private codec math.
"""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ['tests/native/opus_frame_control_public.c', 'tests/native/opus_packet_modes_public.h',
           'tests/run-opus-frame-control-reference.py']
SELECTED = ['m2-s120-code0', 'm2-s120-code3-cbr120', 'm2-s120-code3-cbr-pad255', 'm2-s120-code3-vbr120']


def need(value, reason):
    if not value:
        raise ValueError(reason)


def pin(path):
    data = Path(path).read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def integer_compare(a, b):
    left, right = array('h'), array('h'); left.frombytes(a); right.frombytes(b)
    need(len(left) == len(right) and left, 'equal full PCM extent')
    return dict(equal_bytes=a == b, max_absolute_lsb=max(abs(x - y) for x, y in zip(left, right)),
                unequal_samples=sum(x != y for x, y in zip(left, right)), no_tolerance_applied=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--native', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); reference = args.reference.resolve(); native = args.native.resolve()
    need(out.is_relative_to(ROOT / '.build') and not out.exists(), 'fresh local capture')
    creator = json.loads((reference / 'report.json').read_bytes()); vendor = json.loads((native / 'report.json').read_bytes())
    need(creator['passed'] and creator['completed'] and vendor['passed'] and vendor['completed'], 'unchanged completed parent captures')
    out.mkdir(parents=True)
    report = dict(passed=False, completed=False, commands=[], sources=[], cases={}, native_newly_executed=False,
                  private_abi_used=False, numeric_conformance_claim=False, numeric_tolerance_applied=False,
                  input_creator_report=dict(path=reference.relative_to(ROOT).as_posix(), **pin(reference / 'report.json')),
                  input_native_report=dict(path=native.relative_to(ROOT).as_posix(), **pin(native / 'report.json')))
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    def command(name, arguments, timeout=120):
        argv = (['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + list(map(str, arguments))
        row = dict(name=name, argv=argv, state='starting', timeout_seconds=timeout)
        report['commands'].append(row); save(); started = time.monotonic()
        with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)
            row.update(pid=child.pid, state='running'); save()
            try:
                status = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill(); status = child.wait(); row['timed_out'] = True
            row.update(state='complete', exit_status=status, elapsed_seconds=round(time.monotonic() - started, 3))
        for stream in ('stdout', 'stderr'):
            path = out / (name + '.' + stream + '.log'); row[stream] = dict(path=path.name, **pin(path))
        save(); need(status == 0 and not row.get('timed_out'), 'actual terminal zero: ' + name)
        return (out / (name + '.stdout.log')).read_bytes()
    save()
    try:
        for name in SOURCES:
            destination = out / 'sources' / name; destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / name).read_bytes())
            report['sources'].append(dict(path=name, snapshot=destination.relative_to(out).as_posix(), **pin(destination)))
        command('compiler-version', ['/usr/bin/gcc', '--version'])
        compiler = command('compiler-path', ['readlink', '-f', '/usr/bin/gcc']).decode().strip()
        library = command('libopus-path', ['readlink', '-f', '/lib/x86_64-linux-gnu/libopus.so.0']).decode().strip()
        report['compiler_identity'] = command('compiler-sha', ['sha256sum', compiler]).decode().strip()
        report['libopus_identity'] = command('libopus-sha', ['sha256sum', library]).decode().strip()
        flags = ['-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror', '-Wpedantic', '-Wformat=2',
                 '-fsanitize=address,undefined,float-cast-overflow', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
        command('build', ['/usr/bin/gcc', *flags, host(out / 'sources/tests/native/opus_frame_control_public.c'),
                          library, '-lm', '-o', host(out / 'control')])
        report['executable'] = dict(path='control', local_only=True, **pin(out / 'control')); save()
        names = list(creator['cases'])
        for name in SELECTED:
            folder = out / name; folder.mkdir(); original = creator['cases'][name]
            source = reference / original['artifacts']['framed.packets']['path']; path = folder / 'input.packets'
            need(pin(source) == {k: original['artifacts']['framed.packets'][k] for k in ('bytes', 'sha256')}, 'exact complete framed source input')
            path.write_bytes(source.read_bytes())
            rows = [json.loads(line) for line in command(name, ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1', host(out / 'control'), host(path), host(folder)]).decode().splitlines()]
            need(len(rows) == 5 and rows[-1]['summary'] and rows[-1]['packets'] == 4 and not rows[-1]['private_abi_used'] and
                 not rows[-1]['numeric_tolerance_applied'], 'complete public cadence observations')
            aggregate = (folder / 'aggregate-s16.pcm').read_bytes()
            prior = reference / original['artifacts']['raw.pcm']['path']
            need(pin(prior) == {k: original['artifacts']['raw.pcm'][k] for k in ('bytes', 'sha256')} and aggregate == prior.read_bytes(),
                 'identical aggregate creator reference and decoder progression')
            row = vendor['measurements']['cases'][names.index(name) * 4]
            actual = native / row['complete_pcm']['raw']['path']
            need(pin(actual) == {k: row['complete_pcm']['raw'][k] for k in ('bytes', 'sha256')}, 'exact previous stock-whole native PCM')
            comparisons = {}
            for filename in ('aggregate-s16.pcm', 'elementary-s16.pcm', 'aggregate-hard-s16.pcm', 'elementary-hard-s16.pcm',
                             'aggregate-soft-s16.pcm', 'elementary-soft-s16.pcm'):
                comparisons[filename] = integer_compare(actual.read_bytes(), (folder / filename).read_bytes())
            record = dict(observations=rows, comparisons_to_previous_native=comparisons,
                          aggregate_creator_reference_unchanged=True, files={})
            for path in sorted(folder.iterdir()):
                record['files'][path.name] = dict(path=path.relative_to(out).as_posix(), local_only=True, **pin(path))
            report['cases'][name] = record; save()
            print(json.dumps(dict(name=name, summary=rows[-1], comparisons=comparisons)), flush=True)
        need(command('libopus-post-sha', ['sha256sum', library]).decode().strip() == report['libopus_identity'], 'creator library unchanged')
        need(command('compiler-post-sha', ['sha256sum', compiler]).decode().strip() == report['compiler_identity'], 'compiler unchanged')
        for row in report['sources']:
            need(pin(ROOT / row['path']) == pin(out / row['snapshot']) == dict(bytes=row['bytes'], sha256=row['sha256']), 'all source bytes unchanged')
        report.update(passed=True, completed=True, all_source_bindings_current=True)
        return 0
    except Exception as error:
        report['failure'] = dict(type=type(error).__name__, reason=str(error)); print(json.dumps(dict(passed=False, failure=report['failure'])))
        return 1
    finally:
        save()


if __name__ == '__main__':
    raise SystemExit(main())
