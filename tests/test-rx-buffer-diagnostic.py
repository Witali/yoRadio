"""Compile actual RX ownership code with bounded heap/netif test doubles."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run

folder = ROOT / '.build/codec-owner/host'
folder.mkdir(parents=True, exist_ok=True)
source = ROOT / 'idf/esp32c3-oled-native/main/rx_buffer_diagnostic.c'
harness = ROOT / 'tests/native/rx_buffer_diagnostic_test.c'
code = re.sub(r'^#include[^\n]*\n', '', source.read_text(), flags=re.M)
unit = folder / 'test.c'
unit.write_text(harness.read_text().replace('/* PRODUCTION_SOURCE */', code))
binary = folder / 'test'
build = run(['gcc','-std=c11','-O2','-Wall','-Wextra','-fsanitize=address,undefined',
             '-fno-pie','-no-pie',host(unit),'-o',host(binary)])
(folder / 'build.log').write_bytes(build)
log = run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
           'UBSAN_OPTIONS=halt_on_error=1',host(binary)])
(folder / 'run.log').write_bytes(log)
assert b'live=3 peak=3 allocs=3 frees=0 lost=0 unmatched=0 payload=5172 metadata=96 missing=0' in log
assert b'payload=0 metadata=32 missing=1' in log
report = {'pass':True,'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in (source,harness,Path(__file__))},
          'scope':'Host ownership/range checks; target build checks RV32 stack bound; no physical timing inference'}
(folder / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(log.decode())
