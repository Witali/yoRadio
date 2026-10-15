"""Test the production generic decoder loop with deterministic decoder stubs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import re

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'.build/codec-segment-drain')
out=parser.parse_args().output
out.mkdir(parents=True,exist_ok=True)
main=ROOT/'idf/esp32c3-oled-native/main'
source=main/'audio_service.c'
harness=ROOT/'tests/native/codec_segment_drain_test.c'
text=source.read_text()
start=text.index('static void return_decoded_packet(')
end=text.index('\nstatic void finish_pcm_stream(',start)
returned=text[start:end]
start=text.index('        if (!decoder && !aac_decoder) {',text.index('static void decoder_task('))
end=text.index('\n    }\n}',start)
unit=out/'test.c'
failure_header=main/'cpu_profiler.h'
failure_enum=re.search(r'typedef enum \{.*?} decoder_failure_stage_t;',failure_header.read_text(),re.S).group()
probe_header=main/'audio_pipeline_probe.h'
probe=re.sub(r'^#(?:include|pragma)[^\n]*\n','',probe_header.read_text(),flags=re.M)
unit.write_text(probe+'\n'+harness.read_text().replace('/* PRODUCTION_RETURN */',returned)
               .replace('/* PRODUCTION_DECODE */',text[start:end])
               .replace('/* FAILURE_DECLARATIONS */',failure_enum))
binary=out/'test'
(out/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-pie','-no-pie','-I',host(main),host(unit),'-o',host(binary)]))
log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
         'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
(out/'run.log').write_bytes(log)
paths=[source,main/'audio_completion.h',failure_header,probe_header,harness,Path(__file__).resolve()]
(out/'report.json').write_text(json.dumps(dict(passed=True,cases=30,
    source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    scope='Actual decoder loop and completion routing; deterministic SDK/native-AAC stubs, not real DSP or timing'),indent=2)+'\n')
print(log.decode(),end='')
