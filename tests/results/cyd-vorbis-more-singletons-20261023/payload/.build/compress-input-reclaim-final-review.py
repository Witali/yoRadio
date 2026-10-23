"""Losslessly store large captured build descriptions without duplicating raw text."""
from pathlib import Path
import gzip
import hashlib
import json

base = Path.cwd() / 'tests/results/cyd-input-reclaim-20261020'
folder = base / 'appendix-tools/cyd-input-reclaim-sdk-final-review-01'
map_path = folder / 'archive-map.json'
manifest_path = base / 'manifest.json'
mapping = json.loads(map_path.read_text())
manifest = json.loads(manifest_path.read_text())
digest = lambda data: hashlib.sha256(data).hexdigest()
count = 0
for name, row in mapping.items():
    if row['status'] != 'archived' or row['bytes'] < 1_000_000:
        continue
    source = base / row['path']
    assert source.resolve().is_relative_to(folder.resolve())
    assert source.name in ('build.ninja', 'compile_commands.json')
    data = source.read_bytes()
    assert digest(data) == row['sha256'] and len(data) == row['bytes']
    packed = gzip.compress(data, compresslevel=9, mtime=0)
    assert gzip.decompress(packed) == data
    dest = source.with_name(source.name + '.gz')
    assert not dest.exists()
    dest.write_bytes(packed)
    source.unlink()
    del manifest['files'][row['path']]
    row.update(status='lossless_gzip', path=dest.relative_to(base).as_posix(), stored_bytes=len(packed), stored_sha256=digest(packed))
    manifest['files'][row['path']] = {'bytes': len(packed), 'sha256': digest(packed)}
    count += 1
scope = folder / 'ARCHIVE_SCOPE.md'
scope.write_text(scope.read_text() + '\nLarge build.ninja and compile_commands.json inputs are losslessly gzip encoded. archive-map.json records both their decoded original identities and stored identities. Decompression recovers the exact captured bytes.\n', encoding='utf-8')
map_path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + '\n', encoding='utf-8')
for path in (map_path, scope):
    data = path.read_bytes()
    manifest['files'][path.relative_to(base).as_posix()] = {'bytes': len(data), 'sha256': digest(data)}
manifest['file_count'] = len(manifest['files'])
manifest['indexed_bytes'] = sum(row['bytes'] for row in manifest['files'].values())
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print('Losslessly compressed', count, 'large build descriptions')
