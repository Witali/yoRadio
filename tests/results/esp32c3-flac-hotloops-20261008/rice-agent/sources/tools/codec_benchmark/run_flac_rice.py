"""Differentially test actual scalar/bytewise FLAC Rice readers with ASan/UBSan.

Checks values, error status, consumed bytes, and the complete remaining bit cache
against an independent scalar extractor. This is correctness evidence; host CLZ
timing does not establish speed on ESP32-C3.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from run_output_dma_host import host, run, ROOT


def logged_run(command, destination):
    try:
        output = run(command)
    except subprocess.CalledProcessError as error:
        destination.write_bytes(error.output)
        print(error.output.decode(errors='replace'))
        raise
    destination.write_bytes(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    src = ROOT / 'yoRadio/src/audioI2S/flac_decoder'
    test = ROOT / 'tests/native/flac_bounds'
    files = [src / 'flac_decoder.cpp', src / 'flac_decoder.h', test / 'Arduino.h',
             test / 'rice.cpp', Path(__file__), ROOT / 'tools/codec_benchmark/run_output_dma_host.py']
    report = {'sanitizers': ['address', 'undefined'], 'physical_timing': False,
              'sources': {}, 'variants': {}}
    for path in files:
        name = path.relative_to(ROOT).as_posix()
        target = out / 'sources' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        content = path.read_bytes()
        target.write_bytes(content)
        report['sources'][name] = hashlib.sha256(content).hexdigest()
    frozen_src = out / 'sources/yoRadio/src/audioI2S/flac_decoder'
    frozen_test = out / 'sources/tests/native/flac_bounds'
    flags = ['g++', '-std=c++14', '-O2', '-g', '-Wall', '-Wextra',
             '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
             '-I' + host(frozen_test), '-I' + host(frozen_src)]
    for name, defines in [('default', []), ('scalar', ['-DFLAC_BYTEWISE_RICE=0']),
                          ('bytewise', ['-DFLAC_BYTEWISE_RICE=1'])]:
        binary = out / name
        logged_run(flags + defines + [host(frozen_test / 'rice.cpp'), '-o', host(binary)],
                   out / (name + '-build.log'))
        log = logged_run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                          'UBSAN_OPTIONS=halt_on_error=1', host(binary)], out / (name + '.log'))
        report['variants'][name] = json.loads(log)
    report['identical'] = all(value == report['variants']['default']
                              for value in report['variants'].values())
    report['passed'] = report['identical'] and all(
        value['passed'] for value in report['variants'].values())
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
