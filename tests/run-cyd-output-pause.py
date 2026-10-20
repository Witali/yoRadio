"""Exercise production CYD backend pause/cleanup under ASan/UBSan.

Driver calls are explicit hardware seams; no physical DMA timing is claimed.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    main = ROOT / 'idf/esp32-cyd2usb-native/main'
    files = [main/'native_audio_output.c', main/'native_audio_output.h',
             ROOT/'tests/native/cyd_output_pause_test.c', Path(__file__).resolve(),
             ROOT/'tests/native/cyd_output_metrics_noop.h']
    for p in files:
        target = out/'sources'/p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(p.read_bytes())
    source = re.sub(r'^#include[^\n]*\n', '', files[0].read_text(), flags=re.M)
    variants = {'pdm': 'PDM', 'dac': 'DAC', 'legacy': 'LEGACY_DAC'}
    results, negative = {}, {}
    for name, define in variants.items():
        work = out/name
        work.mkdir()
        (work/'production.inc').write_text(source)
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-Wno-unused-function', '-Wno-unused-variable',
                   '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                   '-fno-pie', '-no-pie', '-DCONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_'+define+'=1',
                   '-I'+host(work), '-I'+host(ROOT/'tests/native'), host(files[2]), '-o', host(work/'test')]
        try:
            build = run(command)
        except subprocess.CalledProcessError as e:
            (work/'build.log').write_bytes(e.output)
            print(e.output.decode(errors='replace'), file=sys.stderr)
            raise
        (work/'build.log').write_bytes(build)
        log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1', host(work/'test')])
        (work/'test.log').write_bytes(log)
        results[name] = log.decode().strip()
        print(name+': '+results[name])
        if name in ('pdm', 'dac'):
            if name == 'pdm':
                old = 'if (result != ESP_OK) return first_error == ESP_OK ? result : first_error;'
                assert source.count(old) == 2
                broken = source.replace(old, '/* negative control: lose ownership on error */')
            else:
                old = 'ESP_RETURN_ON_ERROR(dac_continuous_disable(s_dac), TAG, "disable DAC");'
                assert source.count(old) == 1
                broken = source.replace(old, '(void)dac_continuous_disable(s_dac);')
            (work/'production.inc').write_text(broken)
            negative_command = command[:-1]+[host(work/'negative')]
            (work/'negative-build.log').write_bytes(run(negative_command))
            try:
                run(['env', 'ASAN_OPTIONS=detect_leaks=0:halt_on_error=1', host(work/'negative')])
            except subprocess.CalledProcessError as e:
                (work/'negative.log').write_bytes(e.output)
                expected = b"release: Assertion `h==&driver && driver.allocated && !driver.running' failed."
                if expected not in e.output or b'ERROR: AddressSanitizer' in e.output or b'runtime error:' in e.output:
                    raise AssertionError('unexpected negative failure: '+e.output.decode(errors='replace')) from e
                negative[name] = 'rejected by ownership assertion before deleting running DMA'
            else:
                raise AssertionError('negative control survived: '+name)
            (work/'production.inc').write_text(source)
    (out/'report.json').write_text(json.dumps(dict(
        passed=True, variants=results, negative_controls=negative,
        source_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        compiler=run(['gcc','--version']).decode().splitlines()[0], physical_dma=False), indent=2)+'\n')


if __name__ == '__main__':
    main()
