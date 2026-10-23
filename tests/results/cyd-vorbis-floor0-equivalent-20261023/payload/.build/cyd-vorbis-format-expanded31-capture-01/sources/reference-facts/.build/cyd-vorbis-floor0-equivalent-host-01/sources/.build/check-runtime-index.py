import hashlib
import json
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[1]
prefix='tests/results/native-runtime-transfer-20261018/'
archive=root/prefix
manifest=json.loads((archive/'archive-manifest.json').read_text())
staged=subprocess.check_output(['git','ls-files','--stage','-z','--',prefix],cwd=root)
entries={}
for row in staged.split(b'\0'):
    if not row: continue
    info,name=row.split(b'\t',1)
    mode,oid,stage=info.split()
    assert stage==b'0'
    entries[name.decode()]=oid.decode()
files=list(manifest['files'])+['archive-manifest.json']
for relative in files:
    data=(archive/relative).read_bytes()
    oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert entries[prefix+relative]==oid,relative
assert len(entries)==len(files),(len(entries),len(files))
print('PASS',len(files),'staged raw Git blobs match archived bytes')
