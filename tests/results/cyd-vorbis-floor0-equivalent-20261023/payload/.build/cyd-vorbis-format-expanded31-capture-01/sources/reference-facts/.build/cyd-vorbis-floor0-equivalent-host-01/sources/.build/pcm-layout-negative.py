from pathlib import Path
import importlib.util
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools/codec_benchmark'))
from run_output_dma_host import host, run

spec = importlib.util.spec_from_file_location('gain', root / 'tests/run-cyd-output-gain.py')
gain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gain)
baseline = subprocess.check_output([
    'git', 'show', '900e009c:idf/esp32-cyd2usb-native/main/native_audio_output.c'], cwd=root).decode()
out = root / '.build/pcm-layout-negative'
out.mkdir(exist_ok=False)
(out / 'baseline.c').write_text(baseline)
objects = root / '.build/pcm-layout-final'
flags = ['-O2', '-g', '-Wall', '-Wextra', '-Werror',
         '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
         '-fno-pie', '-pthread']
adapter = root / 'idf/components/native_audio_normalizer'
branches = {
    'pdm': baseline.split('#if CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM', 1)[1]
                   .split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[0],
    'dac': baseline.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC', 1)[1]
                   .split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[0],
    'legacy': baseline.split('#elif CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC', 1)[1],
}
expected = {'pdm': b'captured_size == expected_size',
            'dac': b'native_audio_output_configure(24000) == ESP_FAIL',
            'legacy': b'native_audio_output_configure(24000) == ESP_FAIL'}
for backend, branch in branches.items():
    unit, obj, binary = out / (backend + '.c'), out / (backend + '.o'), out / backend
    actual = (objects / (backend + '.c')).read_text()
    actual = actual.replace(gain.function(actual, 'native_audio_output_configure').rstrip(),
                            gain.function(branch, 'native_audio_output_configure').rstrip(), 1)
    unit.write_text(actual)
    (out / (backend + '-build.log')).write_bytes(run([
        'gcc', '-std=c11', *flags, '-Wno-unused-function', '-Wno-unused-variable',
        '-DTEST_' + backend.upper() + '=1', '-I' + host(adapter),
        '-c', host(unit), '-o', host(obj)]))
    (out / (backend + '-link.log')).write_bytes(run([
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
        (out / (backend + '-negative.log')).write_bytes(error.output)
        assert expected[backend] in error.output, error.output
        print('PASS negative control: original ' + backend + ' configure fails its regression')
    else:
        raise AssertionError('Old ' + backend + ' configure unexpectedly accepted the regression')
