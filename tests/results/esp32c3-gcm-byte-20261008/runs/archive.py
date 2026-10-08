import hashlib
import json
from pathlib import Path
import re
import subprocess

root=Path('.build/c3-gcm-byte-20261008')
out=Path('tests/results/esp32c3-gcm-byte-20261008')
assert not out.exists()
summary=json.loads((root/'summary.json').read_text());assert summary['complete']
assert json.loads((root/'physical/final-board.json').read_text())['result']=='PASS'
assert json.loads((root/'host-final/report.json').read_text())['result']=='PASS'
assert json.loads((root/'verify-ghash.json').read_text())['result']=='PASS'
out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,target):
    target=out/target;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())

for p in root.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.ps1','.c','.h','.inc','.log','.json','.jsonl','.txt','.bin'):
        copy(p,Path('runs')/p.relative_to(root))
base='r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof'
image=Path('firmware/development/esp32c3-idf-6.1-'+base+'-ghash8')
manifest=json.loads((image/'manifest.json').read_text())
assert sha(image/'app.bin')==manifest['image']['sha256']
manifest['qualification']='NOT_QUALIFIED: exact GHASH host tests pass, but physical FLAC still has watchdog events and DMA overruns. Keep disabled.'
qualification=json.loads((image/'qualification.json').read_text())
qualification.update(physical_tests=True,evidence=out.as_posix(),report='docs/ESP32C3_GHASH_EXPERIMENT_20261008.md',
    flac_runtime='FAIL',aac_short_runtime='PASS',restoration='PASS',host_math='PASS',linked_dispatch='PASS')
for name,data in (('manifest.json',manifest),('qualification.json',qualification)):
    (image/name).write_bytes((json.dumps(data,indent=2)+'\n').encode())
for name in ('manifest.json','qualification.json','sdkconfig'):
    copy(image/name,Path('image')/name)
toolbin=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin')
sizes={}
for variant in (base,base+'-ghash8'):
    build=Path('idf/esp32c3-oled-native/build-idf-6.1-'+variant)
    elf=build/'yoradio_esp32c3_oled_native.elf'
    raw=subprocess.check_output([str(toolbin/'riscv32-esp-elf-size.exe'),'-A',str(elf)]).decode()
    sizes[variant]={m[1]:int(m[2]) for line in raw.splitlines() if (m:=re.match(r'(\.\S+)\s+(\d+)\s+\d+',line))}
    for p in build.rglob('*gcm*.su'):
        copy(p,Path('stack')/p.name)
(out/'elf-sizes.json').write_text(json.dumps(sizes,indent=2)+'\n')
wanted=set(manifest['source_overlay_sha256'].items())
for p in out.rglob('*.json'):
    data=json.loads(p.read_text())
    if isinstance(data,dict):
        wanted.update(data.get('test_sources_sha256',{}).items())
# host/ records carry their own source snapshots, including the first prototype.
for name in ('tools/esp32c3_tests/verify_gcm_byte_link.py','tools/esp32c3_tests/staged_dma.py',
             'tools/esp32c3_tests/summarize_radio_flac.py','tools/codec_benchmark/run_gcm_ghash_host.py',
             'tests/native/gcm_ghash_test.c'):
    wanted.add((name,sha(Path(name))))
source_index=[]
for name,expected in sorted(wanted):
    p=Path(name);assert sha(p)==expected,(name,expected)
    snapshot=Path('sources')/expected/p.name
    copy(p,snapshot);source_index.append(dict(path=name,sha256=expected,snapshot=snapshot.as_posix()))
(out/'source-index.json').write_text(json.dumps(source_index,indent=2)+'\n')
references=[]
for name in ('esp32c3-rxonly-long-20261008','esp32c3-staged-dma-profile-20261008'):
    p=Path('tests/results')/name/'index.json';references.append(dict(path=p.as_posix(),sha256=sha(p)))
(out/'baseline-references.json').write_text(json.dumps(references,indent=2)+'\n')
entries={p.relative_to(out).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size)
    for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(entries,indent=2)+'\n')
print('ARCHIVED',len(entries),sum(e['bytes'] for e in entries.values()),'bytes')
print('SIZES',json.dumps({k:{s:v for s,v in data.items() if s in ('.iram0.text','.dram0.data','.dram0.bss','.flash.text','.flash.rodata')} for k,data in sizes.items()}))
