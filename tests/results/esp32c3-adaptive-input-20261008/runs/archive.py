import hashlib, json, re, shutil
from pathlib import Path
source=Path('.build/c3-adaptive-input-20261008')
out=Path('tests/results/esp32c3-adaptive-input-20261008')
assert all(json.loads((source/n/'final-board.json').read_text())['result']=='PASS' for n in ('physical','physical-counters'))
assert not (out/'index.json').exists()
out.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p, rel):
 q=out/rel; q.parent.mkdir(parents=True,exist_ok=True)
 if q.exists(): assert sha(p)==sha(q)
 else: shutil.copyfile(p,q)
for p in source.rglob('*'):
 if p.is_file() and p.suffix in ('.json','.jsonl','.log','.py','.ps1','.c','.h','.txt'):
  copy(p,Path('runs')/p.relative_to(source))
for name in ('ca.pem','server.pem'):
 copy(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)
for p in (Path('.build/c3-memory-20261007/network-base.defaults'),Path('.build/c3-memory-20261007/rx-copy.defaults'),Path('.build/c3-tls-records-20261007/lab-ca.defaults'),Path('.build/idf-upgrade/install.py'),Path('.build/c3-idf-head-20261008/save-head.py')):
 copy(p,Path('build-inputs')/p.name)
images={}
for variant in ('r9a97f6c54ec6-rx6-adaptive','compact-icy-quiet'):
 name='esp32c3-idf-6.1-'+variant; folder=Path('firmware/development')/name
 for filename in ('manifest.json','sdkconfig','qualification.json'):
  p=folder/filename
  if p.exists(): copy(p,Path('images')/name/filename)
 images[name]=dict(app_sha256=sha(folder/'app.bin'),bytes=(folder/'app.bin').stat().st_size)
(out/'images.json').write_text(json.dumps(images,indent=2)+'\n')
wanted=set()
for p in out.rglob('*.json'):
 d=json.loads(p.read_text())
 if not isinstance(d,dict): continue
 for key in ('sources','sources_sha256','source_sha256','test_sources_sha256','source_overlay_sha256'):
  values=d.get(key,{})
  if isinstance(values,dict):
   wanted.update((name.replace('\\','/'),expected) for name,expected in values.items() if isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected))
# Recover older measured source bytes, not today's edited version.
candidates={}
for folder in (source,Path('tests/results/esp32c3-idf61-revision-20261008/sources'),Path('tests/results/esp32c3-wifi-static-rx4-20261008/sources')):
 for p in folder.rglob('*'):
  if p.is_file() and p.suffix in ('.c','.h','.py','.ps1','.txt','.defaults'):
   candidates.setdefault(sha(p),p)
catalog=[]
for name,expected in sorted(wanted):
 p=Path(name)
 if not p.is_file() or sha(p)!=expected: p=candidates.get(expected)
 assert p and p.is_file() and sha(p)==expected,(name,expected)
 rel=Path('sources')/expected/Path(name).name
 copy(p,rel);catalog.append(dict(path=name,sha256=expected,snapshot=rel.as_posix()))
(out/'source-index.json').write_text(json.dumps(catalog,indent=2)+'\n')
index={p.relative_to(out).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('ARCHIVED',len(index),'files',sum(v['bytes'] for v in index.values()),'bytes')
