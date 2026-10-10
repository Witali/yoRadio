"""Check archived evidence in both working tree and Git without transformations."""
import hashlib,json,subprocess
from pathlib import Path
root=Path('tests/results/esp32c3-prefill1000-reneg-20261010')
index=json.loads((root/'index.json').read_text())
files=[root/relative for relative in index]+[root/'index.json']
for relative,expected in index.items():
    raw=(root/relative).read_bytes()
    assert dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())==expected,relative
queries=''.join('HEAD:'+p.as_posix()+'\n' for p in files).encode()
proc=subprocess.run(['git','cat-file','--batch'],input=queries,stdout=subprocess.PIPE,check=True)
data=proc.stdout;cursor=0
for path in files:
    end=data.index(b'\n',cursor);header=data[cursor:end].split();cursor=end+1
    assert header[1]==b'blob',(path,header)
    size=int(header[2]);raw=data[cursor:cursor+size];cursor+=size
    assert data[cursor:cursor+1]==b'\n';cursor+=1
    assert raw==path.read_bytes(),path
assert cursor==len(data)
print('Verified',len(files),'byte-exact committed files')

