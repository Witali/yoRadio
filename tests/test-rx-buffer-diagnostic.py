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
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from rx_ownership import analyze, fields
lines = log.decode().splitlines()
headers = [fields(line, 'PERF RX_OWNER2:') for line in lines if 'PERF RX_OWNER2:' in line]
assert any(h['live'] == 3 and h['payload'] == 5172 and h['metadata'] == 96 and not h['missing'] for h in headers)
assert any(h['payload'] == 0 and h['metadata'] == 32 and h['missing'] == 1 for h in headers)
# Recompute checksums in Python too, and validate the complete successful prefix.
prefix = lines[:next(i for i, line in enumerate(lines) if line.startswith('PERF RX_OWNER2: 3,'))]
owner = analyze([dict(at=i, line=line) for i, line in enumerate(prefix)])
assert owner['maximum_live'] == 3 and owner['maximum_allocated_payload_bytes'] == 5268
report = {'pass':True,'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in (source,harness,Path(__file__))},
          'scope':'Host ownership/range checks; target build checks RV32 stack bound; no physical timing inference'}
(folder / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(log.decode())
