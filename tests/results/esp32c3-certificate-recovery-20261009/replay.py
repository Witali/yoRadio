"""Verify shared frozen sources and reproduce the certificate-recovery findings offline."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
out=args.output.resolve()
assert not out.is_relative_to(ROOT)
out.mkdir(parents=True,exist_ok=False)
index=json.loads((ROOT/'index.json').read_text())

def verify(directory,index):
    for name,expected in index['files'].items():
        path=(directory/name).resolve()
        assert path.is_relative_to(directory)
        blob=path.read_bytes()
        assert len(blob)==expected['bytes'] and hashlib.sha256(blob).hexdigest()==expected['sha256'],name

for name,digest in index['dependencies'].items():
    path=(REPO/name).resolve()
    assert path.is_relative_to(REPO)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
    verify(path.parent,json.loads(path.read_text()))
verify(ROOT,index)
with (out/'replay.log').open('wb') as log:
    subprocess.check_call([sys.executable,'-X','utf8',str(ROOT/'analyze.py'),
        '--output',str(out/'summary.json')],stdout=log,stderr=subprocess.STDOUT)
assert json.loads((ROOT/'summary.json').read_text())==json.loads((out/'summary.json').read_text())
print('PASS:',len(index['files']),'byte-exact files,',len(index['dependencies']),'verified dependency archives; identical results')
