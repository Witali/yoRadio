"""Verify build/host evidence; no claim of physical or production acceptance."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=json.loads((ROOT/'index.json').read_text())['files']
for name,expected in index.items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    assert path.stat().st_size==expected['bytes'] and sha(path)==expected['sha256'],name
art=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-fir32'
m=json.loads((art/'manifest.json').read_text())
for filename,digest in [('app.bin',m['image']['sha256']),('bootloader.bin',m['bootloader_sha256']),('sdkconfig',m['sdkconfig_sha256'])]:
    assert sha(art/filename)==digest,filename
assert (art/'app.bin').read_bytes()[176:208].hex()==m['image']['app_elf_sha256']
for name,digest in m['source_overlay_sha256'].items():assert sha(ROOT/'build-sources'/name)==digest,name
for folder in ('host','default-regression','default-boundaries'):
    report=json.loads((ROOT/folder/'report.json').read_text())
    for name,digest in report['sources'].items():assert sha(ROOT/folder/'sources'/name)==digest,name
assert json.loads((ROOT/'build-audit.json').read_text())['result']=='PASS'
assert not m['production_qualified']
print('PASS:',len(index),'byte-exact files, artifact and source identities; physical qualification remains separate')
