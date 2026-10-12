import json,hashlib
from pathlib import Path
from elftools.elf.elffile import ELFFile
base=Path('idf/esp32c3-oled-native')
old=base/'build-idf-6.1-r9a97-production-radio/esp-idf'
new=base/'build-idf-6.1-r9a97-decoder-arena/esp-idf'
files=[]
for file in (new/'main/CMakeFiles/__idf_main.dir').rglob('*.obj'):
    if file.name.startswith(('aac_','native_aac_')) or 'vorbis_repair' in file.parts:
        files.append(file)
files+=list((new/'custom_flac').rglob('*.obj'))
report={'scope':'Decoder object code/constants/relocations, not decoded PCM equivalence', 'objects':{}}
def sections(path):
    with path.open('rb') as f:
        elf=ELFFile(f)
        data={s.name:s.data() for s in elf.iter_sections() if s.name.startswith(('.text','.rodata')) and s['sh_size']}
        reloc={}
        for s in elf.iter_sections():
            if s['sh_type'] != 'SHT_RELA': continue
            target=elf.get_section(s['sh_info']).name
            if target not in data: continue
            symbols=elf.get_section(s['sh_link'])
            reloc[target]=[(r['r_offset'],r['r_info_type'],symbols.get_symbol(r['r_info_sym']).name,r['r_addend']) for r in s.iter_relocations()]
    return data,reloc
for path in files:
    relative=path.relative_to(new)
    reference=old/relative
    if not reference.exists():
        matches=list((old/relative.parts[0]).rglob(path.name));assert len(matches)==1
        reference=matches[0]
    left,right=sections(reference),sections(path)
    assert left==right,str(relative)
    report['objects'][str(relative)]={'identical_sections':len(left[0]),'relocation_sections':len(left[1]),
        'candidate_object_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
report['vendor_archive_sha256']=hashlib.sha256(Path('C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec/lib/esp32c3/libesp_audio_codec.a').read_bytes()).hexdigest()
report['result']='PASS'
Path('.build/c3-decoder-arena/codec-object-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',len(files),'decoder objects have identical code, constants and relocation targets')
