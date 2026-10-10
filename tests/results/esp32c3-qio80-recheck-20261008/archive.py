"""Archive technical evidence only; never include private Flash backups or keys."""
import hashlib,json,re
from pathlib import Path
root=Path('.build/c3-qio80-recheck-20261008')
dst=Path('tests/results/esp32c3-qio80-recheck-20261008')
assert (root/'physical/final-board.json').is_file()
assert (root/'summary.json').is_file()
assert not dst.exists(),'Never replace earlier evidence'
dst.mkdir(parents=True)

def copy(src,target):
    assert src.suffix not in ('.bin','.elf','.obj','.flac','.pcm','.aac','.key','.pem','.pyc')
    data=src.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',data)
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)

for path in sorted(root.rglob('*')):
    if path.is_file() and '__pycache__' not in path.parts and 'private' not in path.relative_to(root).parts:
        copy(path,dst/path.relative_to(root))
files=set(json.loads((root/'source-fingerprints.json').read_text()))
for directory in ('tools/esp32c3_tests','tools/audio_test_server'):
    files.update(p.as_posix() for p in Path(directory).glob('*.py'))
files.update(['idf/esp32c3-oled-native/build.ps1','idf/esp32c3-oled-native/idf-pin.ps1',
    'tools/codec_benchmark/verify_aac_network_build.py',
    '.build/c3-idf-head-20261008/save-head.py','.build/c3-memory-20261007/network-base.defaults',
    '.build/c3-memory-20261007/rx-copy.defaults','.build/c3-tls-records-20261007/lab-ca.defaults',
    '.agents/skills/flash-reset-esp32c3-oled/scripts/reset_esp32c3_oled.ps1'])
files.update(p.as_posix() for p in Path('idf/esp32c3-oled-native').glob('sdkconfig.*defaults'))
index={}
for name in sorted(files):
    path=Path(name);copy(path,dst/'sources'/name)
    index[name]=hashlib.sha256(path.read_bytes()).hexdigest()
for name,digest in json.loads((root/'source-fingerprints.json').read_text()).items():
    assert index[name]==digest,'Source changed during physical comparison: '+name
(dst/'source-index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
for mode in ('dio','qio'):
    artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-flash-'+mode+'80')
    for name in ('manifest.json','sdkconfig','qualification.json'):
        copy(artifact/name,dst/'artifacts'/mode/name)
copy(Path('.build/c3-reserve-soak-20261008/fixtures/manifest.json'),dst/'fixtures/stress-manifest.json')
index={}
for path in sorted(dst.rglob('*')):
    if path.is_file():
        data=path.read_bytes();index[path.relative_to(dst).as_posix()]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
(dst/'index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
print(json.dumps({'files':len(index),'bytes':sum(v['bytes'] for v in index.values())}))
