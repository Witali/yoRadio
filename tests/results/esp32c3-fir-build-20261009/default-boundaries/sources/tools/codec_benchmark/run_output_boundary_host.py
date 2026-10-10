"""Test real PCM flush/discard functions using guarded host DMA, not hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from run_output_dma_host import host,run,source

ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
TEST=ROOT/'tests/native/output_dma'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
files=[MAIN/n for n in ('native_audio_output.c','native_audio_output_dma.c',
    'native_audio_output.h','native_i2s_generator.c','pipeline_wait.h')]
files += [TEST/'stubs.h',TEST/'boundaries.c',Path(__file__)]
report=dict(physical_dma=False,variants={},sources={})
for path in files:
    name=path.relative_to(ROOT).as_posix()
    report['sources'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    dest=args.output/'sources'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(path.read_bytes())
for mode,filename in [('staged','native_audio_output.c'),('dma','native_audio_output_dma.c')]:
    binary=args.output/mode;unit=args.output/(mode+'.c')
    unit.write_text('#include "stubs.h"\n'+
        ('#define CONFIG_YORADIO_DIRECT_DMA_PCM 1\n' if mode=='dma' else '#define BASELINE 1\n')+
        source(MAIN/'native_audio_output.h')+
        '#define native_i2s_write_generated tested_i2s_write_generated\n'+
        '#define native_i2s_write_full_block tested_i2s_write_full_block\n'+
        source(MAIN/'native_i2s_generator.c')+
        '\n#undef native_i2s_write_generated\n#undef native_i2s_write_full_block\n'+
        source(MAIN/filename)+'\n'+(TEST/'boundaries.c').read_text())
    command=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Wno-unused-function',
             '-Wno-unused-variable','-fsanitize=address,undefined','-fno-omit-frame-pointer',
             '-fno-pie','-no-pie','-I'+host(TEST),host(unit),'-o',host(binary)]
    try:
        (args.output/(mode+'-build.log')).write_bytes(run(command))
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary),host(args.output/(mode+'.pcm'))])
        (args.output/(mode+'.log')).write_bytes(log)
    except subprocess.CalledProcessError as error:
        (args.output/(mode+'-failure.log')).write_bytes(error.output)
        print(error.output.decode(errors='replace'));raise
    pcm=(args.output/(mode+'.pcm')).read_bytes()
    report['variants'][mode]=dict(log=log.decode(),pcm_sha256=hashlib.sha256(pcm).hexdigest(),bytes=len(pcm))
report['pcm_identical']=report['variants']['staged']['pcm_sha256']==report['variants']['dma']['pcm_sha256']
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));assert report['pcm_identical']
