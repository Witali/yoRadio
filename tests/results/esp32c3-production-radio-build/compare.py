import hashlib,json
from pathlib import Path
from elftools.elf.elffile import ELFFile
root=Path('.build/c3-production-radio')
a=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-http-txrelease')
b=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-production-radio')
assert (a/'sdkconfig').read_bytes()==(b/'sdkconfig').read_bytes()
def sections(base):
    result={}
    for path in base.rglob('*.obj'):
        if 'bootloader' in path.relative_to(base).parts:continue
        with path.open('rb') as f:
            result[path.relative_to(base).as_posix()]={s.name:hashlib.sha256(s.data()).hexdigest() for s in ELFFile(f).iter_sections() if s.name.startswith(('.text','.rodata')) and s['sh_size']}
    return result
left,right=sections(a),sections(b)
only_left=sorted(left.keys()-right.keys());only_right=sorted(right.keys()-left.keys())
changes={p:[s for s in left[p].keys()|right[p].keys() if left[p].get(s)!=right[p].get(s)] for p in left.keys()&right.keys() if left[p]!=right[p]}
result=dict(config_equal=True,objects_before=len(left),objects_after=len(right),only_before=only_left,only_after=only_right,changed_sections=changes)
(root/'object-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
