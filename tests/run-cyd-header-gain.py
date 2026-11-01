"""Qualify ordered CYD output-owner header gain using actual shared reader/producers.

Driver calls are guarded captures, not physical DMA/timing evidence. Independent
Decimal references specify post-normalizer S16 projection, existing rounded Q15
user coefficients, wide mono mix and final rounding/saturation. The unchanged
AudioNormalizer reference separately verifies adaptive state and block ordering.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from decimal import Decimal, localcontext, ROUND_HALF_UP
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run

spec = importlib.util.spec_from_file_location('gain_helpers', ROOT / 'tests/run-cyd-output-gain.py')
gain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gain)


def coefficient(volume, balance):
    return (volume * balance * 32768 + 2032) // 4064


def rounded(value):
    return int(value.to_integral_value(rounding=ROUND_HALF_UP))


def expected_mono(header, left, right, channels, volume, balance, precision):
    gl = coefficient(volume, 16 + balance if channels > 1 and balance < 0 else 16)
    gr = coefficient(volume, 16 - balance if balance > 0 else 16)
    with localcontext() as context:
        context.prec = precision
        if not header:
            l = rounded(Decimal(left * gl) / 32768)
            r = rounded(Decimal(right * gr) / 32768)
            value = l if channels == 1 else int(Decimal(l + r) / 2)
        else:
            factor = (Decimal(10).ln() * Decimal(header) / 5120).exp()
            value = rounded(Decimal(left * gl + (right * gr if channels > 1 else 0)) *
                            factor / (65536 if channels > 1 else 32768))
    return min(32767, max(-32768, value))


def reference_vectors():
    headers = [-32768, -48 * 256, -6 * 256, -1, 0, 1, 6 * 256, 48 * 256, 32767]
    pairs = [(-32768, 32767), (-30000, 29900), (-1, 1), (0, 0), (1, -1),
             (25000, 25000), (30000, -29900), (32767, -32768)]
    result = []
    for bits, channels, header, pair, volume, balance in itertools.product(
            (8, 16, 24, 32), (1, 2, 3, 255), headers, pairs, (0, 1, 127, 254), (-16, 0, 16)):
        left, right = pair
        if bits == 8:
            left, right = (left // 256) * 256, (right // 256) * 256
        a = expected_mono(header, left, right, channels, volume, balance, 80)
        b = expected_mono(header, left, right, channels, volume, balance, 120)
        assert a == b
        result.append((bits, channels, header, left, right, volume, balance, a))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    production = ROOT / 'idf/esp32-cyd2usb-native/main/native_audio_output.c'
    harness = ROOT / 'tests/native/cyd_header_gain_test.c'
    platform_file = ROOT / 'tests/native/cyd_normalizer_test.c'
    bridge = ROOT / 'tests/native/cyd_normalizer_reference.cpp'
    adapter = ROOT / 'idf/components/native_audio_normalizer'
    algorithm = ROOT / 'yoRadio/src/audioI2S'
    include = ROOT / 'idf/components/native_stream/include'
    files = [production, production.with_suffix('.h'), harness, platform_file, bridge,
             adapter / 'native_audio_normalizer.cpp', adapter / 'native_audio_normalizer.h',
             algorithm / 'AudioNormalizer.cpp', algorithm / 'AudioNormalizer.h',
             include / 'pcm_header_gain.h', include / 'pcm_channel_layout.h', include / 'pcm_speaker_mix.h',
             ROOT / 'tests/native/cyd_output_metrics_noop.h',
             ROOT / 'tests/run-cyd-output-gain.py', ROOT / 'tools/codec_benchmark/run_output_dma_host.py',
             Path(__file__).resolve()]
    report = dict(passed=False, state='preparing', variants={}, sources={},
                  physical_hardware=False, numerical_conformance_claim=False, scope=__doc__)
    for path in files:
        data = path.read_bytes()
        name = path.relative_to(ROOT).as_posix()
        report['sources'][name] = hashlib.sha256(data).hexdigest()
        dest = out / 'sources' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    try:
        rows = reference_vectors()
        header = ('typedef struct { unsigned bits, channels; int gain, left, right; '
                  'unsigned volume; int balance, expected; } gain_vector;\n'
                  'static const gain_vector vectors_data[] = {\n' +
                  ''.join('    {' + ','.join(map(str, row)) + '},\n' for row in rows) + '};\n')
        (out / 'reference_vectors.h').write_text(header)
        (out / 'reference_vectors.json').write_text(json.dumps(rows, separators=(',', ':')) + '\n')
        report['decimal_vectors'] = len(rows)
        source = production.read_text()
        common = source[source.index('static int16_t scale_sample_q15('):
                        source.index('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM')]
        constants = '\n'.join(re.findall(r'^#define [^\n]+', source, re.M)) + '\n'
        branches = {
            'pdm': source.split('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM', 1)[1]
                         .split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[0],
            'dac': source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[1]
                         .split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[0],
            'legacy': source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[1],
        }
        platform = platform_file.read_text().split('/* PRODUCTION */', 1)[0]
        platform = platform.replace('captured[3072 * 16 * 4]', 'captured[8192 * 16 * 4]', 1)
        platform = platform.replace(gain.function(platform, 'dac_continuous_write').rstrip(), '''
static int test_driver_write(const void *, size_t, size_t *);
static int dac_continuous_write(void *handle, const void *data, size_t size,
                                 size_t *written, unsigned timeout) {
    (void)handle; (void)timeout; return test_driver_write(data, size, written);
}''', 1)
        # Pause failures exercise real lifecycle entry points with driver stubs.
        platform = platform.replace('static int dac_continuous_disable(void *handle) { (void)handle; return ESP_OK; }',
                                    'static int pause_result;\nstatic int dac_continuous_disable(void *handle) { (void)handle; return pause_result; }')
        flags = ['-O2', '-g', '-Wall', '-Wextra', '-Werror',
                 '-fsanitize=address,undefined,float-cast-overflow', '-fno-omit-frame-pointer', '-fno-pie', '-pthread']
        objects = []
        for path in (adapter / 'native_audio_normalizer.cpp', algorithm / 'AudioNormalizer.cpp', bridge):
            obj = out / (path.stem + '.o')
            (out / (path.stem + '-build.log')).write_bytes(run([
                'g++', '-std=c++17', *flags, '-I' + host(adapter), '-I' + host(algorithm),
                '-c', host(path), '-o', host(obj)]))
            objects.append(host(obj))
        report['state'] = 'executing'
        save()
        for backend, branch in branches.items():
            p = platform
            generated = '#include "pcm_header_gain.h"\n#include "pcm_channel_layout.h"\n#include "pcm_speaker_mix.h"\n' + constants + common
            if backend == 'pdm':
                for name in ('pdm_write_resampled', 'pdm_flush', 'reset_resampler'):
                    p = p.replace(gain.function(p, name).rstrip(), '', 1)
                generated += ''.join(gain.function(branch, name) for name in (
                    'reset_resampler', 'pdm_write_block', 'pdm_flush', 'pdm_queue_sample', 'pdm_write_resampled'))
            if backend == 'dac':
                generated += gain.function(branch, 'dac_write_block')
            if backend == 'legacy':
                generated += ''.join(gain.function(branch, name) for name in (
                    'legacy_pack_dac_code', 'legacy_fractional_dac_step', 'legacy_write_frames', 'legacy_write_silence'))
            generated += ''.join(gain.function(branch, name) for name in (
                'native_audio_output_configure', 'native_audio_output_write_pcm',
                'native_audio_output_discard_pcm', 'native_audio_output_flush_pcm', 'native_audio_output_pause'))
            (out / (backend + '.inc')).write_text(generated)
            unit, obj, binary = out / (backend + '.c'), out / (backend + '.o'), out / backend
            unit.write_text(harness.read_text().replace('/* PLATFORM */', p).replace('/* PRODUCTION */', generated))
            (out / (backend + '-build.log')).write_bytes(run([
                'gcc', '-std=c11', *flags, '-Wno-unused-function', '-Wno-unused-variable',
                '-DTEST_' + backend.upper() + '=1', '-I' + host(ROOT / 'tests/native'),
                '-I' + host(adapter), '-I' + host(include), '-I' + host(out),
                '-c', host(unit), '-o', host(obj)]))
            (out / (backend + '-link.log')).write_bytes(run([
                'g++', *flags, '-no-pie', host(obj), *objects,
                '-Wl,--wrap=native_audio_normalizer_configure', '-Wl,--wrap=native_audio_normalizer_reset',
                '-Wl,--wrap=native_audio_normalizer_process_block', '-lm', '-o', host(binary)]))
            trace = out / (backend + '-normalizer-reference.csv')
            log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS=halt_on_error=1',
                       host(binary), host(trace)])
            (out / (backend + '.log')).write_bytes(log)
            trace_rows = [tuple(map(int, line.split(','))) for line in trace.read_text().splitlines()]
            for row in trace_rows:
                assert expected_mono(*row[:6], 80) == row[6]
                assert expected_mono(*row[:6], 120) == row[6]
            report['variants'][backend] = dict(passed=True, result=log.decode().strip(),
                                                decimal_trace_checks=len(trace_rows))
            save()
            print(backend + ': ' + log.decode().strip(), flush=True)
        assert all(hashlib.sha256(path.read_bytes()).hexdigest() == report['sources'][path.relative_to(ROOT).as_posix()]
                   for path in files), 'sources changed during qualification'
        report.update(passed=True, state='complete', compiler=run(['gcc', '--version']).decode().splitlines()[0])
    except BaseException as error:
        report.update(passed=False, state='nonpass', error=type(error).__name__)
        if isinstance(error, subprocess.CalledProcessError):
            (out / 'failure.log').write_bytes(error.output)
            print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
