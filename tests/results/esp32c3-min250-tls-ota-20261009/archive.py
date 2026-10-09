"""Preserve the aborted campaign and continuation without credentials or TLS keys."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from summarize import PHASES

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST=REPO/'tests/results/esp32c3-min250-tls-ota-20261009'
assert not DEST.exists(), 'Preserve previous evidence'
assert json.loads((ROOT/'verified.json').read_text())['result']=='PASS'
files={}
for name in ('physical.py','continue_physical.py','prepare.py','prepare_continuation.py',
             'failure_monitor.py','test_failure_monitor.py','capture-sockets.ps1',
             'preflight.py','preflight.json','host-sockets-after-10048.json','capture_sdk_codes.py',
             'summarize.py','summary.json','verify_evidence.py','verified.json','archive.py','replay.py','test_reset_review.py',
             'sources.json','case-catalog.json','flow_windows.py','eof_replay.py'):
    files[name]=ROOT/name
for folder in ('sources','artifacts'):
    for path in (ROOT/folder).rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts: files[path.relative_to(ROOT).as_posix()]=path
for capture in ('physical','continuation'):
    for path in (ROOT/capture).rglob('*'):
        if path.is_file() and path.suffix in ('.json','.jsonl','.log') and path.name!='running.json':
            files[path.relative_to(ROOT).as_posix()]=path
for path in (ROOT/'monitor-test').glob('*.json'):
    files['host-monitor-test/'+path.name]=path
for name in ('ca.pem','server.pem'):
    files['public-certificates/'+name]=REPO/'.build/c3-tls-records-20261007/trust'/name
files['public-certificates/untrusted.pem']=REPO/'.build/c3-tls-final-gates-20261009/untrusted/cert.pem'
if (ROOT/'sdk-error-codes.json').exists(): files['sdk-error-codes.json']=ROOT/'sdk-error-codes.json'
index=dict(scope='Original abort and failures retained alongside subsequent coverage; not a production qualification.',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),files={})
for name,path in sorted(files.items()):
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob),name
    target=DEST/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(blob)
    index['files'][name]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index['files']),'files,',sum(r['bytes'] for r in index['files'].values()),'bytes')
