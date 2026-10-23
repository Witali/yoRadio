"""Verify saved MPI receipts, staged bytes and hydrated local LFS objects."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

root = Path.cwd()
sha = lambda data: hashlib.sha256(data).hexdigest()
git = lambda *args, **kw: subprocess.check_output(
    ['git', '-c', 'core.longpaths=true', *args], cwd=root, **kw)

def blobs(files):
    query = ''.join(':' + path.relative_to(root).as_posix() + '\n' for path in files)
    result = git('cat-file', '--batch', input=query.encode())
    offset = 0
    for path in files:
        end = result.index(b'\n', offset)
        header = result[offset:end].split()
        assert len(header) == 3 and header[1] == b'blob', (path, header)
        size = int(header[2])
        offset = end + 1
        data = result[offset:offset + size]
        offset += size + 1
        yield path, data
    assert offset == len(result)

sdk = json.loads((root / 'tests/results/cyd-early-mpi-sdk-20261020/SDK.json').read_bytes())
assert sdk['all_seven'] and len(sdk['images']) == 7
assert sdk['source_commit'] == '1190aebce400375c382a5ad54211e2400f98161d'
assert sdk['physical_tested'] is False and sdk['benefit_claimed'] is False
receipts = {row['variant']: row for row in sdk['images']}
folders = sorted((root / 'firmware/development').glob('esp32-cyd2usb-native-early-mpi-*'))
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
            objects.add(digest)
            pointer_count += 1
        else:
            assert raw == actual, path
            raw_count += 1
assert (raw_count, pointer_count, len(objects)) == (49, 14, 8)
print('PASS: seven MPI images; 49 raw metadata/logs, 14 staged LFS pointers, 8 hydrated objects')
