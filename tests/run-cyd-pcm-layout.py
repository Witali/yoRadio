"""Qualify actual CYD packed PCM conversion and resampling without changing hardware clocks.

All backend producers and PDM interpolation/buffering are production functions.
Driver captures and deterministic faults replace hardware; the shared normalizer
runs unchanged. Independent wide-integer references verify packed signed LE
8/16/24/32 conversion, gain/mix, resampling and complete-frame boundaries.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run

spec = importlib.util.spec_from_file_location('cyd_gain_helpers', ROOT / 'tests/run-cyd-output-gain.py')
gain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gain)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source_path = ROOT / 'idf/esp32-cyd2usb-native/main/native_audio_output.c'
    case_path = ROOT / 'tests/native/cyd_pcm_layout_test.c'
    platform_path = ROOT / 'tests/native/cyd_normalizer_test.c'
    bridge_path = ROOT / 'tests/native/cyd_normalizer_reference.cpp'
    adapter = ROOT / 'idf/components/native_audio_normalizer'
    algorithm = ROOT / 'yoRadio/src/audioI2S'
    source = source_path.read_text()
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
    platform = platform_path.read_text().split('/* PRODUCTION */', 1)[0]
    old_capture = 'captured[3072 * 16 * 4]'
    assert old_capture in platform
    platform = platform.replace(old_capture, 'captured[8192 * 16 * 4]', 1)
    # Retain shared driver types/configuration seams; add precise short-write
    # and failure capture to every backend instead of replacing its producer.
    original_write = gain.function(platform, 'dac_continuous_write').rstrip()
    platform = platform.replace(original_write, '''
static int test_driver_write(const void *, size_t, size_t *);
static int dac_continuous_write(void *handle, const void *data, size_t size,
                                 size_t *written, unsigned timeout) {
    (void)handle; (void)timeout;
    return test_driver_write(data, size, written);
}''', 1)
    common_flags = ['-O2', '-g', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    '-fno-pie', '-pthread']
    shared_objects = []
    for path in (adapter / 'native_audio_normalizer.cpp',
                 algorithm / 'AudioNormalizer.cpp', bridge_path):
        obj = out / (path.stem + '.o')
        (out / (path.stem + '-build.log')).write_bytes(run([
            'g++', '-std=c++17', *common_flags,
            '-I' + host(adapter), '-I' + host(algorithm),
            '-c', host(path), '-o', host(obj)]))
        shared_objects.append(host(obj))
    results = {}
    for backend, branch in branches.items():
        platform_variant = platform
        generated = constants + common
        if backend == 'pdm':
            for name in ('pdm_write_resampled', 'pdm_flush', 'reset_resampler'):
                platform_variant = platform_variant.replace(
                    gain.function(platform_variant, name).rstrip(), '', 1)
            generated += '\n'.join(gain.function(branch, name) for name in (
                'reset_resampler', 'pdm_write_block', 'pdm_flush',
                'pdm_queue_sample', 'pdm_write_resampled'))
        if backend == 'dac':
            generated += gain.function(branch, 'dac_write_block')
        if backend == 'legacy':
            generated += '\n'.join(gain.function(branch, name) for name in (
                'legacy_pack_dac_code', 'legacy_fractional_dac_step',
                'legacy_write_frames', 'legacy_write_silence'))
        generated += '\n'.join(gain.function(branch, name) for name in (
            'native_audio_output_configure', 'native_audio_output_write_pcm',
            'native_audio_output_discard_pcm', 'native_audio_output_flush_pcm'))
        if backend == 'dac':
            generated += gain.function(branch, 'native_audio_output_pause')
        (out / (backend + '.inc')).write_text(generated)
        unit, obj, binary = out / (backend + '.c'), out / (backend + '.o'), out / backend
        unit.write_text(case_path.read_text().replace('/* PLATFORM */', platform_variant)
                        .replace('/* PRODUCTION */', generated))
        try:
            (out / (backend + '-build.log')).write_bytes(run([
                'gcc', '-std=c11', *common_flags,
                '-Wno-unused-function', '-Wno-unused-variable',
                '-DTEST_' + backend.upper() + '=1', '-I' + host(ROOT / 'tests/native'), '-I' + host(adapter),
                '-c', host(unit), '-o', host(obj)]))
            (out / (backend + '-link.log')).write_bytes(run([
                'g++', *common_flags, '-no-pie', host(obj), *shared_objects,
                '-Wl,--wrap=native_audio_normalizer_configure',
                '-Wl,--wrap=native_audio_normalizer_reset',
                '-Wl,--wrap=native_audio_normalizer_process_block',
                '-o', host(binary)]))
            log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                       'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
        except subprocess.CalledProcessError as error:
            (out / (backend + '-failure.log')).write_bytes(error.output)
            print(error.output.decode(errors='replace'), file=sys.stderr)
            raise
        (out / (backend + '.log')).write_bytes(log)
        results[backend] = log.decode().strip()
        print(backend + ': ' + results[backend])
    files = [source_path, case_path, platform_path, bridge_path, Path(__file__).resolve(),
             ROOT / 'tests/run-cyd-output-gain.py',
             ROOT / 'idf/esp32-cyd2usb-native/main/native_audio_output.h',
             adapter / 'native_audio_normalizer.cpp', adapter / 'native_audio_normalizer.h',
             algorithm / 'AudioNormalizer.cpp', algorithm / 'AudioNormalizer.h']
    files.append(ROOT / 'tests/native/cyd_output_metrics_noop.h')
    hashes = {}
    for path in files:
        relative = path.relative_to(ROOT)
        destination = out / 'sources' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
        hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    (out / 'report.json').write_text(json.dumps(dict(
        passed=True, variants=results, sources=hashes,
        compiler=run(['gcc', '--version']).decode().splitlines()[0],
        scope=__doc__, physical_hardware=False), indent=2) + '\n')


if __name__ == '__main__':
    main()
