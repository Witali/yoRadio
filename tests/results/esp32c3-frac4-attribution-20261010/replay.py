"""Replay preserved owner/TCP attribution without contacting hardware."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,e in json.loads((ROOT/'index.json').read_text())['files'].items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    assert path.stat().st_size==e['bytes'] and sha(path)==e['sha256'],name
initial=json.loads((ROOT/'physical/initial.json').read_text())
assert sha(ROOT/'physical.py')==initial['controller_sha256']
assert sha(ROOT/'trial.py')==initial['trial_sha256']
for name,digest in initial['test_sources_sha256'].items():assert sha(ROOT/'test-sources'/name)==digest,name
sdk=json.loads((ROOT/'sdk-evidence.json').read_text())
for name,digest in sdk['files'].items():assert sha(ROOT/'sdk-evidence'/name)==digest,name
artifact=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-web-tcp-v2'
manifest=json.loads((artifact/'manifest.json').read_text())
assert manifest['image']==initial['candidate']
static=json.loads((ROOT/'crypto-lock-static.json').read_text())
assert static['elf_sha256']==manifest['elf_sha256']
assert sha(ROOT/'crypto-lock-static.txt')==static['inspection_sha256']
assert not static['runtime_owner_confirmed']
assert sha(artifact/'app.bin')==initial['candidate']['sha256']
assert sha(artifact/'sdkconfig')==manifest['sdkconfig_sha256']
assert (artifact/'app.bin').read_bytes()[176:208].hex()==initial['candidate']['app_elf_sha256']
prior=REPO/'tests/results/esp32c3-web-tcp-v2-20261009'
assert json.loads((prior/'build-audit.json').read_text())['image']==initial['candidate']
for name,digest in manifest['source_overlay_sha256'].items():assert sha(prior/'sources'/name)==digest,name
restore=json.loads((ROOT/'physical/restoration.json').read_text())
assert restore['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']
assert all(restore['persistence'].values())
assert len(restore['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restore['states'])
assert sha(REPO/'firmware/development/esp32c3-idf61-listen-48k/app.bin')==initial['quiet']['sha256']
assert json.loads((ROOT/'physical/probe-flash.json').read_text())['result']=='PASS'
clock=json.loads((ROOT/'physical/probe-clock.json').read_text());assert clock['parsed'] and len(clock['clocks'])==1 and clock['clocks'][0]['exact_nominal_48khz']
with (out/'review.log').open('xb') as log:
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'review.py'),'--output',str(out/'review.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
assert json.loads((out/'review.json').read_text())==json.loads((ROOT/'review.json').read_text())
print('PASS: image/sources/owner and TCP evidence/restoration replayed; original firmware failures remain.')
