"""Preserve regression evidence, including adverse DMA findings, without keys."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from summarize import PHASES

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST=REPO/'tests/results/esp32c3-min-prefill-regression-20261009'
assert not DEST.exists(),'Preserve prior evidence'
assert json.loads((ROOT/'verified.json').read_text())['result']=='PASS'
files={}
for name in ('physical.py','summarize.py','summary.json','verify_evidence.py','verified.json',
             'archive.py','replay.py','flow_windows.py','short_summary.py','sources.json',
             'source-origins.json','case-catalog.json','production-config-differences.json',
             'compare_flac.py','flac-comparison.json'):
    files[name]=ROOT/name
for folder in ('sources','fixtures','fixture-manifests','control-flac'):
    for p in (ROOT/folder).rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:files[p.relative_to(ROOT).as_posix()]=p
for phase in PHASES:
    for p in (ROOT/'physical'/phase).iterdir():
        if p.is_file() and p.suffix=='.json':files[p.relative_to(ROOT).as_posix()]=p
    for suffix in ('.log','-request-phases.jsonl','-transport-timing.json'):
        p=ROOT/'physical'/(phase+suffix)
        if p.is_file():files[p.relative_to(ROOT).as_posix()]=p
for name in ('initial','installed','fractional-clock','phases','settings-after-tests','restoration',
             'controller-failure','restoration-failure'):
    p=ROOT/'physical'/(name+'.json')
    if p.is_file():files[p.relative_to(ROOT).as_posix()]=p
for name in ('sdkconfig','manifest.json'):
    files['candidate/'+name]=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250'/name
for name in ('ca.pem','server.pem'):
    files['public-certificates/'+name]=REPO/'.build/c3-tls-records-20261007/trust'/name
blobs={name:path.read_bytes() for name,path in sorted(files.items())}
for name,blob in blobs.items():
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob),name
index=dict(scope='Original format/memory/runtime gates and separate continuity review. No acoustic qualification.',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),files={})
for name,blob in blobs.items():
    target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
    index['files'][name]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(blobs),'files,',sum(map(len,blobs.values())),'bytes')
