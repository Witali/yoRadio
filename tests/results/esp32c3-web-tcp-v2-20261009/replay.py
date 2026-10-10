"""Verify captured bytes, saved image/config identity and TCP replay without a board."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
output=a.output.resolve()
assert not output.is_relative_to(ROOT),'Preserve frozen evidence'
output.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=json.loads((ROOT/'index.json').read_text())
for name,expected in index['files'].items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    assert path.stat().st_size==expected['bytes'] and sha(path)==expected['sha256'],name
artifact=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-web-tcp-v2'
manifest=json.loads((artifact/'manifest.json').read_text())
audit=json.loads((ROOT/'build-audit.json').read_text())
assert audit['result']=='PASS' and audit['image']==manifest['image']
assert sha(artifact/'app.bin')==audit['image']['sha256']
assert (artifact/'app.bin').read_bytes()[176:208].hex()==audit['image']['app_elf_sha256']
assert sha(artifact/'sdkconfig')==manifest['sdkconfig_sha256']
assert sha(artifact/'bootloader.bin')==manifest['bootloader_sha256']
for name,digest in manifest['source_overlay_sha256'].items():
    assert sha(ROOT/'sources'/name)==digest,name
for name,digest in json.loads((ROOT/'physical/initial.json').read_text())['test_sources_sha256'].items():
    assert sha(ROOT/'sources'/name)==digest,name
restored=json.loads((ROOT/'physical/restoration.json').read_text())
initial=json.loads((ROOT/'physical/initial.json').read_text())
assert restored['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']
assert all(restored['persistence'].values())
assert len(restored['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restored['states'])
with (output/'review.log').open('xb') as log:
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'review.py'),'--output',str(output/'review.json')],
                   stdout=log,stderr=subprocess.STDOUT,check=True)
assert json.loads((output/'review.json').read_text())==json.loads((ROOT/'review.json').read_text())
print('PASS:',len(index['files']),'byte-exact files; image/config/sources, restoration and TCP evidence reproduced')
