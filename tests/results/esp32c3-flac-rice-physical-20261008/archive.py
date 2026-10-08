"""Retain the complete measured comparison without keys, audio or build trees."""
import hashlib,json,re
from pathlib import Path

root=Path('.build/c3-flac-rice-20261008')
destination=Path('tests/results/esp32c3-flac-rice-physical-20261008')
assert (root/'physical/final-board.json').exists()
assert (root/'summary.json').exists()
assert not destination.exists(), 'Never replace earlier evidence'
destination.mkdir(parents=True)

def copy(source,target):
    data=source.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',data)
    assert source.suffix not in ('.bin','.elf','.obj','.flac','.pcm','.aac','.key','.pem')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)

for path in sorted(root.rglob('*')):
    if path.is_file() and '__pycache__' not in path.parts:
        copy(path,destination/path.relative_to(root))

files=set()
for mode in ('control','bytewise'):
    artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-'+mode)
    manifest=json.loads((artifact/'manifest.json').read_text())
    for name in ('manifest.json','sdkconfig','qualification.json'):
        copy(artifact/name,destination/'artifacts'/mode/name)
    for name,digest in manifest['source_overlay_sha256'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
        files.add(name)
files.update(str(path).replace('\\','/') for directory in ('tools/esp32c3_tests','tools/audio_test_server')
             for path in Path(directory).glob('*.py'))
files.update(['idf/esp32c3-oled-native/build.ps1','idf/esp32c3-oled-native/setup.ps1',
              'idf/esp32c3-oled-native/idf-pin.ps1',
              '.build/idf-upgrade/install.py','.build/c3-idf-head-20261008/save-head.py',
              'tools/codec_benchmark/verify_aac_network_build.py'])
for script in (root/'control/build.ps1',root/'bytewise/build.ps1'):
    # Defaults paths used in the frozen recipes are saved separately below.
    assert script.exists()
files.update(str(path).replace('\\','/') for path in Path('idf/esp32c3-oled-native').glob('sdkconfig.*defaults'))
files.update(['.build/c3-memory-20261007/network-base.defaults',
              '.build/c3-memory-20261007/rx-copy.defaults',
              '.build/c3-tls-records-20261007/lab-ca.defaults'])
sources={}
for name in sorted(files):
    path=Path(name)
    assert path.is_file(),name
    copy(path,destination/'sources'/name)
    sources[name]=hashlib.sha256(path.read_bytes()).hexdigest()
(destination/'source-index.json').write_bytes((json.dumps(sources,indent=2)+'\n').encode())

fixture_paths={
    'radio-manifest.json':Path('C:/Work/yoRadio/.worktree/aac-storage18/.build/radio-flac-20261006/recordings/manifest.json'),
    'stress-manifest.json':Path('.build/c3-reserve-soak-20261008/fixtures/manifest.json')}
for name,path in fixture_paths.items():copy(path,destination/'fixtures'/name)

index={}
for path in sorted(destination.rglob('*')):
    if path.is_file():
        data=path.read_bytes()
        index[path.relative_to(destination).as_posix()]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
(destination/'index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
print(json.dumps(dict(files=len(index),bytes=sum(v['bytes'] for v in index.values()))))
