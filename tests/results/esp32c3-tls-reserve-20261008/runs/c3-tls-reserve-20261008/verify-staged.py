import hashlib, json, subprocess
from pathlib import Path

root = Path('tests/results/esp32c3-tls-reserve-20261008')
index = json.loads((root/'index.json').read_text())
paths = [root/name for name in index] + [root/'index.json']
for name, expected in index.items():
    data = (root/name).read_bytes()
    assert len(data) == expected['bytes']
    assert hashlib.sha256(data).hexdigest() == expected['sha256'], name
images = json.loads((root/'images.json').read_text())
paths += [Path('firmware/development')/name/'app.bin' for name in images]
process = subprocess.run(['git','cat-file','--batch'], check=True,
                         input=''.join(':'+p.as_posix()+'\n' for p in paths).encode(),
                         stdout=subprocess.PIPE)
output, at = process.stdout, 0
for path in paths:
    end = output.index(b'\n', at)
    header = output[at:end].split()
    assert len(header) == 3 and header[1] == b'blob', (path, header)
    size = int(header[2]); data = output[end+1:end+1+size]
    at = end+size+2
    if path.name == 'app.bin':
        expected = images[path.parent.name]
        actual = path.read_bytes()
        assert len(actual) == expected['bytes']
        assert hashlib.sha256(actual).hexdigest() == expected['app_sha256']
        assert ('oid sha256:'+expected['app_sha256']).encode() in data
        assert ('size '+str(expected['bytes'])).encode() in data
    else:
        assert data == path.read_bytes(), path
assert at == len(output)
print('VERIFIED',len(index)+1,'exact staged archive blobs and',len(images),'LFS image identities')
