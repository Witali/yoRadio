"""Replay quiet-image source, build, health, failure and restoration evidence."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,entry in json.loads((ROOT/'index.json').read_text())['files'].items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    assert path.stat().st_size==entry['bytes'] and sha(path)==entry['sha256'],name
artifact=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-quiet-mpi-health'
m=json.loads((artifact/'manifest.json').read_text());audit=json.loads((ROOT/'quiet-mpi-health/build-audit.json').read_text())
assert audit['result']=='PASS' and audit['image']==m['image']
assert sha(artifact/'app.bin')==m['image']['sha256']
assert (artifact/'app.bin').read_bytes()[176:208].hex()==m['image']['app_elf_sha256']
assert sha(artifact/'sdkconfig')==m['sdkconfig_sha256'] and sha(artifact/'bootloader.bin')==m['bootloader_sha256']
assert m['production_profile'] and not m['lab_ca'] and not m['production_qualified']
sources=json.loads((ROOT/'source-hashes.json').read_text());assert sources==m['source_overlay_sha256']
for name,digest in sources.items():assert sha(ROOT/'build-sources'/name)==digest,name
health=json.loads((ROOT/'health-audit.json').read_text());assert health['result']=='PASS' and health['elf_sha256']==m['image']['app_elf_sha256']
for campaign,script in (('physical','physical.py'),('physical-local','physical-local.py')):
    initial=json.loads((ROOT/campaign/'initial.json').read_text())
    assert sha(ROOT/script)==initial['controller_sha256'] and initial['candidate']==m['image']
    for name,digest in initial['test_sources_sha256'].items():assert sha(ROOT/'test-sources'/name)==digest
    restore=json.loads((ROOT/campaign/'restoration.json').read_text())
    assert restore['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256'] and all(restore['persistence'].values())
    assert len(restore['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restore['states'])
    assert sha(REPO/'firmware/development/esp32c3-idf61-listen-48k/app.bin')==initial['quiet']['sha256']
with (out/'review.log').open('xb') as log:
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'review.py'),'--output',str(out/'review.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
assert json.loads((out/'review.json').read_text())==json.loads((ROOT/'review.json').read_text())
print('PASS: build/source identities, original failures, heap/fault observations and both restorations replayed')
