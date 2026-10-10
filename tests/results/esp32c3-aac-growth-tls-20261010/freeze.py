"""Freeze controlled TLS evidence without private keys or generated PCM."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEST=Path('tests/results/esp32c3-aac-growth-tls-20261010')
assert not DEST.exists()
assert json.loads((ROOT/'review.json').read_text())['exact_listened_image_restored']
allowed={'.py','.ps1','.json','.jsonl','.log','.txt','.md','.c','.h','.cpp'}
for source in sorted(ROOT.rglob('*')):
    if not source.is_file() or '__pycache__' in source.parts:continue
    relative=source.relative_to(ROOT)
    if source.name in ('ca.pem','server.pem'):
        data=source.read_bytes();assert b'PRIVATE KEY' not in data
    elif relative.parts[0] not in ('build-sources','test-sources','build-logs') and source.suffix not in allowed:
        continue
    dest=DEST/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
for name in ('test-aac-growth-transport.py','test-aac-growth-fixtures.py','test-public-file-acceptance.py'):
    source=Path('tests')/name;dest=DEST/'host-test-sources'/name
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
(DEST/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(DEST).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
       for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Frozen',len(index),'files',sum(r['bytes'] for r in index.values()),'bytes')
