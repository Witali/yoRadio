"""Replay the frozen experiment offline; never reinterpret failed observations."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();output=a.output.resolve()
assert not output.is_relative_to(ROOT),'Preserve frozen evidence'
output.mkdir(parents=True,exist_ok=False)
from references import verify_references
verify_references()
index=json.loads((ROOT/'index.json').read_text())
for name,expected in index['files'].items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    blob=path.read_bytes()
    assert len(blob)==expected['bytes'] and hashlib.sha256(blob).hexdigest()==expected['sha256'],name
for script,name,extra in (
    ('summarize.py','summary',[]),
    ('verify_evidence.py','verified',['--summary',str(output/'summary.json')]),
    ('compare.py','comparison',['--summary',str(output/'summary.json')])):
    with (output/(name+'.log')).open('wb') as log:
        subprocess.check_call([sys.executable,'-X','utf8',str(ROOT/script),*extra,
            '--output',str(output/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT)
    assert json.loads((ROOT/(name+'.json')).read_text())==json.loads((output/(name+'.json')).read_text()),name
print('PASS:',len(index['files']),'byte-exact files; original and independent results reproduced')
