"""Preserve experiment evidence byte-for-byte after replay and restoration."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = Path('tests/results/esp32c3-prefill1000-quiet-20261010')
assert not (DEST / 'index.json').exists(), 'Preserve completed archives'
assert json.loads((ROOT / 'review.json').read_text())['exact_listened_image_restored']
allowed = {'.py', '.json', '.jsonl', '.log', '.md', '.pem', '.txt', '.ps1', '.c', '.h', '.cpp', '.inc', '.projbuild', '.S'}
for source in sorted(ROOT.rglob('*')):
    if source.relative_to(ROOT).parts[0] == 'packages':
        continue
    if not source.is_file() or '__pycache__' in source.parts or source.suffix not in allowed:
        continue
    raw = source.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----', raw), source
    dest = DEST / source.relative_to(ROOT)
    if dest.exists():
        assert dest.read_bytes() == raw, dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
(DEST / '.gitattributes').write_text('* -text -filter -whitespace\n')
index = {p.relative_to(DEST).as_posix(): dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
         for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
print('Frozen', len(index), 'files', sum(v['bytes'] for v in index.values()), 'bytes')
