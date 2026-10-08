import hashlib,json,shutil
from pathlib import Path
source=Path('.build/c3-retained-tls-20261008')
out=Path('tests/results/esp32c3-retained-tls-rx-20261008')
assert json.loads((source/'physical/final-board.json').read_text())['result']=='PASS'
assert not (out/'index.json').exists()
out.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,relative):
    q=out/relative;q.parent.mkdir(parents=True,exist_ok=True)
    if q.exists():assert sha(p)==sha(q)
    else:shutil.copyfile(p,q)
for folder in ('physical','host-default','host-retain'):
    for p in (source/folder).rglob('*'):
        if p.is_file() and p.suffix in ('.json','.log','.py','.c','.h'):
            copy(p,Path('runs')/p.relative_to(source))
for name in ('build.py','build.ps1','build-retain.log','verify-aac.json','verify-http.json','physical.py','control-summary.json','formats-runtime-audit.json'):
    copy(source/name,Path('runs')/name)
for name in ('ca.pem','server.pem'):
    copy(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)
for p in (Path('.build/c3-memory-20261007/network-base.defaults'),Path('.build/c3-memory-20261007/rx-copy.defaults'),Path('.build/c3-tls-records-20261007/lab-ca.defaults'),Path('.build/idf-upgrade/install.py'),Path('.build/idf-upgrade/save-build.py'),Path('.build/idf-upgrade/faad-reference-command.json')):
    copy(p,Path('build-inputs')/p.name)
images={}
for variant in ('esp32c3-idf-6.1-memory-icy-tlslab-rx6-retain','esp32c3-idf-6.1-compact-icy-quiet'):
    p=Path('firmware/development')/variant
    for name in ('manifest.json','sdkconfig'):copy(p/name,Path('images')/variant/name)
    images[variant]=dict(app_sha256=sha(p/'app.bin'),bytes=(p/'app.bin').stat().st_size)
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
    candidates=[Path(name),source/'pre-test-gate'/name]
    found=next((p for p in candidates if p.is_file() and sha(p)==expected),None)
    if found is None:raise ValueError('Missing exact source '+name+' '+expected)
    rel=Path('sources')/expected/Path(name).name
    copy(found,rel);catalog.append(dict(path=name,sha256=expected,snapshot=rel.as_posix()))
(out/'source-index.json').write_text(json.dumps(catalog,indent=2)+'\n')
copy(Path(__file__),Path('archive.py'))
index={p.relative_to(out).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('ARCHIVED',len(index),'files',sum(i['bytes'] for i in index.values()),'bytes')
