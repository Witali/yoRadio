"""Offline reproduction of owner/retention evidence, including original failures."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from references import verify_references

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
output=a.output.resolve()
assert not output.is_relative_to(ROOT), 'Preserve frozen evidence'
output.mkdir(parents=True,exist_ok=False)
verify_references()
index=json.loads((ROOT/'index.json').read_text())
for name,expected in index['files'].items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    blob=path.read_bytes()
    assert len(blob)==expected['bytes'] and hashlib.sha256(blob).hexdigest()==expected['sha256'],name
for script,name,extra in (('review.py','review',[]),('review.py','review-fixed',['--fixed']),
                          ('review.py','review-confirmed',['--confirmed']),
                          ('verify_evidence.py','verified',[])):
    with (output/(name+'.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/script),*extra,'--output',str(output/(name+'.json'))],
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    assert json.loads((output/(name+'.json')).read_text())==json.loads((ROOT/(name+'.json')).read_text()),name
print('PASS:',len(index['files']),'byte-exact files; original and fixed observations reproduced')
