import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
folder = root / 'tests/results/cyd-network-settings-20261020'
manifest = folder / 'manifest.json'
entries = {path.relative_to(folder).as_posix(): {
    'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
    for path in sorted(folder.rglob('*')) if path.is_file() and path != manifest}
if manifest.exists():
    previous = json.loads(manifest.read_text(encoding='utf-8'))
    assert all(entries[name] == value for name, value in previous.items()), 'Previously archived evidence changed'
manifest.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
print('Manifest covers', len(entries), 'raw files')
