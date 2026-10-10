import gzip, hashlib, json
from pathlib import Path

work=Path('.build/flac-hotloops-20261008')
out=Path('tests/results/esp32c3-flac-hotloops-20261008')
out.mkdir(parents=True,exist_ok=False)

def copy_tree(folder,destination):
    for p in folder.rglob('*'):
        if not p.is_file():continue
        if p.suffix not in ('.json','.log','.txt','.py','.ps1','.cpp','.h','.snapshot','.d') and p.name!='cxxflags':continue
        name=destination/p.relative_to(folder)
        data=p.read_bytes()
        if p.name.endswith('.disassembly.txt'):
            name=name.with_suffix(name.suffix+'.gz');data=gzip.compress(data,mtime=0)
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)

for name in ('baseline','rice-profile','compare','matrix','radio-asan','bounds','bounds-contiguous','rice-parent'):
    assert json.loads((work/name/'report.json').read_text())['passed']
    copy_tree(work/name,Path(name))
copy_tree(Path('tests/results/esp32c3-idf6-rice-20261008/host'),Path('rice-agent'))
copy_tree(work/'lpc-codegen/final-source-audit',Path('rv32'))
copy_tree(work/'shift-codegen/frozen-audit',Path('rejected-shift'))
copy_tree(work/'parent-review',Path('parent-review'))
for name in ('save.py','verify_codegen.py'):
    (out/name).write_bytes((work/name).read_bytes())
entries={p.relative_to(out).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
         for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(entries,indent=2)+'\n')
print(len(entries),'files',sum(v['bytes'] for v in entries.values()),'bytes')
