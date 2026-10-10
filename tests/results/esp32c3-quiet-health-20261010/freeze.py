"""Preserve both completed quiet-image campaigns, including every failed gate."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=Path('tests/results/esp32c3-quiet-health-20261010')
assert not OUT.exists()
for name in ('physical','physical-local'):
    initial=json.loads((ROOT/name/'initial.json').read_text())
    restore=json.loads((ROOT/name/'restoration.json').read_text())
    assert restore['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']
    assert all(restore['persistence'].values()) and len(restore['states'])==3
    assert all(s['audio']==initial['status']['audio'] for s in restore['states'])
    assert not (ROOT/name/'restoration-failure.json').exists()
OUT.mkdir()
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or path.name in ('running.json','partial-review.json','index.json'):continue
    blob=path.read_bytes();assert path.suffix!='.key' and not re.search(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----',blob),path
    dst=OUT/path.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
(OUT/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n*.log -diff\n*/logs/** -diff\nbuild-logs/** -diff -whitespace\n# Preserve byte-exact snapshots of existing source/tool output.\nbuild-sources/** -whitespace\nnative-health/*.c -whitespace\n*.disassembly.txt -whitespace\n*/allocator-audit.disassembly.txt -whitespace\n')
files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'index.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
print(len(files),'files;',sum(r['bytes'] for r in files.values()),'bytes')
