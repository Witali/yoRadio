"""Archive completed build and board evidence, excluding private material."""
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path('.build/c3-frac4-20261010')
OUT=Path('tests/results/esp32c3-frac4-20261010')
assert not OUT.exists(),'Preserve existing archive'
restore=json.loads((ROOT/'physical/restoration.json').read_text())
initial=json.loads((ROOT/'physical/initial.json').read_text())
assert restore['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']
assert all(restore['persistence'].values())
assert not (ROOT/'physical/restoration-failure.json').exists()
for target in ('frac4','quiet-frac4'):
    assert json.loads((ROOT/target/'build-audit.json').read_text())['result']=='PASS'
    folder=ROOT/target/'logs';folder.mkdir(exist_ok=True)
    for path in Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-{target}/log').glob('*.log'):
        shutil.copyfile(path,folder/path.name)
for name in ('ca.pem','server.pem'):
    shutil.copyfile(Path('.build/c3-switch-owner-20261009/trust')/name,ROOT/name)
OUT.mkdir()
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or path.name in ('running.json','index.json'):continue
    blob=path.read_bytes()
    assert path.suffix!='.key' and not re.search(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----',blob),path
    dest=OUT/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
(OUT/'.gitattributes').write_text('* -text whitespace=cr-at-eol\nlogs/** -diff\n*.log -diff\n')
files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
       for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'index.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
print(len(files),'files;',sum(p['bytes'] for p in files.values()),'bytes')
