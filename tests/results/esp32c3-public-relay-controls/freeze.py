import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEST=Path('tests/results/esp32c3-public-relay-controls')
review=json.loads((ROOT/'review.json').read_text())
assert review['review']=='PASS' and review['restoration']
assert not DEST.exists()
for source in sorted(ROOT.rglob('*')):
    if not source.is_file() or '__pycache__' in source.parts or source.suffix not in ('.py','.json','.log'):
        continue
    dest=DEST/source.relative_to(ROOT)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(source.read_bytes())
(DEST/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(DEST).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Frozen',len(index),'files')

