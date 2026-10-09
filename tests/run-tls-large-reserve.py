"""Test the actual reserved-slot allocator and TLS wrapper under ASan/UBSan."""
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
    support = ROOT / 'tests/native/adaptive_input_test.c'
    harness = ROOT / 'tests/native/tls_large_reserve_test.c'
    inputs = [main / name for name in ('adaptive_input.h', 'adaptive_input.c',
              'tls_input_reserve.c', 'tls_large_reserve.h', 'tls_large_reserve.c',
              'tls_input_reserve.h')]
    inputs += [support, harness, Path(__file__).resolve()]
    for source in inputs:
        target = args.output / 'sources' / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    common = support.read_text().split('/* PRODUCTION_HEADER */')[0]
    common += body(inputs[0]) + body(inputs[3]) + body(inputs[5])
    variants = []
    for adaptive, rx_only, flac_slots in ((False, False, 0), (True, False, 0),
                                         (False, True, 0), (True, True, 0),
                                         (True, True, 4)):
        name = ('adaptive' if adaptive else 'pool-only') + ('-rx-only' if rx_only else '')
        if flac_slots:
            name += '-flac4'
        queue = ('#define calloc checked_calloc\n#define malloc checked_malloc\n#define free checked_free\n'
                 + body(inputs[1]) + '\n#undef calloc\n#undef malloc\n#undef free\n') if adaptive else ''
        unit = args.output / (name + '.c')
        unit.write_text(common + queue + harness.read_text()
                        .replace('/* PRODUCTION_POOL */', body(inputs[4]))
                        .replace('/* PRODUCTION_WRAPPER */', body(inputs[2])))
        binary = args.output / name
        (args.output / (name + '-build.log')).write_bytes(run([
            'gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
            '-Wno-unused-variable', '-Wno-unused-function', '-pthread',
            '-DCONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE=1',
            f'-DCONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS={flac_slots}',
            *(['-DCONFIG_YORADIO_TLS_RX_ONLY_RESERVE=1'] if rx_only else []),
            *(['-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1'] if adaptive else []),
            '-fsanitize=address,undefined', '-fno-pie', '-no-pie', host(unit), '-o', host(binary)]))
        result = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                      'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
        (args.output / (name + '.log')).write_bytes(result)
        assert result.startswith(b'PASS TLS large reserve:')
        variants.append(dict(adaptive_input=adaptive, rx_only=rx_only, flac_extra_slots=flac_slots,
                             passed=True, concurrent_allocations=8000))
    (args.output / 'report.json').write_text(json.dumps(dict(
        variants=variants, sanitizers=['address', 'undefined'],
        scope='Actual C allocators; pthread platform and simulated heap. SDK sizing separately verified in ELF; no physical qualification.',
        sources={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    ), indent=2) + '\n')
    print('PASS TLS reserve: four baseline variants and bounded FLAC expansion')


if __name__ == '__main__':
    main()
