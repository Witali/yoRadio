"""Compile the actual adaptive queue/TLS wrapper with pthread/heap platform stubs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def body(path):
    return re.sub(r'^#(?:include|pragma once)[^\n]*\n', '', path.read_text(), flags=re.M)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    main = ROOT / 'idf/esp32c3-oled-native/main'
    harness = ROOT / 'tests/native/adaptive_input_test.c'
    inputs = [main / name for name in ('adaptive_input.h', 'adaptive_input.c',
                                      'tls_input_reserve.c', 'tls_input_reserve.h')]
    inputs += [harness, Path(__file__).resolve()]
    for source in inputs:
        saved = args.output / 'sources' / source.relative_to(ROOT)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(source.read_bytes())
    unit = args.output / 'test.c'
    unit.write_text(harness.read_text()
                    .replace('/* PRODUCTION_HEADER */', body(inputs[0]) + body(inputs[3]))
                    .replace('/* PRODUCTION_QUEUE */', body(inputs[1]))
                    .replace('/* PRODUCTION_TLS */', body(inputs[2])))
    binary = args.output / 'test'
    (args.output / 'build.log').write_bytes(run([
        'gcc', '-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1', '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
        '-Wno-unused-variable', '-pthread', '-fsanitize=address,undefined',
        '-fno-pie', '-no-pie', host(unit), '-o', host(binary)]))
    result = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                  'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
    (args.output / 'run.log').write_bytes(result)
    assert result.startswith(b'PASS adaptive input:')
    (args.output / 'report.json').write_text(json.dumps(dict(
        passed=True, stress_packets=30000, sanitizers=['address', 'undefined'],
        scope='Actual queue and TLS pressure wrapper; pthread RTOS and simulated heap. Not physical TLS/PCM qualification.',
        sources={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    ), indent=2) + '\n')
    print(result.decode())


if __name__ == '__main__':
    main()
