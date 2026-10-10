"""Preserve completed early-MPI experiments, excluding private material."""
import hashlib,json,re
from pathlib import Path
ROOT=Path('.build/c3-mpi-startup-20261010');OUT=Path('tests/results/esp32c3-mpi-startup-20261010')
assert not OUT.exists()
i=json.loads((ROOT/'physical/initial.json').read_text());r=json.loads((ROOT/'physical/restoration.json').read_text())
assert r['identity']['app_elf_sha256']==i['quiet']['app_elf_sha256'] and all(r['persistence'].values())
assert not (ROOT/'physical/restoration-failure.json').exists()
OUT.mkdir()
for path in sorted(ROOT.rglob('*')):
 if not path.is_file() or '__pycache__' in path.parts or path.name in ('running.json','partial-review.json','index.json'):continue
 blob=path.read_bytes();assert path.suffix!='.key' and not re.search(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----',blob),path
 dst=OUT/path.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
(OUT/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n*.log -diff\n*/logs/** -diff\n# Byte-exact source and tool-output snapshots preserve their whitespace.\nbuild-sources/** -whitespace\n*/allocator-audit.disassembly.txt -whitespace\n*/startup.disassembly.txt -whitespace\n')
files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'index.json').write_text(json.dumps(dict(files=files),indent=2)+'\n');print(len(files),'files;',sum(f['bytes'] for f in files.values()),'bytes')
