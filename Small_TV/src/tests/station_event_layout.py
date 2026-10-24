"""Resolve native station event constants and payload layout from the exact ELF."""
import hashlib

from elftools.elf.elffile import ELFFile
from photo_target_state import shape


OBJECTS = {'IP_EVENT':4,'WIFI_EVENT':4,'connected':1,'ap_active':1,
           'station_retries':4,'last_station_address':4}
ENUMS = ('WIFI_EVENT_STA_START','WIFI_EVENT_STA_DISCONNECTED','IP_EVENT_STA_GOT_IP')


def describe(path):
    """Reject ambiguous types/constants instead of assuming a different SDK's ABI."""
    with path.open('rb') as stream:
        elf=ELFFile(stream);symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
        objects={}
        for name,size in OBJECTS.items():
            values={(s['st_value'],s['st_size']) for s in symbols if s.name==name and s['st_value']}
            assert len(values)==1 and next(iter(values))[1]==size,(name,values)
            objects[name]=dict(address=next(iter(values))[0],bytes=size)
        constants={name:set() for name in ENUMS};layouts=[]
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name=die.attributes.get('DW_AT_name')
                if not name:continue
                name=name.value.decode(errors='replace')
                if die.tag=='DW_TAG_enumerator' and name in constants:
                    constants[name].add(die.attributes['DW_AT_const_value'].value)
                if name=='ip_event_got_ip_t' and die.tag=='DW_TAG_typedef':layouts.append(shape(die))
        assert layouts and all(value==layouts[0] for value in layouts)
        assert all(len(values)==1 for values in constants.values()),constants
    ip=layouts[0];info=ip['fields']['ip_info'];address=info['fields']['ip']['fields']['addr']
    offset=info['offset']+info['fields']['ip']['offset']+address['offset']
    assert address['bytes']==4 and 0<=offset<=ip['bytes']-4
    return dict(elf_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),objects=objects,
        constants={name:next(iter(values)) for name,values in constants.items()},
        got_ip=ip,ip_offset=offset,ip_bytes=4)
