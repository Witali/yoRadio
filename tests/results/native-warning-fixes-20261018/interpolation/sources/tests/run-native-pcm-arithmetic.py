"""Check signed rounding in all native PDM interpolation implementations."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host, run
spec = importlib.util.spec_from_file_location('cyd_functions', ROOT/'tests/run-cyd-lifecycle.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    files = [ROOT/'idf/esp32c3-oled-native/main'/name for name in
             ('native_audio_output.c','native_audio_output_dma.c','native_audio_output_qemu.c')]
    cases = ROOT/'tests/native/pcm_interpolation_test.c'
    sources = [*files, cases, Path(__file__), ROOT/'tests/run-cyd-lifecycle.py']
    hashes = {}
    for file in sources:
        data = file.read_bytes(); relative = file.relative_to(ROOT)
        hashes[relative.as_posix()] = hashlib.sha256(data).hexdigest()
        destination = out/'sources'/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    results = {}
    for index, file in enumerate(files):
        directory = out/str(index); directory.mkdir(exist_ok=True)
        (directory/'interpolation.inc').write_text(helpers.function(file.read_text(encoding='utf-8'), 'interpolate_sample'), encoding='utf-8')
        binary = directory/'test'
        try:
            (directory/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-g','-Wall','-Wextra',
                '-Wconversion','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',
                '-fno-pie','-no-pie','-I'+host(directory),host(cases),'-o',host(binary)]))
            log = run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                       'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
        except subprocess.CalledProcessError as error:
            print(error.output.decode(errors='replace'),file=sys.stderr);raise
        (directory/'test.log').write_bytes(log)
        results[file.relative_to(ROOT).as_posix()] = log.decode().strip()
        print(file.relative_to(ROOT).as_posix()+': '+log.decode().strip())
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha for name,sha in hashes.items())
    (out/'report.json').write_text(json.dumps(dict(passed=True,physical_hardware=False,
        variants=results,source_sha256=hashes),indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
