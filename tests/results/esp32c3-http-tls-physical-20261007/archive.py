import hashlib,json,shutil
from pathlib import Path

root=Path.cwd()
source=Path('.build/c3-rfc-qualification-20261007')
out=Path('tests/results/esp32c3-http-tls-physical-20261007')
assert json.loads((source/'eof-fixed/final-board.json').read_text())['result']=='PASS'
assert json.loads((source/'verify-http-static.json').read_text())['result']=='PASS'
assert not (out/'index.json').exists(), 'Do not replace a completed archive'
out.mkdir(exist_ok=True)

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(p,relative):
    target=out/relative;target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        assert digest(target)==digest(p), 'Existing evidence differs: '+str(relative)
        return
    shutil.copyfile(p,target)

for folder in ('public','formats','tls-soak','eof','eof-fixed',
               'eof-host-61','eof-host-603','eof-host-fixed-6.0.3','eof-host-fixed-6.1'):
    for p in (source/folder).rglob('*'):
        if p.is_file() and p.suffix in ('.json','.log','.py','.c','.h'):
            copy(p,Path('runs')/p.relative_to(source))
for name in ('physical.json','physical.py','physical-eof.py','physical-eof-fixed.py',
             'install.json','restore.json','final-board.json','final-board.py',
             'public-window-summary.json','mp3-reference.json','mp3-reference.py',
             'host-final.json','host-final-framing.log','host-final-records.log','host-final-framing-cli.log',
             'build-eof.py','build-eof.ps1','build-eof.log','verify-aac-eof.json','verify-http-eof.json',
             'build-eof-fixed.py','build-eof-fixed.ps1','build-eof-fixed.log',
             'build-eof-fixed-retry.py','build-eof-fixed-retry.log',
             'verify-aac-eof-fixed.json','verify-http-eof-fixed.json','rejected-build-link-audit.json'):
    copy(source/name,Path('runs')/name)
for name in ('build-static.ps1','build-static-after-physical.py','build-static.log',
             'verify-http-static.json','verify-aac-static.json'):
    copy(source/name,Path('runs')/name)
for name in ('ca.pem','server.pem'):
    copy(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)
for name,p in (
    ('network-base.defaults',Path('.build/c3-memory-20261007/network-base.defaults')),
    ('rx-copy.defaults',Path('.build/c3-memory-20261007/rx-copy.defaults')),
    ('lab-ca.defaults',Path('.build/c3-tls-records-20261007/lab-ca.defaults')),
    ('install.py',Path('.build/idf-upgrade/install.py')),
    ('save-build.py',Path('.build/idf-upgrade/save-build.py')),
    ('faad-reference-command.json',Path('.build/idf-upgrade/faad-reference-command.json'))):
    copy(p,Path('build-inputs')/name)

variants=('esp32c3-idf-6.1-memory-icy-tlslab-rx4-http-guard',
          'esp32c3-idf-6.1-memory-icy-tlslab-rx6-eof',
          'esp32c3-idf-6.1-memory-icy-tlslab-rx6-eof-fixed',
          'esp32c3-idf-6.1-compact-icy-quiet-eof',
          'esp32c3-idf-6.1-compact-icy-quiet')
images={}
for variant in variants:
    folder=Path('firmware/development')/variant
    for name in ('manifest.json','sdkconfig'):copy(folder/name,Path('images')/variant/name)
    images[variant]=dict(app_sha256=digest(folder/'app.bin'),bytes=(folder/'app.bin').stat().st_size)
(out/'images.json').write_text(json.dumps(images,indent=2)+'\n')

# Each report can refer to a different tool revision, including modules it
# inventories but did not import. Retain exactly those bytes, by hash.
wanted=set()
for p in out.rglob('*.json'):
    value=json.loads(p.read_text(encoding='utf-8'))
    if isinstance(value,dict):
        for key in ('sources_sha256','test_sources_sha256','source_overlay_sha256'):
            for name,expected in value.get(key,{}).items():
                wanted.add((name.replace('\\','/'),expected))
catalog=[]
for name,expected in sorted(wanted):
    candidates=[Path(name),source/'rejected-source'/name,source/'recovered-source'/name,
        Path('tests/results/esp32c3-tcp-rx-window-20261007/sources')/name,
        Path('tests/results/esp32c3-http-rfc-20261007/sources')/name]
    found=next((p for p in candidates if p.is_file() and digest(p)==expected),None)
    if found is None:
        raise RuntimeError('Missing exact source: '+name+' '+expected)
    relative=Path('sources')/expected/Path(name).name
    if not (out/relative).exists():copy(found,relative)
    catalog.append(dict(path=name,sha256=expected,snapshot=relative.as_posix()))
(out/'source-index.json').write_text(json.dumps(catalog,indent=2)+'\n')
(out/'environment-limits.json').write_text(json.dumps(dict(
    loopback_initial='Sandbox temporary-directory WinError 5; rerun outside sandbox passed. Initial output exists in conversation only.',
    link_audit_initial='Sandbox objdump launch failed with WinError 623; no audit report created. The retained rejected-build-link-audit.json is the subsequent successful tool execution rejecting the old image.'),indent=2)+'\n')
copy(Path(__file__),Path('archive.py'))
index={p.relative_to(out).as_posix():dict(sha256=digest(p),bytes=p.stat().st_size)
       for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('ARCHIVED',len(index),'files',sum(x['bytes'] for x in index.values()),'bytes;',len(catalog),'source revisions')
