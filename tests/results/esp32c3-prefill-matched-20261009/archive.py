"""Archive matched controls and every original physical result, excluding keys."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from summarize import PHASES

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST=REPO/'tests/results/esp32c3-prefill-matched-20261009'
assert not DEST.exists(),'Preserve prior evidence'
assert json.loads((ROOT/'verified.json').read_text())['result']=='PASS'
files={}
for name in ('physical.py','summarize.py','summary.json','verify_evidence.py','verified.json',
             'archive.py','replay.py','flow_windows.py','eof_replay.py','sources.json',
             'firmware-sources.json','case-catalog.json'):
    files[name]=ROOT/name
for folder in ('sources','firmware-sources','artifacts'):
    for p in (ROOT/folder).rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:files[p.relative_to(ROOT).as_posix()]=p
for phase in PHASES:
    for p in (ROOT/'physical'/phase).iterdir():
        if p.is_file() and p.suffix=='.json':files[p.relative_to(ROOT).as_posix()]=p
    for suffix in ('.log','-request-phases.jsonl','-transport-timing.json'):
        p=ROOT/'physical'/(phase+suffix)
        if p.is_file():files[p.relative_to(ROOT).as_posix()]=p
for p in (ROOT/'physical').glob('*.json'):
    if p.stem!='running':files[p.relative_to(ROOT).as_posix()]=p
build_root=REPO/'.build/c3-prefill-control-20261009'
for p in build_root.iterdir():
    if p.is_file() and p.suffix in ('.ps1','.py','.json','.log','.txt'):files['build-control/'+p.name]=p
build=REPO/'idf/esp32c3-oled-native/build-idf-6.1-r9a97-prefill-min0'
for p in (build/'log').iterdir():files['build-control/compiler-log/'+p.name]=p
files['build-control/host-prefill-report.json']=REPO/'tests/results/esp32c3-min-prefill-20261009/host-min-prefill/report.json'
files['stress-fixture-manifest.json']=REPO/'.build/c3-reserve-soak-20261008/fixtures/manifest.json'
for name in ('ca.pem','server.pem'):
    files['public-certificates/'+name]=REPO/'.build/c3-tls-records-20261007/trust'/name
blobs={name:path.read_bytes() for name,path in sorted(files.items())}
for name,blob in blobs.items():
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob),name
index=dict(scope='Exact EOF and matched-code FLAC A/B/A; prior failures are not superseded. No acoustic qualification.',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),files={})
for name,blob in blobs.items():
    target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
    index['files'][name]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(blobs),'files,',sum(map(len,blobs.values())),'bytes')
