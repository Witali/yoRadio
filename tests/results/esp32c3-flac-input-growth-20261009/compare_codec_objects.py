"""Compare codec code/constant sections before link-address relocation."""
import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parent
builds={v:Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-flac-input{v}') for v in ('0','4')}
objects={}
for v,build in builds.items():
    chosen=[]
    for pattern in ('flac_decoder.cpp.obj','custom_flac_adapter.cpp.obj','native_aac_decoder.c.obj','aac_*.c.obj'):
        chosen+=list(build.rglob(pattern))
    chosen+=list((build/'esp-idf/main/compact5').glob('*.obj'))
    objects[v]={p.name:p for p in chosen}
    assert len(objects[v])==len(chosen),'Ambiguous object name'
assert objects['0'].keys()==objects['4'].keys()

def sections(path):
    with path.open('rb') as stream:
        elf=ELFFile(stream)
        return {s.name:dict(bytes=s['sh_size'],sha256=hashlib.sha256(s.data()).hexdigest())
                for s in elf.iter_sections() if s.name.startswith(('.text','.rodata')) and s['sh_size']}

rows={}
for name in sorted(objects['0']):
    old,new=(sections(objects[v][name]) for v in ('0','4'))
    rows[name]=dict(identical=old==new,sections=old,
        differing_sections=[k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)])
result=dict(result='PASS' if all(r['identical'] for r in rows.values()) else 'REVIEW_REQUIRED',
    scope='Unrelocated codec text/constant sections only; not PCM or analog measurement.',objects=rows)
(ROOT/'codec-objects.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['result'],len(rows),'codec objects;',sum(len(r['sections']) for r in rows.values()),'sections')
for name,row in rows.items():
    if not row['identical']:print(name,row['differing_sections'])
