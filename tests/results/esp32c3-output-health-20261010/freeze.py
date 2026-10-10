"""Freeze small reproducible evidence; retain PCM hashes rather than raw PCM."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DEST=Path('tests/results/esp32c3-output-health-20261010')
assert not DEST.exists(),'Never overwrite qualification evidence'
assert (ROOT/'physical/restoration.json').exists()
assert json.loads((ROOT/'review.json').read_text())['replay']=='PASS'
allowed={'.py','.ps1','.json','.jsonl','.log','.txt','.md','.c','.h','.cpp'}
for source in sorted(ROOT.rglob('*')):
    if not source.is_file() or '__pycache__' in source.parts:continue
    relative=source.relative_to(ROOT)
    if relative.parts[0] not in ('build-sources','test-sources','build-logs') and source.suffix not in allowed:continue
    dest=DEST/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
for relative in ('tests/test-production-health.py','tests/test-production-health-native.py',
                 'tests/test-sustained-output.py','tests/native/production_health_test.c'):
    path=Path(relative);dest=DEST/'host-test-sources'/path
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes())
(DEST/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(DEST).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
       for p in sorted(DEST.rglob('*')) if p.is_file()}
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Frozen',len(index),'files',sum(r['bytes'] for r in index.values()),'bytes')
