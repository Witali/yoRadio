"""Exercise the actual heap owner probe with guarded allocator/task doubles."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host, run

folder=ROOT/'.build/heap-fragment/host'
folder.mkdir(parents=True,exist_ok=True)
source=ROOT/'idf/esp32c3-oled-native/main/heap_fragment_probe.c'
harness=ROOT/'tests/native/heap_fragment_probe_test.c'
unit=folder/'test.c'
code=re.sub(r'^#include[^\n]*\n','',source.read_text(),flags=re.M)
unit.write_text(harness.read_text().replace('/* PRODUCTION_SOURCE */',code))
binary=folder/'test'
(folder/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-pie','-no-pie',host(unit),'-o',host(binary)]))
log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
(folder/'run.log').write_bytes(log)
assert b'PASS arm/range/task/ISR/realloc-failure/in-place/moving/zero/free/reuse/overflow/unknown/snapshot/log-lock' in log
files=[source,harness,Path(__file__)]
for p in files:
    target=folder/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(p.read_bytes())
(folder/'report.json').write_text(json.dumps(dict(passed=True,
    source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
    scope='Actual probe with host allocator/task doubles; target stack/timing require physical build/tests'),indent=2)+'\n')
print(log.decode())
