"""Execute actual output_task control flow with deterministic queue/output stubs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run,source
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
production=ROOT/'idf/esp32c3-oled-native/main/audio_service.c'
header=production.with_name('native_audio_output.h')
harness=ROOT/'tests/native/output_task_boundaries.c'
text=production.read_text()
def function(name):
    begin=text.index('static void '+name+'(')
    end=text.index('\n}',begin)+2
    return text[begin:end]
packet=re.search(r'typedef struct \{\n    uint32_t generation;\n    uint32_t sample_rate;.*?} pcm_packet_t;',text,re.S).group()
unit=args.output/'test.c'
unit.write_text(harness.read_text().replace('/* PRODUCTION_OUTPUT_HEADER */',source(header).replace('#pragma once',''))
    .replace('/* PRODUCTION_PACKET_TYPE */',packet)
    .replace('/* PRODUCTION_FINISH */',function('finish_pcm_stream'))
    .replace('/* PRODUCTION_RELEASE */','#ifdef CONFIG_YORADIO_DIRECT_DMA_PCM\n'+function('release_pcm_lease')+'\n#endif')
    .replace('/* PRODUCTION_OUTPUT_TASK */',function('output_task')))
report=dict(scope='Actual output_task with queue and output spies; no physical timing or PCM arithmetic',variants={},sources={})
for path in (production,header,harness,Path(__file__)):
    name=path.relative_to(ROOT).as_posix();report['sources'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    dest=args.output/'sources'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
for mode in ('staged','direct'):
    binary=args.output/mode
    command=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
        '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
    if mode=='direct': command+=['-DCONFIG_YORADIO_DIRECT_DMA_PCM=1']
    try:
        (args.output/(mode+'-build.log')).write_bytes(run(command+[host(unit),'-o',host(binary)]))
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                 'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
        (args.output/(mode+'.log')).write_bytes(log)
    except subprocess.CalledProcessError as error:
        (args.output/(mode+'-failure.log')).write_bytes(error.output)
        print(error.output.decode(errors='replace'));raise
    report['variants'][mode]=dict(result='PASS',cases=10,log=log.decode())
(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
