"""Freeze the unchanged sources used by the currently running controller."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parent
initial=json.loads((root/'physical/initial.json').read_text())
sources={}
for name,digest in initial['test_sources_sha256'].items():
    blob=Path(name).read_bytes()
    assert hashlib.sha256(blob).hexdigest()==digest,name
    sources[name]=digest
    path=root/'sources'/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(blob)
name='tests/test-reboot-tls-review.py'
blob=Path(name).read_bytes()
path=root/'sources'/name
path.parent.mkdir(parents=True,exist_ok=True)
path.write_bytes(blob)
sources[name]=hashlib.sha256(blob).hexdigest()
(root/'sources.json').write_text(json.dumps(sources,indent=2)+'\n')
artifacts=root/'artifacts'
artifacts.mkdir(exist_ok=True)
for name in ('manifest.json','sdkconfig'):
    (artifacts/name).write_bytes((Path('firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250')/name).read_bytes())
print('Frozen',len(sources),'sources with pre-test hash comparison')
