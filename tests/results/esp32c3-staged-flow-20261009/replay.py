"""Replay frozen metrics and verdicts without a board or network connection."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
output=args.output.resolve()
assert not output.is_relative_to(ROOT), 'Write outside frozen evidence'
output.mkdir(parents=True,exist_ok=False)
index=json.loads((ROOT/'index.json').read_text())
for relative,expected in index['files'].items():
    source=(ROOT/relative).resolve()
    assert source.is_relative_to(ROOT)
    blob=source.read_bytes()
    assert len(blob)==expected['bytes'] and hashlib.sha256(blob).hexdigest()==expected['sha256'],relative
for script,extra,name in (
    ('summarize.py',[],'summary'),
    ('verify_evidence.py',['--summary',str(output/'summary.json')],'verified')):
    with (output/(name+'.log')).open('wb') as log:
        subprocess.check_call([sys.executable,'-X','utf8',str(ROOT/script),*extra,
                               '--output',str(output/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT)
    expected=json.loads((ROOT/(name+'.json')).read_text())
    actual=json.loads((output/(name+'.json')).read_text())
    if name=='summary':
        expected.pop('sources_sha256',None);actual.pop('sources_sha256',None)
    assert expected==actual, 'Replay changed '+name
print('PASS:',len(index['files']),'byte-exact files; all metrics and original verdicts identical')
