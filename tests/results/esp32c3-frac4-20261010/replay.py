"""Replay the frozen fractional-clock combination without accessing a board."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=json.loads((ROOT/'index.json').read_text())
for name,expected in index['files'].items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    assert path.stat().st_size==expected['bytes'] and sha(path)==expected['sha256'],name
for name,digest in json.loads((ROOT/'source-hashes.json').read_text()).items():assert sha(ROOT/'build-sources'/name)==digest,name
initial=json.loads((ROOT/'physical/initial.json').read_text())
assert sha(ROOT/'physical.py')==initial['controller_sha256']
assert sha(ROOT/'trial.py')==initial['trial_sha256']
for name,digest in initial['test_sources_sha256'].items():assert sha(ROOT/'test-sources'/name)==digest,name
assert initial['host_clock']['api']=='time.perf_counter' and initial['host_clock']['resolution']<=1e-6
restore=json.loads((ROOT/'physical/restoration.json').read_text())
assert restore['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']
assert all(restore['persistence'].values())
assert len(restore['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restore['states'])
for target in ('frac4','quiet-frac4'):
    artifact=REPO/f'firmware/development/esp32c3-idf-6.1-r9a97-{target}'
    manifest=json.loads((artifact/'manifest.json').read_text())
    audit=json.loads((ROOT/target/'build-audit.json').read_text())
    assert audit['result']=='PASS' and audit['image']==manifest['image']
    assert sha(artifact/'app.bin')==manifest['image']['sha256']
    assert (artifact/'app.bin').read_bytes()[176:208].hex()==manifest['image']['app_elf_sha256']
    assert sha(artifact/'sdkconfig')==manifest['sdkconfig_sha256']
    assert sha(artifact/'bootloader.bin')==manifest['bootloader_sha256']
    assert manifest['source_overlay_sha256']==json.loads((ROOT/'source-hashes.json').read_text())
    if target=='frac4':assert initial['candidate']==manifest['image']
assert json.loads((ROOT/'physical/frac4-flash.json').read_text())['result']=='PASS'
clock=json.loads((ROOT/'physical/frac4-clock.json').read_text())
assert clock['parsed'] and len(clock['clocks'])==1 and clock['clocks'][0]['exact_nominal_48khz']
for name in ('review','events'):
    with (out/(name+'.log')).open('xb') as log:
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/(name+'.py')),'--output',str(out/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
    assert json.loads((out/(name+'.json')).read_text())==json.loads((ROOT/(name+'.json')).read_text())
print('PASS: byte-exact images/evidence, retained verdicts and restoration replayed')
