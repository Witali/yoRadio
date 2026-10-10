"""Freeze completed reboot controls, excluding private settings and TLS keys."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parent
REPO=Path.cwd()
DEST=REPO/'tests/results/esp32c3-reboot-tls-20261009'
assert not DEST.exists()
assert json.loads((ROOT/'summary.json').read_text())['result']=='PASS'
files={}
for name in ('prepare.py','physical.py','freeze.py','prepare_evidence.py','summarize.py',
             'summary.json','sources.json','fixture.json','sdk-shutdown-review.json','archive.py','replay.py'):
    files[name]=ROOT/name
for folder in ('physical','sources','artifacts','application-sources'):
    for path in (ROOT/folder).rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts and path.name!='running.json':
            files[path.relative_to(ROOT).as_posix()]=path
for name in ('ca.pem','server.pem'):
    files['public-certificates/'+name]=REPO/'.build/c3-tls-records-20261007/trust'/name
index=dict(git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    scope='Three active and three stopped TLS-stream reboot controls, with all errors retained.',files={})
for name,path in sorted(files.items()):
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob)
    target=DEST/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(blob)
    index['files'][name]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index['files']),'files;',sum(v['bytes'] for v in index['files'].values()),'bytes')
