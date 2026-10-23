from pathlib import Path
import sys
import subprocess

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools/codec_benchmark'))
from run_output_dma_host import host, run

out = root / '.build/normalizer-prime-negative'
out.mkdir(exist_ok=False)
unit = out / 'baseline.c'
source = (root / 'tests/native/cyd_normalizer_test.c').read_text()
source = source.replace('/* PRODUCTION */',
                        (root / '.build/normalizer-final/dac.inc').read_text())
# Let the old cached-ready flag through to demonstrate the actual subsequent
# same-rate retry returning ESP_OK while retaining the previous DSP rate.
source = source.replace('assert(s_dac_sample_rate == 0 && s_pcm_sample_rate == before_rate);',
                        'assert(s_pcm_sample_rate == before_rate);')
unit.write_text(source)
adapter = root / 'idf/components/native_audio_normalizer'
objects = root / '.build/normalizer-prime-retry'
flags = ['-O2', '-g', '-Wall', '-Wextra', '-Werror',
         '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
         '-fno-pie', '-pthread']
obj, binary = out / 'baseline.o', out / 'baseline'
(out / 'build.log').write_bytes(run([
    'gcc', '-std=c11', *flags, '-Wno-unused-function', '-Wno-unused-variable',
    '-DTEST_DAC=1', '-I' + host(adapter), '-c', host(unit), '-o', host(obj)]))
(out / 'link.log').write_bytes(run([
    'g++', *flags, '-no-pie', host(obj),
    *[host(objects / name) for name in ('native_audio_normalizer.o',
                                       'AudioNormalizer.o', 'cyd_normalizer_reference.o')],
    '-Wl,--wrap=native_audio_normalizer_configure',
    '-Wl,--wrap=native_audio_normalizer_reset',
    '-Wl,--wrap=native_audio_normalizer_process_block', '-o', host(binary)]))
try:
    run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
         'UBSAN_OPTIONS=halt_on_error=1', host(binary)])
except subprocess.CalledProcessError as error:
    (out / 'negative.log').write_bytes(error.output)
    assert b's_pcm_sample_rate == rate' in error.output, error.output
    print('PASS negative control: old DAC prime/retry retains the previous DSP rate')
else:
    raise AssertionError('Old DAC configure unexpectedly accepted the regression')
