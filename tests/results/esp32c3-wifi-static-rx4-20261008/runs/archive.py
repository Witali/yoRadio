import hashlib,json,shutil
from pathlib import Path
source=Path('.build/c3-static-rx4-20261008')
out=Path('tests/results/esp32c3-wifi-static-rx4-20261008')
assert json.loads((source/'physical/final-board.json').read_text())['result']=='PASS'
assert json.loads((source/'soak/recovery-board.json').read_text())['result']=='PASS'
assert not (out/'index.json').exists()
out.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,relative):
    q=out/relative;q.parent.mkdir(parents=True,exist_ok=True)
    if q.exists():assert sha(p)==sha(q)
    else:shutil.copyfile(p,q)
for p in source.rglob('*'):
    if p.is_file() and p.suffix in ('.json','.jsonl','.log','.py','.ps1'):
        copy(p,Path('runs')/p.relative_to(source))
for name in ('ca.pem','server.pem'):
    copy(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)
for p in (Path('.build/c3-memory-20261007/network-base.defaults'),Path('.build/c3-memory-20261007/rx-copy.defaults'),
          Path('.build/c3-tls-records-20261007/lab-ca.defaults'),Path('.build/idf-upgrade/install.py'),
          Path('.build/c3-idf-head-20261008/save-head.py')):
    copy(p,Path('build-inputs')/p.name)
images={}
for variant in ('r9a97f6c54ec6-rx6-srx4','r9a97f6c54ec6-rx6-dynamic','compact-icy-quiet'):
    name='esp32c3-idf-6.1-'+variant;p=Path('firmware/development')/name
    for file in ('manifest.json','sdkconfig'):copy(p/file,Path('images')/name/file)
    images[name]=dict(app_sha256=sha(p/'app.bin'),bytes=(p/'app.bin').stat().st_size)
(out/'images.json').write_text(json.dumps(images,indent=2)+'\n')
wanted=set()
for p in out.rglob('*.json'):
    v=json.loads(p.read_text())
    if isinstance(v,dict):
        for key in ('sources_sha256','source_sha256','test_sources_sha256','source_overlay_sha256'):
            d=v.get(key,{})
            if isinstance(d,dict):wanted.update((name.replace('\\','/'),expected) for name,expected in d.items())
catalog=[]
for name,expected in sorted(wanted):
    p=Path(name);assert p.is_file() and sha(p)==expected,(name,expected)
    rel=Path('sources')/expected/p.name
    copy(p,rel);catalog.append(dict(path=name,sha256=expected,snapshot=rel.as_posix()))
(out/'source-index.json').write_text(json.dumps(catalog,indent=2)+'\n')
index={p.relative_to(out).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('ARCHIVED',len(index),'files',sum(i['bytes'] for i in index.values()),'bytes')
