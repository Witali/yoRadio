"""Append the independent read-only seven-image review without rewriting evidence."""
from pathlib import Path
import hashlib
import json

root = Path.cwd()
base = root / 'tests/results/cyd-input-reclaim-20261020'
origin = root / '.build/cyd-input-reclaim-sdk-final-review-01'
target = base / 'appendix-tools/cyd-input-reclaim-sdk-final-review-01'
digest = lambda data: hashlib.sha256(data).hexdigest()
report = json.loads((origin / 'review.json').read_text())
assert digest((origin / 'review.json').read_bytes()) == '5c6a0069f15890267371da4538ca5b6cbdf9cd0e758b077ffe725b410e30a74c'
manifest_path = base / 'manifest.json'
manifest = json.loads(manifest_path.read_text())
old_records = dict(manifest['files'])
for name, value in old_records.items():
    data = (base / name).read_bytes()
    assert len(data) == value['bytes'] and digest(data) == value['sha256']
target.mkdir(parents=True, exist_ok=True)
mappings = {}
for path in sorted(origin.rglob('*')):
    if not path.is_file():
        continue
    data = path.read_bytes()
    name = path.relative_to(origin).as_posix()
    if path.suffix in ('.bin', '.elf') or data.startswith((b'\x7fELF', b'MZ')):
        mappings[name] = {'status': 'omitted_binary', 'bytes': len(data), 'sha256': digest(data)}
        continue
    dest = target / path.relative_to(origin)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    mappings[name] = {'status': 'archived', 'path': dest.relative_to(base).as_posix(), 'bytes': len(data), 'sha256': digest(data)}
    manifest['files'][dest.relative_to(base).as_posix()] = {'bytes': len(data), 'sha256': digest(data)}
note = target / 'ARCHIVE_SCOPE.md'
note.write_text('This is the raw independent read-only seven-image review. Review reports, inputs and source snapshots retain their original bytes. Its nested manifest describes the original ignored capture, including binaries that are deliberately omitted here; archive-map.json records every original file and its disposition. The surrounding archive manifest covers every retained file. ELF and binary identities alone cannot reproduce the original artifact review. Application and partition binaries are saved separately under firmware/development with LFS; ELF files remain in the ignored original build/review directories. No build or runtime test is performed by this packaging step.\n', encoding='utf-8')
mapping_file = target / 'archive-map.json'
mapping_file.write_text(json.dumps(mappings, indent=2, sort_keys=True) + '\n', encoding='utf-8')
for path in (note, mapping_file):
    data = path.read_bytes()
    manifest['files'][path.relative_to(base).as_posix()] = {'bytes': len(data), 'sha256': digest(data)}
for path in target.rglob('*'):
    if path.is_file():
        assert path.relative_to(base).as_posix() in manifest['files']
assert all(manifest['files'][name] == value for name, value in old_records.items())
manifest['file_count'] = len(manifest['files'])
manifest['indexed_bytes'] = sum(value['bytes'] for value in manifest['files'].values())
manifest['sdk_appendix']['independent_actual_review_sha256'] = digest((origin / 'review.json').read_bytes())
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print('Appended independent review; indexed files:', manifest['file_count'])
