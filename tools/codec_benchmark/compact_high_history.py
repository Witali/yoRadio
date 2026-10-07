#!/usr/bin/env python3
"""Build-local pinned AAC object copies for an actually smaller QMF owner.

The native arithmetic and call order stay intact. Typed compiler fields replace
address immediates. Only sbr_dec's memmove symbol is redirected, with its entire
relocation inventory pinned below; the helper recognizes six history transfers
and forwards all other copies unchanged.
"""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
import compact_sbr_tables as base

SPECS=copy.deepcopy(base.PATCH_SPECS)
SPECS['init_sbr_dec'] += [
 (0x8,'6715','hi:frame_gain','gain storage high'),
 (0x18,'cb870713','lo:frame_gain','gain storage low'),
 (0x1c,'0b878793','lo:frame_table_0','smoothing table base'),
 (0x20,'0cce0e13','lo:frame_table_end','five-row initialization end')]
SPECS['sbr_applied'] += [
 (0x7a,'e315ae23','lo:left_real','left high real pointer for PS'),
 (0xc8,'e3c7ae23','lo:left_real','left high real pointer for SBR'),
 (0xf6,'6e91','scale:right_high_delta:1','shared right pointer upper-base difference')]
SPECS['ps_allocate_decoder'] += [
 (0x82,'64a5','hi:ps_delay_real','main real history high'),
 (0x84,'6925','hi:ps_delay_imag','main imaginary history high'),
 (0x86,'6ba5','hi:ps_real_pointers','real delay table high'),
 (0x88,'6b25','hi:ps_imag_pointers','imaginary delay table high'),
 (0xfc,'67a5','hi:ps_real_pointers','real delay table cursor high')]
SPECS['sbr_dec'] += [
 (0x40,'e38a0793','lo:frame_real_history','real history identity token'),
 (0x46,'e34a2503','lo:frame_real','initial real working pointer'),
 (0x114,'e3442603','lo:frame_real','HF generation real working pointer'),
 (0x1c6,'0b878793','lo:frame_table_0','smoothing pointer table zero'),
 (0x1cc,'e3442583','lo:frame_real','complex envelope real working pointer'),
 (0x314,'e3492583','lo:frame_real','PS working real row'),
 (0x482,'e34a2583','lo:frame_real','PS real history save source'),
 (0x4a2,'9b450513','lo:frame_imag_history','PS imaginary history save token'),
 (0x4ce,'2b858593','lo:frame_synthesis','PS synthesis history load'),
 (0x670,'e34a2503','lo:frame_real','inactive SBR high real zeroing'),
 (0x6b2,'2b858593','lo:frame_synthesis','SBR synthesis history load'),
 (0x772,'e34ca703','lo:frame_real','complex SBR real synthesis row'),
 (0x8a4,'2b850513','lo:frame_synthesis','SBR synthesis history save'),
 (0x902,'e347a583','lo:frame_real','SBR real history save source'),
 (0x96c,'9b450513','lo:frame_imag_history','SBR imaginary history save token'),
 (0xa18,'e34ca683','lo:frame_real','real SBR synthesis row'),
 (0xb3c,'9b458593','lo:frame_imag_history','imaginary history load token'),
 (0xb60,'6a15','hi:frame_alias','real SBR alias workspace high'),
 (0xb6c,'bb8a0a13','lo:frame_alias','real SBR alias workspace low'),
 (0xbe0,'e3442583','lo:frame_real','real envelope working pointer'),
 (0xc4a,'2b858593','lo:frame_synthesis','PS downsampled synthesis load'),
 (0xcde,'2b850513','lo:frame_synthesis','PS synthesis history save')]

HISTORY_CALLS={0x54:'load_real',0xb46:'load_imag',0x494:'PS_store_real',
               0x4ae:'PS_store_imag',0x914:'SBR_store_real',0x978:'SBR_store_imag'}
OTHER_MEMMOVES={0x452,0x468,0x4e0,0x506,0x524,0x5b0,0x5c6,0x6ca,0x8ba,
               0x8e8,0x946,0x9b6,0xb10,0xb2c,0xc5a,0xcb0,0xcce,0xcea,0xd0e,0xda4,0xdb4}

def redirect_copies(path,objcopy):
    elf=ELFFile(io.BytesIO(path.read_bytes()))
    rels=elf.get_section_by_name('.rela.text.compact5_sbr_dec')
    # objcopy renames symbols, not the original section names.
    if rels is None: rels=elf.get_section_by_name('.rela.text.sbr_dec')
    symbols=elf.get_section(rels['sh_link'])
    found={r['r_offset'] for r in rels.iter_relocations()
           if symbols.get_symbol(r['r_info_sym']).name=='memmove' and r['r_info_type']==19}
    if found != set(HISTORY_CALLS)|OTHER_MEMMOVES:
        raise ValueError('sbr_dec memmove relocation inventory changed')
    subprocess.run([str(objcopy),'--redefine-sym','memmove=aac_high_history_memmove',str(path)],check=True)
    return {hex(k):HISTORY_CALLS.get(k,'forward unchanged') for k in sorted(found)}

def build(archive,output,ar,objcopy,layout_object):
    # Reuse the fail-closed instruction patcher. These globals are private to
    # this standalone build invocation, never used by the original profile.
    prior=base.PATCH_SPECS
    try:
        base.PATCH_SPECS=SPECS
        evidence=base.build(archive,output,ar,objcopy,layout_object)
    finally:
        base.PATCH_SPECS=prior
    obj=output/'sbr_dec.c.obj'
    evidence['history_copy_calls']=redirect_copies(obj,objcopy)
    evidence['functions']['sbr_dec']['output_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
    evidence['scope']='QEMU high-QMF persistent storage experiment; guarded PCM/reset qualification required'
    (output/'audit.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
    return evidence

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__)
    for name in ('archive','output','ar','objcopy','layout-object'):
        p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(build(a.archive,a.output,a.ar,a.objcopy,a.layout_object)['compiler_layout']))
