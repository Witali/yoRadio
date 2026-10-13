import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent;dest=Path('tests/results/esp32c3-radio-wifi-capture')
review=json.loads((root/'review.json').read_text())
assert review['review']=='PASS' and review['restoration']
assert not dest.exists(),'Preserve evidence'
for source in sorted(root.rglob('*')):
    if not source.is_file() or '__pycache__' in source.parts or source.suffix not in ('.py','.json','.jsonl','.log','.txt'):continue
    target=dest/source.relative_to(root);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
(dest/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(dest).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Frozen',len(index),'files; private stderr and audio excluded')
