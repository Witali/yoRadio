"""Check actual CYD PCM mixing and three output producers against fixed-point reference.

Driver/resampler calls are capture seams; this does not measure DMA or CPU on CYD.
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


def function(source, name):
    match = re.search(r'^(?:static )?[^\n]*\b' + name + r'\(', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source_path = ROOT / 'idf/esp32-cyd2usb-native/main/native_audio_output.c'
    case_path = ROOT / 'tests/native/cyd_output_gain_test.c'
    source = source_path.read_text()
    common = source[source.index('static int16_t scale_sample_q15('):
                    source.index('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM')]
    # Count actual coefficient evaluations while preserving its arithmetic.
    common = common.replace('static uint32_t channel_gain_q15(',
                            'static uint32_t production_channel_gain_q15(', 1)
    common = common.replace('static pcm_gains_t pcm_channel_gains(', '''
static uint32_t channel_gain_q15(uint8_t volume, uint8_t balance) {
    ++gain_calls;
    return production_channel_gain_q15(volume, balance);
}
static pcm_gains_t pcm_channel_gains(''', 1)
    constants = ''
    for name in ('OUTPUT_PACKET_BYTES', 'SAMPLE_GAIN_SCALE', 'VOLUME_DENOMINATOR',
                 'BALANCE_DENOMINATOR', 'LEGACY_OUTPUT_BYTES', 'LEGACY_OVERSAMPLE_FACTOR'):
        constants += re.search(r'^#define ' + name + r'[^\n]+', source, re.M).group(0) + '\n'
    branches = {
        'pdm': source.split('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM', 1)[1]
                     .split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[0],
        'dac': source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[1]
                     .split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[0],
        'legacy': source.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[1],
    }
    results = {}
    for backend, branch in branches.items():
        generated = constants + common
        if backend == 'legacy':
            generated += '\n'.join(function(branch, name) for name in (
                'legacy_pack_dac_code', 'legacy_fractional_dac_step', 'legacy_write_frames'))
        generated += function(branch, 'native_audio_output_write_pcm')
        include = out / (backend + '.inc')
        include.write_text(generated)
        unit = out / (backend + '.c')
        unit.write_text(case_path.read_text().replace('/* PRODUCTION */', generated))
        binary = out / backend
        try:
            (out / (backend + '-build.log')).write_bytes(run([
                'gcc', '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
                '-Wno-unused-function', '-Wno-unused-variable',
                '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                '-fno-pie', '-no-pie', '-DTEST_' + backend.upper() + '=1',
                host(unit), '-o', host(binary)]))
            log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                       'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
        except subprocess.CalledProcessError as error:
            (out / (backend + '-failure.log')).write_bytes(error.output)
            print(error.output.decode(errors='replace'), file=sys.stderr)
            raise
        (out / (backend + '.log')).write_bytes(log)
        results[backend] = log.decode().strip()
        print(backend + ': ' + results[backend])
    files = [source_path, case_path, Path(__file__).resolve()]
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
