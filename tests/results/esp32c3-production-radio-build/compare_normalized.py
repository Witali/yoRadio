import hashlib,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
root=Path('.build/c3-production-radio');base=Path('idf/esp32c3-oled-native')
a=base/'build-idf-6.1-r9a97-quiet-http-txrelease';b=base/'build-idf-6.1-r9a97-production-radio'
def sections(folder):
    result={}
    for path in folder.rglob('*.obj'):
        rel=path.relative_to(folder).as_posix()
        if rel.startswith('bootloader/'):continue
        key=rel
        assert key not in result,key
        with path.open('rb') as f:result[key]={s.name:s.data() for s in ELFFile(f).iter_sections() if s.name.startswith(('.text','.rodata')) and s['sh_size']}
    return result
left,right=sections(a),sections(b)
for name in list(left.keys()-right.keys()):
    matches=[p for p in right.keys()-left.keys() if p.split('.dir/')[0]==name.split('.dir/')[0] and Path(p).name==Path(name).name]
    assert len(matches)==1,(name,matches)
    right[name]=right.pop(matches[0])
assert left.keys()==right.keys()
changes={};matched=0
for path in left:
    assert left[path].keys()==right[path].keys(),path
    for section,old in left[path].items():
        new=right[path][section]
        if old==new:matched+=1;continue
        if section=='.text.http_on_body':
            assert len(old)==len(new) and old[:0x104]==new[:0x104] and old[0x108:]==new[0x108:]
            assert old[0x104:0x108].hex()=='13059503' and new[0x104:0x108].hex()=='13055503'
            reason='Assertion path string relocation addend: 57 -> 53; disassembly retained'
        elif section in ('.rodata_desc','.rodata.esp_bootloader_desc'):
            reason='Build timestamp/project descriptor metadata'
        else:
            assert section.startswith('.rodata'),(path,section)
            assert old.replace(a.name.encode(),b.name.encode())==new,(path,section)
            reason='Generated build-directory path string only'
        changes[path+'::'+section]=reason
result=dict(result='PASS',scope='All application object .text/.rodata sections; not linked-image equivalence or hardware qualification',objects=len(left),identical_sections=matched,changes=changes,configuration_equal=(a/'sdkconfig').read_bytes()==(b/'sdkconfig').read_bytes())
assert result['configuration_equal']
(root/'normalized-object-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
