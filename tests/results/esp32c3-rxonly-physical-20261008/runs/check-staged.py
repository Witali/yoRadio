import hashlib
import json
import subprocess
from pathlib import Path

root = Path('tests/results/esp32c3-rxonly-physical-20261008')
entries = json.loads((root / 'index.json').read_text())
process = subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
def staged(path):
    process.stdin.write((':' + path.as_posix() + '\n').encode())
    process.stdin.flush()
    header = process.stdout.readline().split()
    assert len(header) == 3 and header[1] == b'blob', (path, header)
    data = process.stdout.read(int(header[2]))
    assert process.stdout.read(1) == b'\n'
    return data

for relative, expected in entries.items():
    data = staged(root / relative)
    assert len(data) == expected['bytes'], relative
    assert hashlib.sha256(data).hexdigest() == expected['sha256'], relative
for source in json.loads(staged(root / 'source-index.json')):
    assert hashlib.sha256(staged(root / source['snapshot'])).hexdigest() == source['sha256']
for variant in ('rxonly', 'output8'):
    folder = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-' + variant)
    manifest = json.loads(staged(folder / 'manifest.json'))
    assert hashlib.sha256(staged(folder / 'sdkconfig')).hexdigest() == manifest['sdkconfig_sha256']
    pointer = staged(folder / 'app.bin').decode()
    assert 'oid sha256:' + manifest['image']['sha256'] in pointer
    assert 'size ' + str(manifest['image']['bytes']) in pointer
process.stdin.close()
assert process.wait() == 0
print('STAGED_SHA256_PASS', len(entries), 'archive files, source snapshots and 2 image identities')
