"""Freeze this completed local study without executables, keys or private settings."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
OUT=REPO/'tests/results/esp32c3-switch-owner-20261009'
assert not OUT.exists(), 'Preserve archive'
assert json.loads((ROOT/'verified.json').read_text())['result']=='PASS'
for name in ('physical','physical-fixed','physical-confirmed'):
    assert (ROOT/name/'restoration.json').is_file()
    assert not (ROOT/name/'restoration-failure.json').exists()
OUT.mkdir()
allowed={'.json','.jsonl','.txt','.log','.c','.h','.S','.py','.ps1','.pem','.md'}
for src in sorted(ROOT.rglob('*')):
    if not src.is_file() or src.suffix not in allowed or '__pycache__' in src.parts:continue
    if src.name in ('running.json','prepare_controller.py'):continue
    rel=src.relative_to(ROOT)
    blob=src.read_bytes()
    assert not re.search(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----',blob), rel
    dst=OUT/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(blob)
index={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
       for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='index.json'}
(OUT/'index.json').write_text(json.dumps(dict(files=index),indent=2)+'\n')
print(len(index),'files;',sum(p['bytes'] for p in index.values()),'bytes')
