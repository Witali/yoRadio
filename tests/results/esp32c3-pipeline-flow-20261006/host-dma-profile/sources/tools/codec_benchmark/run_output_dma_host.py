"""Run actual staged/direct output C and the DMA writer with guarded host DMA.

Only platform #include lines are replaced by stubs. PCM arithmetic and driver
control flow are compiled unchanged. This is not physical DMA timing evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
MAIN=ROOT/'idf/esp32c3-oled-native/main'
TEST=ROOT/'tests/native/output_dma'

def host(path):
    path=Path(path).resolve().as_posix()
    return '/mnt/'+path[0].lower()+path[2:] if sys.platform=='win32' else path

def run(args):
    return subprocess.check_output((['wsl.exe','--exec'] if sys.platform=='win32' else [])+args,stderr=subprocess.STDOUT)

def source(path):
    return re.sub(r'^#include[^\n]*\n','',path.read_text(),flags=re.M)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--profile', action='store_true',
                        help='Also prove diagnostic DMA code preserves all PCM and ownership cases')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    report={'physical_dma':False,'variants':{}}
    files=[TEST/'stubs.h',TEST/'test.c',MAIN/'native_i2s_generator.c',
           MAIN/'native_audio_output.c',MAIN/'native_audio_output_dma.c',
           MAIN/'native_audio_output.h',MAIN/'native_i2s_generator.h',Path(__file__),
           TEST/'normalizer_chunks.cpp', ROOT/'yoRadio/src/audioI2S/AudioNormalizer.cpp',
           ROOT/'yoRadio/src/audioI2S/AudioNormalizer.h']
    if args.profile: files += [MAIN/'pipeline_wait.h']
    report['sources']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    # Freeze every source before executing either variant.
    for path in files:
        destination=args.output/'sources'/path.relative_to(ROOT)
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(path.read_bytes())
    variants = [('staged','native_audio_output.c'),('dma','native_audio_output_dma.c')]
    if args.profile: variants += [('dma-profile','native_audio_output_dma.c')]
    for name,filename in variants:
        unit=args.output/(name+'.c');binary=args.output/name
        unit.write_text('#include "stubs.h"\n'+
            '#define CONFIG_YORADIO_DIRECT_DMA_PCM 1\n'+source(MAIN/'native_audio_output.h')+
            ('#define CONFIG_YORADIO_PIPELINE_PROFILE 1\n'+source(MAIN/'pipeline_wait.h')
             if name == 'dma-profile' else '')+
            '#define native_i2s_write_generated tested_i2s_write_generated\n'+
            '#define native_i2s_write_full_block tested_i2s_write_full_block\n'+
            source(MAIN/'native_i2s_generator.c')+'\n#undef native_i2s_write_generated\n#undef native_i2s_write_full_block\n'+
            ('#define BASELINE 1\n' if name=='staged' else '')+
            source(MAIN/filename)+'\n#include "test.c"\n')
        cmd=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Wno-unused-function',
             '-Wno-unused-variable','-fsanitize=address,undefined','-fno-omit-frame-pointer',
             '-fno-pie','-no-pie','-I'+host(TEST),host(unit),'-o',host(binary)]
        (args.output/(name+'-build.log')).write_bytes(run(cmd))
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary),host(args.output/(name+'.pcm'))])
        (args.output/(name+'.log')).write_bytes(log)
        pcm=(args.output/(name+'.pcm')).read_bytes()
        report['variants'][name]={'pcm_bytes':len(pcm),'sha256':hashlib.sha256(pcm).hexdigest()}
    report['pcm_identical']=report['variants']['staged']==report['variants']['dma']
    report['case_metadata_identical']=(args.output/'staged.log').read_bytes()==(args.output/'dma.log').read_bytes()
    if args.profile:
        report['profile_pcm_identical'] = report['variants']['dma-profile'] == report['variants']['dma']
        report['profile_metadata_identical'] = (args.output/'dma-profile.log').read_bytes() == (args.output/'dma.log').read_bytes()
    normalizer=ROOT/'yoRadio/src/audioI2S'
    binary=args.output/'normalizer-chunks'
    (args.output/'normalizer-build.log').write_bytes(run([
        'g++','-std=c++14','-O2','-fsanitize=address,undefined','-fno-pie','-no-pie',
        '-I'+host(normalizer),host(TEST/'normalizer_chunks.cpp'),
        host(normalizer/'AudioNormalizer.cpp'),'-o',host(binary)]))
    result=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
    (args.output/'normalizer.log').write_bytes(result)
    report['normalizer']=result.decode().strip()
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if all(report.get(key, True) for key in ('pcm_identical', 'case_metadata_identical',
                 'profile_pcm_identical', 'profile_metadata_identical')) else 1

if __name__=='__main__':sys.exit(main())
