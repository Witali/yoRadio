"""Verify evidence bytes in Git's index, and firmware LFS object identities."""
import gzip, hashlib, io, json, subprocess
from pathlib import Path
root=Path('tests/results/esp32c3-icy-rx-memory-20261007')
index=json.loads((root/'index.json').read_bytes())
entries=[(str(root/e['path']).replace('\\','/'),e) for e in index['files']]
entries.append((str(root/'index.json').replace('\\','/'),dict(stored_sha256=hashlib.sha256((root/'index.json').read_bytes()).hexdigest())))
for name in ('memory-control-profile','memory-rxcopy-profile','compact-icy-debug','compact-icy-quiet',
             'memory-icy-rxcopy-profile','memory-icy-rxcopy-quiet'):
    directory=Path('firmware/development/esp32c3-idf-6.1-'+name)
    manifest=json.loads((directory/'manifest.json').read_bytes())
    entries.append((str(directory/'app.bin').replace('\\','/'),dict(lfs_sha256=manifest['image']['sha256'])))
    for name in ('sdkconfig','manifest.json'):
        entries.append((str(directory/name).replace('\\','/'),dict(stored_sha256=hashlib.sha256((directory/name).read_bytes()).hexdigest())))
data=subprocess.check_output(['git','cat-file','--batch'],input=''.join(':'+p+'\n' for p,_ in entries).encode())
stream=io.BytesIO(data)
for path,expected in entries:
    header=stream.readline().split()
    assert len(header)==3 and header[1]==b'blob',(path,header)
    raw=stream.read(int(header[2]))
    assert stream.read(1)==b'\n'
    if 'lfs_sha256' in expected:
        assert ('oid sha256:'+expected['lfs_sha256']).encode() in raw,path
    else:
        assert hashlib.sha256(raw).hexdigest()==expected['stored_sha256'],path
        if 'raw_sha256' in expected:
            decoded=gzip.decompress(raw) if path.endswith('.gz') else raw
            assert hashlib.sha256(decoded).hexdigest()==expected['raw_sha256'],path
assert not stream.read()
print('Verified',len(entries),'staged evidence/config/LFS entries')
