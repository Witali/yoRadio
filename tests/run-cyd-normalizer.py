"""Exercise actual CYD PCM producers and the shared normalizer with guarded host seams.

Runs all three backend producers using immutable, unaligned PCM. The reference
feeds the original C3 AudioNormalizer one stereo frame at a time; production
uses its block API through the shared C adapter and bounded scratch storage.
Driver calls are capture seams, not physical CYD DMA or timing measurements.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run
sys.path.insert(0, str(ROOT / 'tests'))
import importlib.util
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
    case_path = ROOT / 'tests/native/cyd_normalizer_test.c'
    bridge_path = ROOT / 'tests/native/cyd_normalizer_reference.cpp'
    adapter = ROOT / 'idf/components/native_audio_normalizer'
    normalizer = ROOT / 'yoRadio/src/audioI2S'
    source = source_path.read_text()
    common = source[source.index('static int16_t scale_sample_q15('):
                    source.index('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM')]
    constants = ''
    for name in ('OUTPUT_PACKET_BYTES', 'SAMPLE_GAIN_SCALE', 'VOLUME_DENOMINATOR',
                 'BALANCE_DENOMINATOR', 'NORMALIZER_CHUNK_FRAMES',
                 'LEGACY_OUTPUT_BYTES', 'LEGACY_OVERSAMPLE_FACTOR',
                 'LEGACY_DMA_DESCRIPTORS', 'LEGACY_DMA_FRAMES',
                 'LEGACY_MIN_INPUT_SAMPLE_RATE', 'LEGACY_MAX_INPUT_SAMPLE_RATE'):
        constants += re.search(r'^#define ' + name + r'[^\n]+', source, re.M).group(0) + '\n'
    branches = {
        'pdm': source.split('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM', 1)[1]
                     .split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[0],
        'dac': source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[1]
                     .split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[0],
        'legacy': source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[1],
    }
    results = {}
    common_flags = ['-O2', '-g', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    '-fno-pie', '-pthread']
    shared_objects = []
    for path in (adapter / 'native_audio_normalizer.cpp',
                 normalizer / 'AudioNormalizer.cpp', bridge_path):
        obj = out / (path.stem + '.o')
        (out / (path.stem + '-build.log')).write_bytes(run([
            'g++', '-std=c++17', *common_flags,
            '-I' + host(adapter), '-I' + host(normalizer),
            '-c', host(path), '-o', host(obj)]))
        shared_objects.append(host(obj))
    for backend, branch in branches.items():
        generated = constants + common
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
        unit = out / (backend + '.c')
        unit.write_text(case_path.read_text().replace('/* PRODUCTION */', generated))
        binary, obj = out / backend, out / (backend + '.o')
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
    files = [source_path, case_path, bridge_path, Path(__file__).resolve(),
             ROOT / 'tests/run-cyd-output-gain.py',
             adapter / 'native_audio_normalizer.cpp',
             adapter / 'native_audio_normalizer.h', adapter / 'CMakeLists.txt',
             normalizer / 'AudioNormalizer.cpp', normalizer / 'AudioNormalizer.h',
             ROOT / 'idf/esp32-cyd2usb-native/CMakeLists.txt',
             ROOT / 'idf/esp32-cyd2usb-native/main/CMakeLists.txt',
             ROOT / 'idf/esp32-cyd2usb-native/main/native_audio_output.h',
             ROOT / 'idf/esp32-cyd2usb-native/main/radio_control_platform.h']
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
