"""Qualify actual FLAC signed fields, wasted-bit bounds and malformed errors.

Uses ASan/UBSan with both workspace geometries and scalar/bytewise Rice modes.
An optional earlier revision records reference behavior without changing checkout
sources. These are host correctness tests, not target timing measurements.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from run_output_dma_host import ROOT, host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--revision', help='Freeze earlier core sources for a reference comparison')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    core = Path('yoRadio/src/audioI2S/flac_decoder')
    test = Path('tests/native/flac_bounds')
    files = [core / 'flac_decoder.cpp', core / 'flac_decoder.h',
             test / 'Arduino.h', test / 'warnings.cpp',
             Path(__file__).resolve().relative_to(ROOT)]
    report = dict(revision=args.revision, sanitizers=['address', 'undefined'],
                  physical_timing=False, sources={}, variants={})
    for name in files:
        data = (subprocess.check_output(['git', 'show', args.revision + ':' + name.as_posix()], cwd=ROOT)
                if args.revision and name.parent == core else (ROOT / name).read_bytes())
        target = out / 'sources' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        report['sources'][name.as_posix()] = hashlib.sha256(data).hexdigest()
    source = out / 'sources'
    for segmented in (False, True):
        for bytewise in (False, True):
            name = ('segmented' if segmented else 'contiguous') + ('-bytewise' if bytewise else '-scalar')
            binary = out / name
            command = ['g++', '-std=c++14', '-O2', '-g', '-fsanitize=address,undefined',
                       '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                       '-I' + host(source / test), '-I' + host(source / core),
                       '-DFLAC_BYTEWISE_RICE=' + str(int(bytewise))]
            if segmented: command += ['-DFLAC_SEGMENTED_WORKSPACE=1', '-DFLAC_OUTPUT_FRAMES=512']
            (out / (name + '-build.log')).write_bytes(run(command + [
                host(source / test / 'warnings.cpp'), '-o', host(binary)]))
            results = {}
            for case in ('signed', 'wasted', 'errors'):
                try:
                    log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                               'UBSAN_OPTIONS=halt_on_error=1', host(binary), case])
                    result = dict(passed=True, output=log.decode().strip())
                except subprocess.CalledProcessError as error:
                    log = error.output
                    result = dict(passed=False, exit_code=error.returncode)
                (out / (name + '-' + case + '.log')).write_bytes(log)
                results[case] = result
                print(name, case, 'PASS' if result['passed'] else 'FAIL', flush=True)
            report['variants'][name] = results
    report['passed'] = all(case['passed'] for cases in report['variants'].values() for case in cases.values())
    report['compiler'] = run(['g++', '--version']).decode().splitlines()[0]
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] or args.revision else 1


if __name__ == '__main__':
    sys.exit(main())
