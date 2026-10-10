"""Freeze matched FLAC input-capacity evidence, excluding keys and private state."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST=REPO/'tests/results/esp32c3-flac-input-growth-20261009'
assert not DEST.exists(),'Preserve original evidence'
assert json.loads((ROOT/'verified.json').read_text())['result']=='PASS'
files={}
for folder in ('sources','physical','artifacts','audit0','audit4'):
    for path in (ROOT/folder).rglob('*'):
        if path.is_file() and path.suffix not in ('.pyc','.bin') and path.name!='running.json':
            files[path.relative_to(ROOT).as_posix()]=path
for folder in ROOT.glob('host-*'):
    for path in folder.rglob('*'):
        if path.is_file() and path.suffix in ('.py','.c','.h','.json','.log'):
            files[path.relative_to(ROOT).as_posix()]=path
for path in ROOT.iterdir():
    if path.is_file() and path.suffix in ('.py','.ps1','.log','.json'):
        files[path.name]=path
for variant in ('0','4'):
    build=REPO/f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-input{variant}'
    for path in (build/'log').iterdir():
        if path.is_file():files[f'build{variant}/compiler-log/{path.name}']=path
for name in ('ca.pem','server.pem'):
    files['public-certificates/'+name]=REPO/'.build/c3-tls-records-20261007/trust'/name
index=dict(kind='Matched FLAC input-capacity experiment',
    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    scope='Original observations and failures; no private settings, keys or acoustic capture.',files={})
for name,path in sorted(files.items()):
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC |ENCRYPTED )?PRIVATE KEY-----',blob)
    target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
    index['files'][name]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index['files']),'files,',sum(v['bytes'] for v in index['files'].values()),'bytes')
