"""Archive sanitized reports and reproducible sources, retaining raw/stored hashes."""
import gzip, hashlib, json, shutil, subprocess
from pathlib import Path
root=Path('.build/c3-memory-20261007')
target=Path('tests/results/esp32c3-icy-rx-memory-20261007')
target.mkdir(parents=True,exist_ok=True)
sha=lambda value:hashlib.sha256(value).hexdigest()
entries=[]
def save(path,relative):
    raw=path.read_bytes()
    compressed=len(raw)>65536
    stored=gzip.compress(raw,mtime=0) if compressed else raw
    relative=str(relative).replace('\\','/')+('.gz' if compressed else '')
    output=target/relative
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(stored)
    assert (gzip.decompress(output.read_bytes()) if compressed else output.read_bytes()) == raw
    entries.append(dict(path=relative,raw_bytes=len(raw),stored_bytes=len(stored),
                        raw_sha256=sha(raw),stored_sha256=sha(stored)))

for path in sorted(root.rglob('*')):
    if path.is_file() and path.suffix in ('.json','.log','.ps1','.py','.defaults'):
        save(path,Path('runs')/path.relative_to(root))
for helper in ('install.py','save-build.py','faad-reference-command.json'):
    save(Path('.build/idf-upgrade')/helper,Path('helpers')/helper)
for name in ('memory-control-profile','memory-rxcopy-profile','compact-icy-production','compact-icy-quiet',
             'memory-icy-rxcopy-profile','memory-icy-rxcopy-quiet'):
    directory=Path('idf/esp32c3-oled-native/build-idf-6.1-'+name)
    for path in sorted((directory/'log').glob('idf_py_*')):
        if path.is_file():save(path,Path('build-logs')/name/path.name)
sources=[Path(p) for p in subprocess.check_output(['git','diff','--name-only','3445993a..HEAD'],text=True).splitlines()
         if p.endswith(('.c','.h','.py','.js','CMakeLists.txt'))]
for directory in ('tools/esp32c3_tests','tools/audio_test_server'):
    sources.extend(Path(directory).glob('*.py'))
sources.extend(Path('idf/esp32c3-oled-native').glob('sdkconfig*.defaults'))
for path in sorted(set(sources)):
    if path.is_file():save(path,Path('sources')/path)
for name in ('memory-control-profile','memory-rxcopy-profile','compact-icy-debug','compact-icy-quiet',
             'memory-icy-rxcopy-profile','memory-icy-rxcopy-quiet'):
    directory=Path('firmware/development/esp32c3-idf-6.1-'+name)
    manifest=json.loads((directory/'manifest.json').read_text())
    assert sha((directory/'app.bin').read_bytes()) == manifest['image']['sha256']
    assert sha((directory/'sdkconfig').read_bytes()) == manifest['sdkconfig_sha256']
    for file in ('manifest.json','sdkconfig'):save(directory/file,Path('firmware')/name/file)
index=dict(source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    note='Raw broadcasts, credentials and private TLS keys are not archived. Verdicts are not changed by archiving.',files=entries)
(target/'index.json').write_text(json.dumps(index,indent=2)+'\n')
for entry in entries:
    stored=(target/entry['path']).read_bytes()
    assert sha(stored)==entry['stored_sha256']
    raw=gzip.decompress(stored) if entry['path'].endswith('.gz') else stored
    assert sha(raw)==entry['raw_sha256']
print('Archived and verified',len(entries),'files;',sum(e['stored_bytes'] for e in entries),'bytes')
