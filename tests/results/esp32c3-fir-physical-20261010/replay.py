"""Validate frozen evidence; replay success does not mean playback acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=json.loads((ROOT/'index.json').read_text())
for name,expected in index['files'].items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    assert path.stat().st_size==expected['bytes'] and sha(path)==expected['sha256'],name
initial=json.loads((ROOT/'physical/initial.json').read_text())
assert sha(ROOT/'physical.py')==initial['controller_sha256']
assert sha(ROOT/'trial.py')==initial['trial_sha256']
for name,digest in initial['test_sources_sha256'].items():assert sha(ROOT/'test-sources'/name)==digest,name
restore=json.loads((ROOT/'physical/restoration.json').read_text())
assert restore['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']
assert all(restore['persistence'].values())
assert all(s['audio']==initial['status']['audio'] for s in restore['states'])
with (out/'review.log').open('xb') as log:
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'review.py'),'--output',str(out/'review.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
observed=json.loads((out/'review.json').read_text())
assert observed==json.loads((ROOT/'review.json').read_text())
assert not observed['missing']
assert observed['phases']['fir-flac']['runtime']['result']=='FAIL'
assert observed['phases']['fir-tls-grow']['observation_interrupted']
assert all(not v['sustained']['digital_acceptance'] for v in observed['phases'].values() if 'sustained' in v)
print('PASS: byte-exact evidence and verdicts replayed; FIR physical acceptance remains FAIL')
