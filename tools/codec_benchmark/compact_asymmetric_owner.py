#!/usr/bin/env python3
"""Asymmetric SBR channel extents, common table prefix, unchanged native DSP."""
import argparse,copy,hashlib,json
from pathlib import Path
import compact_low_workspace as low
import compact_sbr_tables as base

SPECS=copy.deepcopy(low.SPECS)
for symbol,rows in SPECS.items():
    revised=[]
    for offset,word,expression,meaning in rows:
        if symbol=='sbr_read_data' and offset in (0xbe,0xc0):
            expression=expression.replace(':ps_data',':frame_cursor_end')
            meaning='comparison-only reset cursor end; not the PS object'
        if symbol in ('init_sbr_dec','sbr_dec') and expression.startswith('hi:frame_table_'):
            expression='scale:frame_table_upper:1'
            meaning='zero upper base for signed prefix-table displacement'
        revised.append((offset,word,expression,meaning))
    SPECS[symbol]=revised

def prefix_immediate(word,width,value):
    # Prefix addresses fit signed LO12. C.LUI cannot represent a zero upper
    # base: C.LI rd,0 preserves width and clears exactly the same register.
    if width==2 and value==0 and word&0xe003==0x6001:
        rd=(word>>7)&31
        if rd in (0,2):raise ValueError('Invalid prefix-base register')
        return (rd<<7)|0x4001
    return ORIGINAL_IMMEDIATE(word,width,value)

ORIGINAL_IMMEDIATE=base.immediate

def build(archive,output,ar,objcopy,layout_object):
    previous_specs,previous_immediate=low.SPECS,base.immediate
    try:
        low.SPECS=SPECS;base.immediate=prefix_immediate
        evidence=low.build(archive,output,ar,objcopy,layout_object)
    finally:
        low.SPECS=previous_specs;base.immediate=previous_immediate
    evidence['scope']='QEMU asymmetric owner: common prefix tables, left frame only, right PS overlay'
    evidence['native_open']='Unused: the existing typed initializer handles both first open and PS-preserving reopen'
    (output/'audit.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
    return evidence

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('archive','output','ar','objcopy','layout-object'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=build(args.archive,args.output,args.ar,args.objcopy,args.layout_object)
    print(json.dumps({'left_extent':result['compact_channel'],'full_owner':result['compact_owner']}))
