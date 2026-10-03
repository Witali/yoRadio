#!/usr/bin/env python3
"""Pinned RV32 low-QMF workspace relocation; native DSP arithmetic is retained.

Every new address comes from the target compiler. Four-byte low-base ADDIs
become four-byte loads of call-local, frame-relative bindings. The preceding
LUIs are harmless overwritten values; instruction positions never move.
"""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import struct
from elftools.elf.elffile import ELFFile
import compact_smoothing_history as smoothing

SPECS=copy.deepcopy(smoothing.SPECS)

def add(symbol, expression, sites):
    for offset, word in sites:
        SPECS[symbol].append((offset,word,expression,'low workspace: '+expression))

add('init_sbr_dec','hi:frame_table_0',[(0xe,'6799')])
add('init_sbr_dec','hi:frame_table_end',[(0x10,'6e19')])
add('sbr_open','hi:channel_size',[(0x1c,'6999'),(0x4a,'6619')])
add('sbr_open','lo:left_header',[(0x60,'0c840713')])
add('sbr_open','lo:left_sample_mode',[(0x80,'0d4b2583'),(0xbe,'0d242a23')])
add('sbr_open','lo:left_frame',[(0x84,'00840693')])
add('sbr_open','lo:left_startup',[(0x9a,'71242a23')])
add('sbr_read_data','lo:left_header',[(0x70,'0c848513'),(0x90,'0c848793')])
add('sbr_read_data','lo:left_header_end',[(0x96,'10848693')])
add('sbr_read_data','lo:left_sample_mode',[(0xcc,'0d44a603'),(0x140,'0d44a603')])
add('sbr_read_data','lo:left_frame',[(0xc8,'00848413'),(0x106,'00848513'),
                                  (0x118,'00848413'),(0x144,'00848413')])
add('sbr_read_data','lo:frame_sync',[(0xe0,'fef42e23')])
add('sbr_read_data','hi:channel_size',[(0xe4,'6799')])
add('sbr_read_data','hi:right_header',[(0x88,'6719')])
add('sbr_read_data','hi:right_frame',[(0xfc,'6599')])
add('sbr_applied','lo:left_frame',[(0x1e,'00850993'),(0x184,'00840993'),
                                (0x1d2,'00840993'),(0x254,'00840993'),(0x2aa,'00840993')])
add('sbr_applied','lo:left_coupling',[(0x1ee,'18042683'),(0x2c6,'18042683')])
add('sbr_applied','hi:right_synthesis',[(0x52,'6729')])
add('sbr_applied','hi:left_real',[(0x6a,'6591'),(0xb4,'6e91')])
add('sbr_applied','lo:left_imag',[(0x7e,'9af5ac23'),(0xcc,'9a67ac23')])
add('sbr_applied','hi:right_status',[(0xfc,'6799'),(0x26a,'6699')])
add('sbr_applied','hi:right_frame',[(0x104,'6619'),(0x1fa,'6519'),(0x284,'6699')])
add('sbr_applied','hi:right_coupling',[(0x21a,'6699')])
for field,site,word in [('ps_peak',0x24,'661d'),('ps_energy',0x26,'669d'),
                        ('ps_difference',0x28,'671d'),('ps_hybrid',0x2a,'679d')]:
    add('ps_allocate_decoder','hi:'+field,[(site,word)])
add('sbr_dec','hi:frame_real',[(0x3e,'6a11'),(0x10e,'6411'),(0x30e,'6711'),
                             (0x47e,'6a11'),(0x664,'6a11'),(0x6e4,'6c91'),(0x8fe,'6791')])
add('sbr_dec','lo:frame_imag',[(0x14e,'9b042683'),(0x1be,'9b042603'),(0x33a,'9b092583'),
                             (0x49c,'9b0a2583'),(0x684,'9b0a2503'),(0x834,'9b0ca703'),
                             (0x960,'9b07a583'),(0xb36,'9b0a2503')])
add('sbr_dec','hi:frame_imag',[(0x95c,'6791')])
add('sbr_dec','hi:frame_imag_history',[(0x4a0,'6511'),(0x964,'6511'),(0xb3a,'6591')])
add('sbr_dec','hi:frame_synthesis',[(0x4ca,'6591'),(0x6a6,'6591'),(0x8a2,'6511'),
                                  (0xc46,'6591'),(0xcdc,'6511')])
for field,site,word in [('frame_table_0',0x1c4,'6799'),('frame_table_3',0x1e4,'6519'),
                        ('frame_table_2',0x1ea,'6699'),('frame_table_1',0x1ec,'6719')]:
    add('sbr_dec','hi:'+field,[(site,word)])

LOW_BASES={
    'real': [(0x68,'1b0c8c93'),(0x13a,'1b050513'),(0x262,'1b078793'),
             (0x424,'1b0a0a13'),(0x6e6,'1b078793'),(0x8c8,'1b048493'),(0xb58,'1b050513')],
    'imag': [(0x6c,'5b0a0a13'),(0x136,'5b058593'),(0x26c,'5b0a0a13'),
             (0x3a8,'5b0f0f13'),(0x430,'5b0b0b13'),(0x7aa,'5b070713'),(0x928,'5b048493')],
}

def read_slots(data):
    elf=ELFFile(io.BytesIO(data))
    symbols=elf.get_section_by_name('.symtab').get_symbol_by_name('aac_low_slots')
    if not symbols or len(symbols)!=1 or symbols[0]['st_size']!=16:
        raise ValueError('Missing low-QMF compiler binding descriptor')
    symbol=symbols[0]; section=elf.get_section(symbol['st_shndx'])
    offset=symbol['st_value']-section['sh_addr']
    original_real,real,original_imag,imag=struct.unpack_from('<iiii',section.data(),offset)
    if (original_real,original_imag)!=(0x11b0,0x25b0) or not (-2048<=real<imag<0):
        raise ValueError('Unexpected original matrix or signed binding offsets')
    return {'real':real,'imag':imag}

def bind_low_bases(data,slots):
    elf=ELFFile(io.BytesIO(data)); section=elf.get_section_by_name('.text.sbr_dec')
    if section is None:raise ValueError('Missing sbr_dec section')
    code=section.data(); changes=[]; result=bytearray(data)
    relocations=elf.get_section_by_name('.rela.text.sbr_dec')
    for part,sites in LOW_BASES.items():
        for offset,expected in sites:
            old=int(expected,16)
            if int.from_bytes(code[offset:offset+4],'little')!=old or old&0x707f!=0x13:
                raise ValueError(f'Low base instruction mismatch at {offset:#x}')
            if any(offset<=rel['r_offset']<offset+4 for rel in relocations.iter_relocations()):
                raise ValueError('Low base binding overlaps a relocation')
            # LW rd, compiler_slot(s3). Every audited setup has its frame in s3.
            new=((slots[part]&0xfff)<<20)|(19<<15)|(2<<12)|(old&0xf80)|0x03
            position=section['sh_offset']+offset
            result[position:position+4]=new.to_bytes(4,'little')
            changes.append(dict(offset=hex(offset),original=expected,replacement=f'{new:08x}',
                                meaning=f'{part} call-local frame-relative binding',slot=slots[part]))
    return bytes(result),changes

def build(archive,output,ar,objcopy,layout_object):
    slots=read_slots(layout_object.read_bytes())
    prior=smoothing.SPECS
    try:
        smoothing.SPECS=SPECS
        evidence=smoothing.build(archive,output,ar,objcopy,layout_object)
    finally:
        smoothing.SPECS=prior
    layout=evidence['compiler_layout']
    # Native shared LUI bases still serve these adjacent fields.
    for fields in [('frame_real','frame_imag','frame_real_history'),
                   ('left_real','left_imag'),('right_high_real','right_high_imag'),
                   ('ps_pointer','ps_flag')]:
        if len({(layout[name][1]+0x800)>>12 for name in fields})!=1:
            raise ValueError('Shared upper address no longer valid: '+str(fields))
    obj=output/'sbr_dec.c.obj'
    data,changes=bind_low_bases(obj.read_bytes(),slots)
    obj.write_bytes(data)
    evidence['functions']['sbr_dec']['patches']+=changes
    evidence['functions']['sbr_dec']['output_sha256']=hashlib.sha256(data).hexdigest()
    evidence['low_bindings']=slots
    evidence['scope']='QEMU low-QMF stack workspace; requires full PCM/pointer/reset/stack qualification'
    (output/'audit.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
    return evidence

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__)
    for name in ('archive','output','ar','objcopy','layout-object'):
        p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    result=build(a.archive,a.output,a.ar,a.objcopy,a.layout_object)
    print(json.dumps({'channel_bytes':result['compact_channel'],
                      'full_owner_bytes':result['compact_owner'],'bindings':result['low_bindings']}))
