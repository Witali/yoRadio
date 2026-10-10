import hashlib, json, re, subprocess
from pathlib import Path

root=Path('.build/c3-rxonly-physical-20261008')
out=Path('tests/results/esp32c3-rxonly-physical-20261008')
assert not (out/'index.json').exists()
assert json.loads((root/'physical/final-board.json').read_text())['result']=='PASS'
assert not (root/'long').exists(), 'Archive short qualification before starting long comparison'
out.mkdir(parents=True,exist_ok=True)
def digest(data): return hashlib.sha256(data).hexdigest()
def copy(source,relative):
    target=out/relative;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(source.read_bytes())
for source in root.rglob('*'):
    if source.is_file() and source.suffix in ('.py','.ps1','.json','.jsonl','.log','.txt','.c','.h','.defaults'):
        copy(source,Path('runs')/source.relative_to(root))
for name in ('ca.pem','server.pem'):
    copy(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)
for name in ('.build/c3-memory-20261007/network-base.defaults','.build/c3-memory-20261007/rx-copy.defaults',
             '.build/c3-tls-records-20261007/lab-ca.defaults','.build/idf-upgrade/install.py',
             '.build/c3-idf-head-20261008/save-head.py','.build/c3-tls-reserve-floor-20261008/tls-timed.py'):
    copy(Path(name),Path('build-inputs')/Path(name).name)
for variant in ('r9a97f6c54ec6-rx6-reserve-output8','r9a97f6c54ec6-rx6-reserve-rxonly','compact-icy-quiet'):
    folder=Path('firmware/development')/('esp32c3-idf-6.1-'+variant)
    manifest=json.loads((folder/'manifest.json').read_text())
    assert digest((folder/'app.bin').read_bytes())==manifest['image']['sha256']
    for name in ('manifest.json','qualification.json','sdkconfig'):
        if (folder/name).exists():copy(folder/name,Path('images')/folder.name/name)
wanted=set()
for source in list(out.rglob('*.json')):
    data=json.loads(source.read_text())
    if not isinstance(data,dict):continue
    maps=[data] if source.name=='sources.json' else []
    maps += [data.get(name,{}) for name in ('test_sources_sha256','source_overlay_sha256','sources')]
    for mapping in maps:
        if isinstance(mapping,dict):
            wanted.update((name.replace('\\','/'),expected) for name,expected in mapping.items()
                          if isinstance(expected,str) and re.fullmatch('[a-f0-9]{64}',expected))
index=[]
for name,expected in sorted(wanted):
    p=Path(name);data=p.read_bytes() if p.is_file() else b''
    saved=root/'historical'/expected/p.name
    if digest(data)!=expected and saved.is_file():
        data=saved.read_bytes()
    if digest(data)!=expected:
        for archive in ('esp32c3-tls-rx-reserve-20261008','esp32c3-flac-watchdog-20261008','esp32c3-tls-reserve-20261008','esp32c3-adaptive-input-20261008'):
            saved=Path('tests/results')/archive/'sources'/expected/Path(name).name
            if saved.is_file() and digest(saved.read_bytes())==expected:
                data=saved.read_bytes();break
    if digest(data)!=expected:
        for ref in ('HEAD','2a998912','07457c69','3c214632','2650eb0a','7101c491','67448ed3','94a9c814','4cef6dcd'):
            attempt=subprocess.run(['git','show',ref+':'+name],capture_output=True)
            if attempt.returncode:continue
            for candidate in (attempt.stdout,attempt.stdout.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')):
                if digest(candidate)==expected:data=candidate;break
            if digest(data)==expected:break
    assert digest(data)==expected,(name,expected)
    target=Path('sources')/expected/Path(name).name
    (out/target).parent.mkdir(parents=True,exist_ok=True);(out/target).write_bytes(data)
    index.append(dict(path=name,sha256=expected,snapshot=target.as_posix()))
for name in ('tests/test-esp32c3-transport-trace.py','tests/test-audio-server-recovery.py',
             'tools/esp32c3_tests/trace_transport.py','tools/esp32c3_tests/verify_adaptive_input_link.py',
             'tools/patch_tls_rx_reserve.py'):
    copy(Path(name),Path('validation-sources')/Path(name).name)
(out/'source-index.json').write_text(json.dumps(index,indent=2)+'\n')
entries={p.relative_to(out).as_posix():dict(sha256=digest(p.read_bytes()),bytes=p.stat().st_size)
         for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(entries,indent=2)+'\n')
print('ARCHIVED',len(entries),'files',sum(v['bytes'] for v in entries.values()),'bytes')
