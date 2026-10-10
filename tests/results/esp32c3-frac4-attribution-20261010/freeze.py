"""Freeze attribution evidence without TLS private keys or board settings."""
from pathlib import Path
import hashlib,json,re,shutil
ROOT=Path('.build/c3-frac4-attribution-20261010');OUT=Path('tests/results/esp32c3-frac4-attribution-20261010')
assert not OUT.exists()
initial=json.loads((ROOT/'physical/initial.json').read_text());restore=json.loads((ROOT/'physical/restoration.json').read_text())
assert restore['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256'] and all(restore['persistence'].values())
assert not (ROOT/'physical/restoration-failure.json').exists()
OUT.mkdir()
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or path.name in ('running.json','partial-review.json','partial-review.log','index.json'):continue
    blob=path.read_bytes();assert path.suffix!='.key' and not re.search(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----',blob),path
    dest=OUT/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
(OUT/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n*.log -diff\n# Immutable input snapshots preserve their original whitespace.\nsdk-evidence/** -whitespace\nphysical.py -whitespace\n')
files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'index.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
print(len(files),'files;',sum(p['bytes'] for p in files.values()),'bytes')
