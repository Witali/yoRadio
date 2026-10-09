"""Freeze quiet-build provenance without copying private configuration or keys."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST=REPO/'tests/results/esp32c3-quiet-min250-build-20261009'
ART=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-quiet-min250'
BUILD=REPO/'idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-min250'
assert not DEST.exists(), 'Preserve evidence'
manifest=json.loads((ART/'manifest.json').read_text())
audit=json.loads((ROOT/'build-audit.json').read_text())
assert audit['result']=='PASS' and audit['image']==manifest['image']
sha=lambda blob:hashlib.sha256(blob).hexdigest()
files={p.name:p for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.py','.ps1','.json','.log','.txt')}
for name in ('manifest.json','sdkconfig'):files['artifact/'+name]=ART/name
for name,digest in manifest['source_overlay_sha256'].items():
    path=REPO/name
    assert sha(path.read_bytes())==digest,name
    files['sources/'+name]=path
for name in ('tools/codec_benchmark/verify_aac_network_build.py',
             'tools/codec_benchmark/compact_sbr_tables.py',
             'tools/esp32c3_tests/verify_http_link.py',
             'tools/esp32c3_tests/verify_adaptive_input_link.py',
             'idf/esp32c3-oled-native/build.ps1',
             '.build/c3-idf-head-20261008/save-head.py'):
    files['sources/'+name]=REPO/name
for p in (BUILD/'log').iterdir():files['compiler-log/'+p.name]=p
for name in ('sdkconfig','manifest.json'):
    files['prior-quiet/'+name]=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-production-qio80'/name
blobs={name:p.read_bytes() for name,p in sorted(files.items())}
for name,blob in blobs.items():
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob),name
index=dict(scope='Build/link evidence only. No physical, network or acoustic qualification.',files={})
for name,blob in blobs.items():
    target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
    index['files'][name]=dict(bytes=len(blob),sha256=sha(blob))
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(blobs),'files,',sum(map(len,blobs.values())),'bytes')
