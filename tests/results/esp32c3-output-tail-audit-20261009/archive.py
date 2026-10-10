"""Freeze the baseline tail reproduction independently of future source changes."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/codec_benchmark/run_output_dma_host.py').is_file())
DEST=REPO/'tests/results/esp32c3-output-tail-audit-20261009'
assert not DEST.exists()
report=json.loads((ROOT/'report.json').read_text())
assert report['result']=='BUG REPRODUCED'
files={name:ROOT/name for name in ('probe.c','unit.c','probe.pcm','report.json','result.log','build.log','archive.py','replay.py')}
for relative,expected in report['sources'].items():
    path=ROOT/'sources'/relative
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
    name=('sources/'+relative) if not relative.startswith('.build/') else 'initial-'+path.name
    files[name]=path
index=dict(kind='Baseline staged PCM EOF/same-rate contamination reproduction',
    git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    result='BUG REPRODUCED',files={})
for relative,path in files.items():
    blob=path.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',blob)
    dest=DEST/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
    index['files'][relative]=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest())
(DEST/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(files),'files')
