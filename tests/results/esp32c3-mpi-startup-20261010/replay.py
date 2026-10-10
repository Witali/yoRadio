"""Replay byte-exact early-MPI build, memory and playback evidence without a board."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,e in json.loads((ROOT/'index.json').read_text())['files'].items():
 path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
 assert path.stat().st_size==e['bytes'] and sha(path)==e['sha256'],name
initial=json.loads((ROOT/'physical/initial.json').read_text())
assert sha(ROOT/'physical.py')==initial['controller_sha256']
assert sha(ROOT/'matrix.py')==initial['matrix_sha256']
for name,h in initial['test_sources_sha256'].items():assert sha(ROOT/'test-sources'/name)==h,name
sources=json.loads((ROOT/'source-hashes.json').read_text())
for name,h in sources.items():assert sha(ROOT/'build-sources'/name)==h,name
for target in ('mpi-probe','mpi-frac4'):
 artifact=REPO/('firmware/development/esp32c3-idf-6.1-r9a97-'+target)
 m=json.loads((artifact/'manifest.json').read_text());audit=json.loads((ROOT/target/'build-audit.json').read_text())
 assert audit['result']=='PASS' and audit['image']==m['image']==initial['candidates'][target]
 assert m['source_overlay_sha256']==sources
 assert sha(artifact/'app.bin')==m['image']['sha256']
 assert (artifact/'app.bin').read_bytes()[176:208].hex()==m['image']['app_elf_sha256']
 assert sha(artifact/'sdkconfig')==m['sdkconfig_sha256']
 assert sha(artifact/'bootloader.bin')==m['bootloader_sha256']
 startup=json.loads((ROOT/target/'startup-audit.json').read_text())
 assert startup['result']=='PASS' and startup['elf_sha256']==m['image']['app_elf_sha256']
 assert sha(ROOT/target/'startup.disassembly.txt')==startup['disassembly_sha256']
 if (ROOT/'physical'/(target+'-installed.json')).is_file():
  assert json.loads((ROOT/'physical'/(target+'-flash.json')).read_text())['result']=='PASS'
  clock=json.loads((ROOT/'physical'/(target+'-clock.json')).read_text())
  assert clock['parsed'] and len(clock['clocks'])==1 and clock['clocks'][0]['exact_nominal_48khz']
restore=json.loads((ROOT/'physical/restoration.json').read_text())
assert restore['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256'] and all(restore['persistence'].values())
assert len(restore['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restore['states'])
assert sha(REPO/'firmware/development/esp32c3-idf61-listen-48k/app.bin')==initial['quiet']['sha256']
with (out/'review.log').open('xb') as log:
 subprocess.run([sys.executable,'-X','utf8',str(ROOT/'review.py'),'--output',str(out/'review.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
assert json.loads((out/'review.json').read_text())==json.loads((ROOT/'review.json').read_text())
with (out/'compare.log').open('xb') as log:
 subprocess.run([sys.executable,'-X','utf8',str(ROOT/'compare.py'),'--output',str(out/'probe-comparison.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
assert json.loads((out/'probe-comparison.json').read_text())==json.loads((ROOT/'probe-comparison.json').read_text())
print('PASS: original build/source identities, test verdicts, owner snapshots and restoration replayed')
