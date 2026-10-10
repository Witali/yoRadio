import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path('.build/c3-tls-path-20261008')
out = Path('tests/results/esp32c3-tls-path-20261008')
assert not out.exists()
summary = json.loads((root/'summary.json').read_text())
assert summary['complete']
assert json.loads((root/'physical/final-board.json').read_text())['result'] == 'PASS'
assert json.loads((root/'physical-aac-repeat/final-board.json').read_text())['result'] == 'PASS'
for name in ('flac-tls-path.json', 'aac-repeat-tls-path.json'):
    assert all(c['coverage_complete'] for c in json.loads((root/name).read_text())['cases'])
for name in ('host/report.json', 'http-host/report.json', 'verify-path.json'):
    assert json.loads((root/name).read_text())['result'] == 'PASS'
out.mkdir(parents=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def copy(p, target):
    target = out/target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(p.read_bytes())

for p in root.rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py', '.ps1', '.c', '.h', '.log', '.json', '.jsonl', '.txt'):
        copy(p, Path('runs')/p.relative_to(root))

base = 'r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof'
image = Path('firmware/development/esp32c3-idf-6.1-'+base+'-tlspath')
manifest = json.loads((image/'manifest.json').read_text())
assert sha(image/'app.bin') == manifest['image']['sha256']
manifest['qualification'] = 'NOT_QUALIFIED: optional diagnostic instrumentation; consult retained heavy-case runtime and DMA results. No production default change.'
qualification = json.loads((image/'qualification.json').read_text())
qualification.update(physical_tests=True, evidence=out.as_posix(),
    report='docs/ESP32C3_TLS_PATH_PROFILE_20261008.md', restoration='PASS',
    host_wrapper_seams='PASS', linked_dispatch='PASS', original_acceptance_preserved=True)
for name, data in (('manifest.json', manifest), ('qualification.json', qualification)):
    (image/name).write_bytes((json.dumps(data, indent=2)+'\n').encode())
for name in ('manifest.json', 'qualification.json', 'sdkconfig'):
    copy(image/name, Path('image')/name)

toolbin = Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin')
sizes = {}
for variant in (base, base+'-tlspath'):
    elf = Path('idf/esp32c3-oled-native/build-idf-6.1-'+variant)/'yoradio_esp32c3_oled_native.elf'
    raw = subprocess.check_output([str(toolbin/'riscv32-esp-elf-size.exe'), '-A', str(elf)]).decode()
    sizes[variant] = {m[1]: int(m[2]) for line in raw.splitlines() if (m := re.match(r'(\.\S+)\s+(\d+)\s+\d+', line))}
(out/'elf-sizes.json').write_text(json.dumps(sizes, indent=2)+'\n')
wanted = set(manifest['source_overlay_sha256'].items())
for name in ('tools/esp32c3_tests/verify_tls_path_link.py', 'tools/esp32c3_tests/tls_path.py',
             'tools/esp32c3_tests/staged_dma.py', 'tools/esp32c3_tests/summarize_radio_flac.py',
             'tests/native/tls_path_profile_test.c', 'tests/test-tls-path-profile.py',
             'tests/test-tls-path-summary.py', 'tests/test-stream-http-reader.py',
             'tests/esp32c3-native-idf.test.js'):
    wanted.add((name, sha(Path(name))))
index = []
for name, expected in sorted(wanted):
    p = Path(name)
    assert sha(p) == expected, name
    target = Path('sources')/expected/p.name
    copy(p, target)
    index.append(dict(path=name, sha256=expected, snapshot=target.as_posix()))
(out/'source-index.json').write_text(json.dumps(index, indent=2)+'\n')
references = []
for name in ('esp32c3-rxonly-long-20261008', 'esp32c3-staged-dma-profile-20261008', 'esp32c3-gcm-byte-20261008'):
    p = Path('tests/results')/name/'index.json'
    references.append(dict(path=p.as_posix(), sha256=sha(p)))
(out/'baseline-references.json').write_text(json.dumps(references, indent=2)+'\n')
entries = {p.relative_to(out).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size)
           for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(entries, indent=2)+'\n')
print('ARCHIVED', len(entries), sum(e['bytes'] for e in entries.values()), 'bytes')
print('SIZES', json.dumps({k: {s: v for s, v in data.items() if s in
    ('.iram0.text', '.dram0.data', '.dram0.bss', '.flash.text', '.flash.rodata')} for k, data in sizes.items()}))
