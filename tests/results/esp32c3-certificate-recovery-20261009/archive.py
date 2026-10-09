"""Archive this capture and pin shared immutable evidence instead of duplicating sources."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parent
REPO=Path.cwd()
DEST=REPO/'tests/results/esp32c3-certificate-recovery-20261009'
assert not DEST.exists()
assert json.loads((ROOT/'summary.json').read_text())['result']=='PASS'
files={}
for name in ('prepare.py','physical.py','failure_monitor.py','capture-sockets.ps1','analyze.py',
             'summary.json','sources.json','case-catalog.json','sdk-error-codes.json','archive.py','replay.py'):
    files[name]=ROOT/name
for folder in ('physical','artifacts'):
    for path in (ROOT/folder).rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts and path.name!='running.json':
            files[path.relative_to(ROOT).as_posix()]=path
for name in ('ca.pem','server.pem'):
    files['public-certificates/'+name]=REPO/'.build/c3-tls-records-20261007/trust'/name
files['public-certificates/untrusted.pem']=REPO/'.build/c3-tls-final-gates-20261009/untrusted/cert.pem'
dependencies={}
for name in ('esp32c3-min250-tls-ota-20261009','esp32c3-reboot-tls-20261009'):
    path=REPO/'tests/results'/name/'index.json'
    dependencies[path.relative_to(REPO).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
index=dict(git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    scope='Original framing-to-rejection sequence plus full HE-AACv2 recovery; earlier failed campaign retained separately.',
    dependencies=dependencies,files={})
for name,path in sorted(files.items()):
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob),name
    target=DEST/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(blob)
    index['files'][name]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index['files']),'files;',sum(v['bytes'] for v in index['files'].values()),'bytes;',len(dependencies),'frozen dependencies')
