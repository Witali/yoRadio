"""Test the exact SDK DAC write function with controlled completion interrupts."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'tests/target/cyd_full_app_openeth_qemu'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    spec = importlib.util.spec_from_file_location('dac_overlay', TARGET / 'prepare-dac-source.py')
    patch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patch)
    raw = (args.sdk / 'components/esp_driver_dac/dac_continuous.c').read_bytes()
    candidate = patch.overlay(raw, bound_stop_wait=True)
    original = raw.replace(b'\r\n', b'\n')
    control = original.replace(patch.SPIN, patch.WAIT, 1)
    output.mkdir(parents=True)
    for mode, source in (('candidate', candidate), ('old-order', control)):
        work = output / mode
        work.mkdir()
        (work / 'dac-write.inc').write_bytes(patch.WRITE + source.split(patch.WRITE, 1)[1])
        binary = work / 'test'
        try:
            build = run(['gcc', '-std=c11', '-O1', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                         '-Wno-pointer-to-int-cast', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-I' + host(work),
                         host(TARGET / 'dac-write-test.c'), '-o', host(binary)])
        except subprocess.CalledProcessError as error:
            (work / 'build.log').write_bytes(error.output)
            print(error.output.decode(errors='replace'), file=sys.stderr)
            raise
        (work / 'build.log').write_bytes(build)
        command = ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1', 'UBSAN_OPTIONS=halt_on_error=1', host(binary)]
        try:
            log = run(command)
        except subprocess.CalledProcessError as error:
            log = error.output
            if mode != 'old-order' or b"starts == 2 && written == 2 && !driver.is_running && !locked' failed" not in log:
                raise
        else:
            if mode != 'candidate' or b'PASS 5 synchronous DAC start/stop cases' not in log:
                raise RuntimeError(f'Unexpected {mode} result')
        (work / 'test.log').write_bytes(log)
        print(f'{mode}: {"passed" if mode == "candidate" else "rejected by early completion control"}')


if __name__ == '__main__':
    main()
