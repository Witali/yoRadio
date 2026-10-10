"""Freeze finished observations, retaining hash-pinned shared evidence."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
DEST = REPO/'tests/results/esp32c3-switch-capacity-control-20261009'
assert not DEST.exists(), 'Do not replace frozen evidence'
assert json.loads((ROOT/'verified.json').read_text())['restored']
DEST.mkdir()
for name in ('physical.py','prepare.py','summarize.py','verify_evidence.py','compare.py','replay.py',
             'references.py','references.json','build-audit.json','case-catalog.json','sdk.json',
             'summary.json','verified.json','comparison.json','archive.py','README.md'):
    shutil.copy2(ROOT/name,DEST/name)
shutil.copytree(ROOT/'physical',DEST/'physical')
shutil.copytree(ROOT/'sdk',DEST/'sdk')
files = {}
for path in sorted(DEST.rglob('*')):
    if path.is_file():
        blob = path.read_bytes()
        files[path.relative_to(DEST).as_posix()] = dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
index = dict(kind='Matched 0/4/4/0 switching and TLS capacity control',
             scope='Original observations; private settings and private keys are not archived.',
             files=files)
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(files),'files,',sum(f['bytes'] for f in files.values()),'bytes')
