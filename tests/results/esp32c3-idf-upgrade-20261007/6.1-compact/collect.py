"""Retain explicit test artifacts; exclude temporary flash, credentials and TLS key."""
import argparse, gzip, hashlib, json, shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--version',required=True);a=p.parse_args()
src=Path('.build/idf-upgrade')
dst=Path('tests/results/esp32c3-idf-upgrade-20261007')/a.version
dst.mkdir(parents=True,exist_ok=False)
files=set()
if a.version=='6.1':
 files.update(src/name for name in ('setup-6.1.ps1','build-prepare-6.1.ps1','prepare-6.1.ps1',
                                   'physical-next.py','check-pin.ps1'))
if a.version=='6.1-compact':
 files.update(src/name for name in ('build-compact.ps1','qemu-compact.defaults',
                                   'physical-compact.py','check-compact-pcm.py','physical-ram-check.py'))
if a.version=='6.1-compact-ram':
 files.update(src/name for name in ('build-ram-final.ps1','qemu-compact.defaults',
                                   'physical-ram-check.py','physical-full-ram.py','check-compact-pcm.py'))
folders=[f'python-{a.version}',f'qemu-{a.version}-aac',f'qemu-{a.version}-vorbis-raw',
 f'qemu-{a.version}-vorbis-output',f'qemu-{a.version}-vorbis-lifecycle']
folders += [p.name for p in src.glob(f'physical-{a.version}-*') if p.is_dir()]
folders += [p.name for p in src.glob(f'qemu-{a.version}-aac-*') if p.is_dir()]
folders += [p.name for p in src.glob(f'buildlogs-{a.version}') if p.is_dir()]
if '-compact' in a.version:folders.append('qemu-'+a.version)
if a.version=='6.0.3':
 folders += ['baseline-6.0.2','host-flac-bounds','host-flac-depths']
 folders += [p.name for p in src.glob('physical-6.0.2-*') if p.is_dir()]
for name in folders:
 for f in (src/name).rglob('*'):
  if not f.is_file():continue
  relative=f.relative_to(src/name)
  if 'sources' in relative.parts:continue # repository/source hashes identify the source
  if f.suffix in ('.json','.log') or f.name=='sdkconfig':files.add(f)
  if name.endswith('vorbis-raw') and f.name=='ample.pcm.gz':files.add(f)
  if name.endswith('-aac') and f.name=='audio.wav':files.add(f)
  if name=='qemu-'+a.version and f.name.endswith('.pcm.gz'):files.add(f)
for pattern in (f'*{a.version}*.json',f'*{a.version}*.log'):
 files.update(f for f in src.glob(pattern) if f.is_file())
if a.version=='6.0.3':
 for pattern in ('host-*.log','host-*.json','build-tools-tests.log','*6.0.2*.log','*6.0.2*.json'):
  files.update(src.glob(pattern))
 files.add(src/'build-control-6.0.2.ps1')
for name in ('build-profile.ps1','build-qemu.ps1','save-build.py','install.py','qemu-aac.py',
 'physical-stage.py','physical-control.py','quiet-public.py','environment.py','host-summary.py','load-table.py',
 'run-host-tests.py','qemu-stage.py','summarize.py','collect.py','capture-build-evidence.py','node-files.txt'):
 files.add(src/name)
if a.version=='6.1':
 files={f for f in files if '6.1-compact' not in str(f)}
if a.version=='6.1-compact':
 files={f for f in files if '6.1-compact-ram' not in str(f)}
index=[]
for f in sorted(files):
 rel=f.relative_to(src);data=f.read_bytes()
 target=dst/rel
 compressed=f.suffix=='.log' or f.name in ('status.json','performance.json','audio.wav') or (f.suffix=='.json' and len(data)>131072)
 if compressed:target=target.with_name(target.name+'.gz')
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_bytes(gzip.compress(data,mtime=0) if compressed else data)
 index.append({'file':target.relative_to(dst).as_posix(),'original_bytes':len(data),
 'original_sha256':hashlib.sha256(data).hexdigest(),'stored_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(dst/'artifact-index.json').write_text(json.dumps(index,indent=2)+'\n')
print(json.dumps({'files':len(index),'bytes':sum(p.stat().st_size for p in dst.rglob('*') if p.is_file())}))
