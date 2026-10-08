import hashlib,json,re,shutil,subprocess
from pathlib import Path
root=Path('.build/c3-flac-watchdog-20261008')
out=Path('tests/results/esp32c3-flac-watchdog-20261008')
assert not (out/'index.json').exists()
for name in ('physical','profile-physical'):
 assert json.loads((root/name/'final-board.json').read_text())['result']=='PASS'
out.mkdir(parents=True,exist_ok=True)
def digest(data):return hashlib.sha256(data).hexdigest()
def copy(source,relative):
 target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
for source in root.rglob('*'):
 if source.is_file() and source.suffix in ('.py','.ps1','.json','.log','.txt'):
  copy(source,Path('runs')/source.relative_to(root))
for name in ('ca.pem','server.pem'):
 copy(Path('.build/c3-tls-records-20261007/trust')/name,Path('public-certificates')/name)
for name in ('.build/c3-memory-20261007/network-base.defaults','.build/c3-memory-20261007/rx-copy.defaults',
             '.build/c3-tls-records-20261007/lab-ca.defaults','.build/idf-upgrade/install.py',
             '.build/c3-idf-head-20261008/save-head.py'):
 copy(Path(name),Path('build-inputs')/Path(name).name)
for variant in ('r9a97f6c54ec6-rx6-reserve-floor','r9a97f6c54ec6-rx6-reserve-profile','compact-icy-quiet'):
 folder=Path('firmware/development')/('esp32c3-idf-6.1-'+variant)
 for name in ('manifest.json','qualification.json','sdkconfig'):
  if (folder/name).exists():copy(folder/name,Path('images')/folder.name/name)
wanted=set()
for source in list(out.rglob('*.json')):
 data=json.loads(source.read_text())
 if not isinstance(data,dict):continue
 maps=[data] if source.name=='sources.json' else []
 maps += [data.get(name,{}) for name in ('test_sources_sha256','source_overlay_sha256')]
 for mapping in maps:
  if isinstance(mapping,dict):
   wanted.update((name.replace('\\','/'),expected) for name,expected in mapping.items()
                 if isinstance(expected,str) and re.fullmatch('[a-f0-9]{64}',expected))
index=[]
for name,expected in sorted(wanted):
 p=Path(name);data=p.read_bytes() if p.is_file() else b''
 if digest(data)!=expected:
  for archive in ('esp32c3-tls-reserve-20261008','esp32c3-adaptive-input-20261008'):
   saved=Path('tests/results')/archive/'sources'/expected/Path(name).name
   if saved.is_file() and digest(saved.read_bytes())==expected:
    data=saved.read_bytes();break
 if digest(data)!=expected:
  for ref in ('94a9c814','c12c3eb8','4cef6dcd'):
   attempt=subprocess.run(['git','show',ref+':'+name],capture_output=True)
   if attempt.returncode:continue
   for candidate in (attempt.stdout,attempt.stdout.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')):
    if digest(candidate)==expected:data=candidate;break
   if digest(data)==expected:break
 assert digest(data)==expected,(name,expected)
 target=Path('sources')/expected/Path(name).name
 (out/target).parent.mkdir(parents=True,exist_ok=True);(out/target).write_bytes(data)
 index.append(dict(path=name,sha256=expected,snapshot=target.as_posix()))
for name in ('tests/test-esp32c3-panic-capture.py','tests/esp32c3-cpu-profile.test.js'):
 copy(Path(name),Path('validation-sources')/Path(name).name)
(out/'source-index.json').write_text(json.dumps(index,indent=2)+'\n')
entries={p.relative_to(out).as_posix():dict(sha256=digest(p.read_bytes()),bytes=p.stat().st_size)
         for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(entries,indent=2)+'\n')
print('ARCHIVED',len(entries),'files',sum(v['bytes'] for v in entries.values()),'bytes')
