import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEST=Path('tests/results/esp32c3-http-request-buffer')
review=json.loads((ROOT/'review.json').read_text())
assert review['review']=='PASS' and review['restoration']
assert not DEST.exists()
files=[]
for folder in ('host','physical','physical-repeat','physical-observed','physical-cold-control','test-sources','build-sources','quiet-http-txrelease'):
    for source in sorted((ROOT/folder).rglob('*')):
        if source.is_file() and '__pycache__' not in source.parts and (folder=='build-sources' or source.suffix in ('.py','.json','.jsonl','.log','.c','.h','.cpp','.txt','.projbuild','.ps1')):
            files.append(source)
files.extend(p for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.py','.json','.log','.ps1','.txt'))
for source in files:
    dest=DEST/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(source.read_bytes())
(DEST/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(DEST).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Frozen',len(index),'files')
