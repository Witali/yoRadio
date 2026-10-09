"""Exercise the real C3 rational resampler against independent integer math.

This verifies PCM counts and interpolation, not acoustic output or DMA timing.
Tone results quantify linear-interpolation loss and must not be described as
the AAC codec's compact-storage error.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from run_output_dma_host import ROOT, MAIN, TEST, host, run, source

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
files = [Path(__file__), ROOT/'tools/codec_benchmark/run_output_dma_host.py',
         TEST/'stubs.h', TEST/'integer_rate.c', MAIN/'native_audio_output.c',
         MAIN/'native_i2s_generator.c', MAIN/'native_audio_output.h']
hashes = {}
for path in files:
    name = path.relative_to(ROOT)
    hashes[name.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    dest = args.output/'sources'/name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(path.read_bytes())
def logged_run(name, command):
    try:
        log = run(command)
    except subprocess.CalledProcessError as error:
        (args.output/name).write_bytes(error.output)
        print(error.output.decode(errors='replace'))
        raise
    (args.output/name).write_bytes(log)
    return log


unit = args.output/'host_unit.c'
unit.write_text('#include "stubs.h"\n'
    '#define CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION 1\n'
    '#define CONFIG_YORADIO_STAGED_DMA_PROFILE 1\n'+source(MAIN/'native_audio_output.h')+
    '#define native_i2s_write_generated tested_i2s_write_generated\n'
    '#define native_i2s_write_full_block tested_i2s_write_full_block\n'+
    source(MAIN/'native_i2s_generator.c')+
    '\n#undef native_i2s_write_generated\n#undef native_i2s_write_full_block\n'+
    source(MAIN/'native_audio_output.c')+'\n#include "integer_rate.c"\n')
binary = args.output/'integer_rate'
logged_run('build.log', ['gcc','-std=c11','-O2','-g','-Wall','-Wextra',
    '-Wno-unused-function','-Wno-unused-variable','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+host(TEST),host(unit),'-o',host(binary),'-lm'])
log = logged_run('test.log', ['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
           'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
cases = [json.loads(line) for line in log.decode().splitlines()]
assert len(cases)==35
report = dict(sources=hashes, cases=cases, memory_sanitizers_passed=True,
              physical_tested=False, production_qualified=False, note=__doc__)
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(cases=len(cases), tones=[c for c in cases if c.get('tone_hz')],
    ten_minute_counts=[c for c in cases if c.get('seconds')]),indent=2))
