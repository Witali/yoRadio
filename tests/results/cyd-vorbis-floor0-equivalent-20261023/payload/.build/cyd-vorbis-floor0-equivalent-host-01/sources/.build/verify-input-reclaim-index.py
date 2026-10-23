"""Verify raw staged evidence, all seven image receipts and actual LFS bytes."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

root = Path.cwd()
sha = lambda data: hashlib.sha256(data).hexdigest()
git = lambda *args, **kw: subprocess.check_output(['git', '-c', 'core.longpaths=true', *args], cwd=root, **kw)

def blobs(files):
    query = ''.join(':' + path.relative_to(root).as_posix() + '\n' for path in files)
    result = git('cat-file', '--batch', input=query.encode())
    offset = 0
    for path in files:
        end = result.index(b'\n', offset)
        header = result[offset:end].split()
        assert len(header) == 3 and header[1] == b'blob', (path, header)
        size = int(header[2]); offset = end + 1
        data = result[offset:offset + size]; offset += size + 1
        yield path, data
    assert offset == len(result)

for name in ('cyd-input-reclaim-20261020', 'cyd-input-reclaim-qemu-20261020',
             'cyd-vorbis-xtensa-audit-20261020', 'cyd-tls-reserve-mpi-audit-20261020'):
    folder = root / 'tests/results' / name
    manifest = json.loads((folder / 'manifest.json').read_text())
    files = sorted(path for path in folder.rglob('*') if path.is_file())
    assert {path.relative_to(folder).as_posix() for path in files} == set(manifest['files']) | {'manifest.json'}
    for relative, value in manifest['files'].items():
        raw = (folder / relative).read_bytes()
        assert sha(raw) == value['sha256'] and len(raw) == value['bytes']
    for path, raw in blobs(files):
        assert raw == path.read_bytes(), path
    print('Verified raw staged archive:', name, len(files), 'files', flush=True)

sdk = json.loads((root / 'tests/results/cyd-input-reclaim-20261020/SDK.json').read_text())
assert sdk['passed'] and len(sdk['images']) == 7
receipts = {row['variant']: row for row in sdk['images']}
folders = sorted((root / 'firmware/development').glob('esp32-cyd2usb-native-tls-input-reclaim-*'))
assert len(folders) == 7 and {folder.name for folder in folders} == set(receipts)
common = Path(git('rev-parse', '--git-common-dir').decode().strip())
if not common.is_absolute():
    common = (root / common).resolve()
raw_count = pointer_count = 0
objects = set()
for folder in folders:
    receipt_bytes = (folder / 'manifest.json').read_bytes()
    assert sha(receipt_bytes) == receipts[folder.name]['manifest_sha256']
    receipt = json.loads(receipt_bytes)
    assert receipt['build_check'] == 'PASS' and receipt['source_dirty'] is False
    assert receipt['source_commit'] == sdk['source_commit'] and receipt['physical_tested'] is False
    assert sha((folder / 'app.bin').read_bytes()) == receipts[folder.name]['app_sha256']
    for path, raw in blobs(sorted(path for path in folder.rglob('*') if path.is_file())):
        actual = path.read_bytes()
        if path.suffix == '.bin':
            match = re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n', raw)
            assert match, (path, 'LFS pointer required')
            digest = sha(actual)
            assert match[1].decode() == digest and int(match[2]) == len(actual)
            obj = common / 'lfs/objects' / digest[:2] / digest[2:4] / digest
            assert obj.read_bytes() == actual, obj
            objects.add(digest); pointer_count += 1
        else:
            assert raw == actual, path
            raw_count += 1
print('Verified seven saved images:', raw_count, 'raw metadata/logs,', pointer_count,
      'LFS pointers,', len(objects), 'actual LFS objects', flush=True)
