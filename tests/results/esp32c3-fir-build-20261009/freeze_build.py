import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path('.build/c3-fir-20261009')
OUT=Path('tests/results/esp32c3-fir-build-20261009')
assert not OUT.exists();OUT.mkdir()
for name in ('audit_build.py','audit.log','audit-sandbox-failure.log','aac-audit-sandbox-failure.log',
             'aac-audit.log','aac-audit.json','http-audit.log','http-audit.json','allocator-audit.log','allocator-audit.json',
             'build-audit.json','codec-objects.json','build.ps1','build.log','prepare_build.py','source-hashes.json',
             'source-head.txt','output-disassembly.txt','freeze_build.py','node.log'):
    shutil.copyfile(ROOT/name,OUT/name)
shutil.copyfile(ROOT/'build-README.md',OUT/'README.md')
shutil.copyfile(ROOT/'build_replay.py',OUT/'replay.py')
for folder in ('build-sources','host','default-regression','default-boundaries'):
    for src in (ROOT/folder).rglob('*'):
        if not src.is_file() or '__pycache__' in src.parts:continue
        if folder!='build-sources' and 'sources' not in src.parts and src.suffix not in ('.json','.log'):continue
        dest=OUT/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
for p in OUT.rglob('*'):
    if p.is_file():assert not re.search(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----',p.read_bytes()),p
files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
       for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'index.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
print(len(files),'files;',sum(v['bytes'] for v in files.values()),'bytes')
