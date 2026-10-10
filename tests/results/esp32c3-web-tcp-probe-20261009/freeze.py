"""Archive the completed diagnostic trial, excluding executables and private keys."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
OUT=REPO/'tests/results/esp32c3-web-tcp-probe-20261009'
assert not OUT.exists(),'Preserve existing evidence'
restore=json.loads((ROOT/'physical/restoration.json').read_text())
assert all(restore['persistence'].values())
assert not (ROOT/'physical/restoration-failure.json').exists()
assert (ROOT/'review.json').is_file()
OUT.mkdir()
allowed={'.json','.jsonl','.txt','.log','.c','.h','.S','.py','.ps1','.pem','.md'}
for src in sorted(ROOT.rglob('*')):
    if not src.is_file() or '__pycache__' in src.parts:continue
    if src.suffix not in allowed and not src.is_relative_to(ROOT/'sources'):continue
    if src.name=='running.json':continue
    rel=src.relative_to(ROOT)
    blob=src.read_bytes()
    assert not re.search(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----',blob),rel
    dest=OUT/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(blob)
files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
       for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='index.json'}
(OUT/'index.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
print(len(files),'files;',sum(p['bytes'] for p in files.values()),'bytes')
