"""Read exact-ELF JPEG/RTOS state from a passive synthetic RAM snapshot."""
import argparse
import bisect
import hashlib
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile


def underlying(die):
    """Resolve typedef/qualifier wrappers without guessing a target ABI."""
    while die.tag in ('DW_TAG_typedef','DW_TAG_const_type','DW_TAG_volatile_type','DW_TAG_restrict_type'):
        die=die.get_DIE_from_attribute('DW_AT_type')
    return die


def shape(die,depth=4):
    """Describe bounded fields, including mutex union members, from DWARF."""
    die=underlying(die);size=die.attributes.get('DW_AT_byte_size')
    result=dict(kind=die.tag,bytes=size.value if size else None)
    if die.tag=='DW_TAG_array_type' and size is None:
        element=shape(die.get_DIE_from_attribute('DW_AT_type'),0);count=1
        for child in die.iter_children():
            if child.tag=='DW_TAG_subrange_type':
                bound=child.attributes.get('DW_AT_count')
                count*=bound.value if bound else child.attributes['DW_AT_upper_bound'].value+1
        result['bytes']=element['bytes']*count
    if depth and die.tag in ('DW_TAG_structure_type','DW_TAG_union_type'):
        fields={}
        for member in die.iter_children():
            if member.tag!='DW_TAG_member' or 'DW_AT_name' not in member.attributes:continue
            value=shape(member.get_DIE_from_attribute('DW_AT_type'),depth-1)
            offset=member.attributes.get('DW_AT_data_member_location')
            value['offset']=offset.value if offset else 0
            fields[member.attributes['DW_AT_name'].value.decode()]=value
        result['fields']=fields
    return result


def describe(path):
    """Locate actual private globals/types; reject ambiguous symbol locations."""
    names={'codec','storage','upload','codec_mutex','media_mutex','jobs','foreground_pending','cancel_background'}
    with path.open('rb') as stream:
        elf=ELFFile(stream);symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
        locations={name:[s['st_value'] for s in symbols if s.name==name and s['st_value']] for name in names}
        assert all(len(v)==1 for v in locations.values()),locations
        result=dict(elf_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),globals={},types={})
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                specification=die.get_DIE_from_attribute('DW_AT_specification') if 'DW_AT_specification' in die.attributes else die
                name=specification.attributes.get('DW_AT_name')
                if not name:continue
                name=name.value.decode(errors='replace')
                if die.tag=='DW_TAG_variable' and name in names and 'DW_AT_type' in specification.attributes:
                    location=die.attributes.get('DW_AT_location')
                    if not location:continue
                    expression=bytes(location.value)
                    if len(expression)!=5 or expression[0]!=3 or int.from_bytes(expression[1:],'little')!=locations[name][0]:continue
                    value=shape(specification.get_DIE_from_attribute('DW_AT_type'))
                    value['address']=locations[name][0];result['globals'][name]=value
                if die.tag=='DW_TAG_structure_type' and name in ('tskTaskControlBlock','QueueDefinition'):
                    value=shape(die)
                    if value.get('fields'):result['types'][name]=value
        assert set(result['globals'])==names and set(result['types'])=={'tskTaskControlBlock','QueueDefinition'},(list(result['globals']),list(result['types']))
        result['functions']=sorted([dict(address=s['st_value'],bytes=s['st_size'],name=s.name) for s in symbols
            if s['st_info']['type']=='STT_FUNC' and s['st_value'] and s['st_size']],key=lambda x:x['address'])
        return result


def inspect(layout,ram,base=0x3fca0000):
    """Report fields and stack candidates, not an invented unwound call chain."""
    def integer(address,size):
        assert size in (1,2,4,8) and base<=address<=base+len(ram)-size,(address,size)
        return int.from_bytes(ram[address-base:address-base+size],'little')

    def fields(address,description):
        result={}
        for name,member in description.get('fields',{}).items():
            location=address+member['offset']
            if member.get('fields'):result[name]=fields(location,member)
            elif member['kind'] not in ('DW_TAG_array_type',) and member['bytes'] in (1,2,4,8):
                result[name]=integer(location,member['bytes'])
        return result

    result=dict(globals={},tasks=[])
    for name,value in layout['globals'].items():
        result['globals'][name]=fields(value['address'],value) if value.get('fields') else integer(value['address'],value['bytes'])
    queue=layout['types']['QueueDefinition']
    for name in ('jobs','media_mutex','codec_mutex'):
        address=result['globals'][name]
        if base<=address<base+len(ram)-queue['bytes']:result[name+'_queue']=dict(address=address,fields=fields(address,queue))
    tcb=layout['types']['tskTaskControlBlock'];offset=tcb['fields']['pcTaskName']['offset']
    functions=layout['functions'];starts=[f['address'] for f in functions]
    for name in (b'tv-photo\0',b'clock_display\0',b'httpd\0',b'IDLE\0',b'tcpip\0',b'wifi\0'):
        cursor=0
        while True:
            found=ram.find(name,cursor)
            if found<0:break
            cursor=found+len(name);address=base+found-offset
            if address<base or address+tcb['bytes']>base+len(ram):continue
            values=fields(address,tcb);stack=values.get('pxStack',0);top=values.get('pxTopOfStack',0)
            if not base<=stack<=top<base+len(ram) or values.get('uxPriority',999)>31:continue
            row=dict(name=name[:-1].decode(),address=address,fields=values,stack_candidates=[])
            for at in range(top,min(top+384,base+len(ram)-3),4):
                pointer=integer(at,4);index=bisect.bisect_right(starts,pointer)-1
                if index>=0 and pointer<functions[index]['address']+functions[index]['bytes']:
                    row['stack_candidates'].append(dict(stack_address=at,code_address=pointer,function=functions[index]['name']))
            result['tasks'].append(row)
    return result


def main():
    """Read saved synthetic RAM only; never attach to or modify a physical target."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf',type=Path,required=True)
    parser.add_argument('--ram',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();layout=describe(args.elf)
    result=dict(layout=layout,state=inspect(layout,args.ram.read_bytes()))
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result['state'],indent=2))


if __name__=='__main__':main()
