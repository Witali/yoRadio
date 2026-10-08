import hashlib, json, shutil
from pathlib import Path

source = Path('.build/c3-idf-head-20261008')
host = Path('.build/c3-retained-tls-20261008')
out = Path('tests/results/esp32c3-idf61-revision-20261008')
assert not (out/'index.json').exists()
for directory in ('physical','soak','mp3-followup'):
    assert json.loads((source/directory/'final-board.json').read_text())['result']=='PASS'
out.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p, relative):
    q=out/relative;q.parent.mkdir(parents=True,exist_ok=True)
    if q.exists(): assert sha(p)==sha(q)
    else: shutil.copyfile(p,q)

for p in source.rglob('*'):
    if p.is_file() and p.suffix in ('.json','.jsonl','.log','.py','.ps1'):
        copy(p,Path('runs')/p.relative_to(source))
for name in ('host-sdk-head','lwip-head-pool','lwip-head-heap','native-node-tests.log','native-node-tests-fixed.log',
             'file-runtime-tests.log','file-runtime-tests-unrestricted.log','acceptance-host.log','public-host.log',
             'sdk-source-audit.json','setup-revision.log','setup-tools-revision.log','upstream-http-tls.diff','upstream-tags.txt'):
    p=host/name
    if p.is_dir():
        for child in p.rglob('*'):
            if child.is_file() and child.suffix in ('.json','.log','.py','.c','.h'):
                copy(child,Path('host')/child.relative_to(host))
    else: copy(p,Path('host')/(name+'.json' if name.startswith('lwip-head-') else name))
qemu=Path('.build/idf-upgrade/qemu-head9a97')
for name in ('qemu.log','report.json','pcm-comparison.json','late.pcm.gz','gaps.pcm.gz'):
    copy(qemu/name,Path('qemu')/name)
copy(Path('idf/esp32c3-oled-native/build-idf-6.1-head9a97-qemu/sdkconfig'),Path('qemu/sdkconfig'))
for name in ('ca.pem','server.pem'):
    copy(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)
for p in (Path('.build/c3-memory-20261007/network-base.defaults'),Path('.build/c3-memory-20261007/rx-copy.defaults'),
          Path('.build/c3-tls-records-20261007/lab-ca.defaults'),Path('.build/idf-upgrade/install.py'),
          Path('.build/idf-upgrade/faad-reference-command.json'),Path('.build/idf-upgrade/check-compact-pcm.py')):
    copy(p,Path('build-inputs')/p.name)
images={}
for variant in ('r9a97f6c54ec6-rx6-dynamic','r9a97f6c54ec6-quiet','r9a97f6c54ec6-deep-sleep','r9a97f6c54ec6-rtc32k','compact-icy-quiet'):
    name='esp32c3-idf-6.1-'+variant;p=Path('firmware/development')/name
    for file in ('manifest.json','sdkconfig'):copy(p/file,Path('images')/name/file)
    images[name]=dict(app_sha256=sha(p/'app.bin'),bytes=(p/'app.bin').stat().st_size)
(out/'images.json').write_text(json.dumps(images,indent=2)+'\n')
wanted=set()
for p in out.rglob('*.json'):
    v=json.loads(p.read_text())
    if isinstance(v,dict):
        for key in ('sources','sources_sha256','source_sha256','test_sources_sha256','source_overlay_sha256'):
            d=v.get(key,{})
            if isinstance(d,dict):wanted.update((name.replace('\\','/'),expected) for name,expected in d.items()
                if isinstance(expected,str) and len(expected)==64 and all(c in '0123456789abcdef' for c in expected))
catalog=[]
for name,expected in sorted(wanted):
    candidates=[Path(name),host/'pre-test-gate'/name]
    found=next((p for p in candidates if p.is_file() and sha(p)==expected),None)
    if found is None:raise ValueError('Missing exact source '+name+' '+expected)
    rel=Path('sources')/expected/Path(name).name
    copy(found,rel);catalog.append(dict(path=name,sha256=expected,snapshot=rel.as_posix()))
(out/'source-index.json').write_text(json.dumps(catalog,indent=2)+'\n')
index={p.relative_to(out).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('ARCHIVED',len(index),'files',sum(i['bytes'] for i in index.values()),'bytes')
