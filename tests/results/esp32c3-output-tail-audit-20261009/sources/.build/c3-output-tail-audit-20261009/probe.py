"""Isolated baseline bug probe; no board access or production-source edits."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/codec_benchmark/run_output_dma_host.py').is_file())
sys.path.insert(0,str(REPO/'tools/codec_benchmark'))
from run_output_dma_host import source,host,run
MAIN=REPO/'idf/esp32c3-oled-native/main'
TEST=REPO/'tests/native/output_dma'
files=[MAIN/'native_audio_output.c',MAIN/'native_audio_output.h',
       MAIN/'native_i2s_generator.c',TEST/'stubs.h',MAIN/'audio_service.c',ROOT/'probe.c',Path(__file__)]
sources={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
for path in files:
    target=ROOT/'sources'/path.relative_to(REPO)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(path.read_bytes())
unit=ROOT/'unit.c'
unit.write_text('#include "stubs.h"\n'+source(MAIN/'native_audio_output.h')+
    '#define native_i2s_write_generated tested_i2s_write_generated\n'+
    '#define native_i2s_write_full_block tested_i2s_write_full_block\n'+
    source(MAIN/'native_i2s_generator.c')+
    '\n#undef native_i2s_write_generated\n#undef native_i2s_write_full_block\n'+
    source(MAIN/'native_audio_output.c')+'\n'+(ROOT/'probe.c').read_text())
binary=ROOT/'probe'
command=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Wno-unused-function',
         '-Wno-unused-variable','-fsanitize=address,undefined','-fno-omit-frame-pointer',
         '-fno-pie','-no-pie','-I'+host(TEST),host(unit),'-o',host(binary)]
(ROOT/'build.log').write_bytes(run(command))
result=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1',host(binary),host(ROOT/'probe.pcm')])
(ROOT/'result.log').write_bytes(result)
(ROOT/'report.json').write_text(json.dumps(dict(sources=sources,
    result='BUG REPRODUCED', scope='Real staged C functions under guarded host DMA, '
    'with EOF represented by its current no-output-work branch; not a full output_task test.',
    output=result.decode()),indent=2)+'\n')
print(result.decode())
