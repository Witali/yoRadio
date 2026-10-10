"""Archive original staged-flow observations and frozen measured source inputs."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST=REPO/'tests/results/esp32c3-min-prefill-20261009'
assert not DEST.exists(), 'Preserve previous evidence'
assert json.loads((ROOT/'verified.json').read_text())['result']=='PASS'
assert not (ROOT/'physical/restoration-failure.json').exists()
sources={}
for name,digest in json.loads((ROOT/'sources.json').read_text()).items():
    p=ROOT/'sources'/name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
    sources['sources/'+name]=p
for phase in ('profile-short','profile-long'):
    for name in ('report.json','status.json','performance.json'):
        sources[f'physical/{phase}/{name}']=ROOT/'physical'/phase/name
    for suffix in ('.log','-request-phases.jsonl','-transport-timing.json'):
        sources['physical/'+phase+suffix]=ROOT/'physical'/(phase+suffix)
for name in ('initial','installed-control','installed-profile','control-clock','profile-clock',
             'phases','settings-after-tests','restoration','controller-failure'):
    p=ROOT/'physical'/(name+'.json')
    if p.is_file():sources['physical/'+name+'.json']=p
for name in ('build.ps1','build.log','audit_build.py','build-audit.json','output-task-disassembly.txt',
             'verify-aac.json','verify-aac.json.log','verify-http.json','verify-http.json.log',
             'freeze_sources.py','sources.json',
             'physical.py','summarize.py','summary.json','compare.py','comparison.json',
             'verify_evidence.py','verified.json','archive.py','replay.py'):
    sources[name]=ROOT/name
for p in (ROOT/'host-min-prefill').rglob('*'):
    if p.is_file() and p.suffix in ('.py','.c','.h','.json','.log'):
        sources[p.relative_to(ROOT).as_posix()]=p
build=REPO/'idf/esp32c3-oled-native/build-idf-6.1-r9a97-prefill-min250'
for p in (build/'log').iterdir(): sources['build/compiler-log/'+p.name]=p
artifact=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250'
for name in ('sdkconfig','manifest.json'): sources['build/'+name]=artifact/name
trust=REPO/'.build/c3-tls-records-20261007/trust'
for name in ('ca.pem','server.pem'): sources['public-certificates/'+name]=trust/name
blobs={}
for name,path in sorted(sources.items()):
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob)
    blobs[name]=blob
index=dict(kind='Physical minimum-prefill continuity experiment',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    scope='Original verdicts, flow waits and DMA counters; private settings and keys excluded.',files={})
for name,blob in blobs.items():
    target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
    index['files'][name]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index['files']),'files,',sum(v['bytes'] for v in index['files'].values()),'bytes')
