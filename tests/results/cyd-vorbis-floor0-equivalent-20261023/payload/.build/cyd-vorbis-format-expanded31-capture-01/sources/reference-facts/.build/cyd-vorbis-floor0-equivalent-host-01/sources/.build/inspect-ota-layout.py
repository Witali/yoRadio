"""Read actual target DWARF sizes; run with the pinned SDK Python environment."""
import argparse
import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

p=argparse.ArgumentParser()
p.add_argument('elf',type=Path)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
names={'ota_http_io_t','native_ota_form_t','native_ota_sink_t','play_command_t','audio_maintenance_token_t'}
sizes={}
with a.elf.open('rb') as stream:
    elf=ELFFile(stream)
    assert elf.has_dwarf_info()
    for cu in elf.get_dwarf_info().iter_CUs():
        for die in cu.iter_DIEs():
            name=die.attributes.get('DW_AT_name')
            if not name or not isinstance(name.value,bytes):continue
            name=name.value.decode(errors='replace')
            if name not in names:continue
            target=die
            seen=set()
            while 'DW_AT_byte_size' not in target.attributes and 'DW_AT_type' in target.attributes:
                assert target.offset not in seen
                seen.add(target.offset)
                target=target.get_DIE_from_attribute('DW_AT_type')
            if 'DW_AT_byte_size' in target.attributes:
                size=target.attributes['DW_AT_byte_size'].value
                assert name not in sizes or sizes[name]==size,(name,sizes.get(name),size)
                sizes[name]=size
    symbols=[]
    for symbol in elf.get_section_by_name('.symtab').iter_symbols():
        if (symbol.name.startswith(('s_maintenance_','s_last_command')) or
            symbol.name in {'s_last_url','s_last_codec','s_last_generation','s_stream_retry_pending'}) and symbol['st_size']:
            symbols.append({'name':symbol.name,'bytes':symbol['st_size'],'section':symbol['st_shndx']})
assert {'ota_http_io_t','native_ota_form_t','native_ota_sink_t'}<=sizes.keys(),sizes
result={'elf':str(a.elf),'elf_sha256':hashlib.sha256(a.elf.read_bytes()).hexdigest(),'target_machine':elf['e_machine'],'target_types_bytes':sizes,
        'selected_static_symbols':symbols,'scope':'Actual compiler target layout. No allocator overhead, TLS/HTTPD buffers, linker padding, stack high-water, physical heap admission or peak-RAM claim.'}
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
