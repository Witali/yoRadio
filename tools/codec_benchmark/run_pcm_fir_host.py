"""Validate actual C3 FIR output against a double-precision independent oracle."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from run_output_dma_host import ROOT, MAIN, TEST, host, run, source

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
files=[Path(__file__),ROOT/'tools/codec_benchmark/run_output_dma_host.py',
       ROOT/'tools/codec_benchmark/generate_pcm_fir.py',ROOT/'tools/codec_benchmark/compare_integer_rate_filters.py',
       MAIN/'native_audio_output.c',MAIN/'native_audio_output.h',MAIN/'native_i2s_generator.c',
       MAIN/'native_pcm_fir.h',MAIN/'native_pcm_fir_coefficients.h',
       TEST/'stubs.h',TEST/'boundaries.c',TEST/'fir_quality.c']
hashes={}
for path in files:
    name=path.relative_to(ROOT);hashes[name.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    dest=args.output/'sources'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
reports={}
for name in ('fir_quality','boundaries'):
    unit=args.output/(name+'_host.c');binary=args.output/name
    unit.write_text('#include "stubs.h"\n#include "native_pcm_fir.h"\n'
        '#define CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION 1\n'
        '#define CONFIG_YORADIO_PDM_INTEGER_FIR 1\n#define BASELINE 1\n'+source(MAIN/'native_audio_output.h')+
        '#define native_i2s_write_generated tested_i2s_write_generated\n'
        '#define native_i2s_write_full_block tested_i2s_write_full_block\n'+source(MAIN/'native_i2s_generator.c')+
        '\n#undef native_i2s_write_generated\n#undef native_i2s_write_full_block\n'+source(MAIN/'native_audio_output.c')+
        '\n'+(TEST/(name+'.c')).read_text())
    command=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Wno-unused-function','-Wno-unused-variable',
             '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
             '-I'+host(TEST),'-I'+host(MAIN),host(unit),'-o',host(binary),'-lm']
    try:
        (args.output/(name+'-build.log')).write_bytes(run(command))
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),host(args.output/'boundary.pcm')])
        (args.output/(name+'.log')).write_bytes(log)
    except subprocess.CalledProcessError as error:
        (args.output/(name+'-failure.log')).write_bytes(error.output);print(error.output.decode(errors='replace'));raise
    reports[name]=[json.loads(line) for line in log.decode().splitlines()] if name=='fir_quality' else log.decode()
assert len(reports['fir_quality'])==122
report=dict(sources=hashes,results=reports,physical_tested=False,sanitizers_passed=True)
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(cases=len(reports['fir_quality']),boundaries=reports['boundaries'],
    max_lsb=max(r['max_reference_lsb'] for r in reports['fir_quality']),
    tones=[r for r in reports['fir_quality'] if r['tone']]),indent=2))
