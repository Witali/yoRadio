"""Verify and replay the frozen reboot comparison without board access."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
args=p.parse_args()
out=args.output.resolve()
assert not out.is_relative_to(ROOT)
out.mkdir(parents=True,exist_ok=False)
index=json.loads((ROOT/'index.json').read_text())
for name,expected in index['files'].items():
    path=(ROOT/name).resolve()
    assert path.is_relative_to(ROOT)
    blob=path.read_bytes()
    assert len(blob)==expected['bytes'] and hashlib.sha256(blob).hexdigest()==expected['sha256'],name
with (out/'replay.log').open('wb') as log:
    subprocess.check_call([sys.executable,'-X','utf8',str(ROOT/'summarize.py'),
                           '--output',str(out/'summary.json')],stdout=log,stderr=subprocess.STDOUT)
assert json.loads((ROOT/'summary.json').read_text())==json.loads((out/'summary.json').read_text())
print('PASS:',len(index['files']),'byte-exact files; all reboot and TLS observations reproduced')
