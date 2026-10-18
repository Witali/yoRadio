"""Qualify C3 staged/direct maintenance quiet ownership with production DMA writer."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run,source


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32c3-oled-native/main';test=ROOT/'tests/native/output_dma'
    files=[Path(__file__).resolve(),ROOT/'tests/native/c3_output_pause_test.c',test/'stubs.h',test/'test.c',
           *[main/n for n in ('native_audio_output.c','native_audio_output_dma.c','native_audio_output.h','native_i2s_generator.c')]]
    for f in files:
        saved=out/'sources'/f.relative_to(ROOT);saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(f.read_bytes())
    driver='''#define i2s_channel_disable original_disable
#define i2s_del_channel original_delete
#include "stubs.h"
#undef i2s_channel_disable
#undef i2s_del_channel
static bool fail_pause_disable,fail_pause_delete;
static int i2s_channel_disable(i2s_chan_handle_t h) {return fail_pause_disable ? ESP_FAIL:original_disable(h);}
static int i2s_del_channel(i2s_chan_handle_t h) {return fail_pause_delete ? ESP_FAIL:original_delete(h);}
'''
    results={};mutants={}
    for name,file in [('staged','native_audio_output.c'),('direct','native_audio_output_dma.c')]:
        common=driver+('#define BASELINE 1\n' if name=='staged' else '#define CONFIG_YORADIO_DIRECT_DMA_PCM 1\n')+source(main/'native_audio_output.h').replace('#pragma once','')
        common+='#define native_i2s_write_generated tested_i2s_write_generated\n#define native_i2s_write_full_block tested_i2s_write_full_block\n'+source(main/'native_i2s_generator.c')+'\n#undef native_i2s_write_generated\n#undef native_i2s_write_full_block\n'
        suffix=(test/'test.c').read_text().split('int main(',1)[0]+files[1].read_text()
        body=source(main/file);unit=out/(name+'.c');binary=out/name
        command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+host(test),host(unit),'-o',host(binary)]
        def build(text,tag):
            unit.write_text(common+text+suffix)
            try:(out/(tag+'-build.log')).write_bytes(run(command))
            except subprocess.CalledProcessError as e:
                (out/(tag+'-build.log')).write_bytes(e.output);print(e.output.decode(errors='replace'),file=sys.stderr);raise
        build(body,name)
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
        (out/(name+'.log')).write_bytes(log);results[name]=log.decode().strip();print(name+': '+results[name])
        old='ESP_RETURN_ON_ERROR(i2s_channel_disable(s_pdm), TAG, "pause PDM");'
        assert body.count(old)==1
        build(body.replace(old,'(void)i2s_channel_disable(s_pdm);'),name+'-negative')
        try:run(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
        except subprocess.CalledProcessError as e:
            (out/(name+'-negative.log')).write_bytes(e.output)
            if b'Assertion `' not in e.output or b'native_audio_output_pause()!=ESP_OK' not in e.output or b'ERROR: AddressSanitizer' in e.output or b'runtime error:' in e.output:
                raise AssertionError('unexpected negative runtime failure') from e
            mutants[name]='semantic ownership assertion'
        else:raise AssertionError('negative control survived '+name)
        build(body,name+'-restored')
    (out/'report.json').write_text(json.dumps(dict(passed=True,variants=results,negative_controls=mutants,physical_dma=False,
        source_sha256={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}),indent=2)+'\n')


if __name__=='__main__':main()
