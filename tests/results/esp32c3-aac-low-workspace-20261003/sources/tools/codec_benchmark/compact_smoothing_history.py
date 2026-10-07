#!/usr/bin/env python3
"""Four retained SBR FIR rows; native five-tap arithmetic uses a temporary fifth."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
import compact_high_history as high

SPECS=copy.deepcopy(high.SPECS)
SPECS['init_sbr_dec'] += [
 (0x4a,'50070313','scale:matrix_size:1','noise matrix relative to gain matrix'),
 (0x4e,'20188893','scale:gain_exponent_tail:1','gain exponent address after first immediate'),
 (0x52,'70180813','scale:noise_exponent_tail:1','noise exponent address after first immediate')]
SPECS['ps_allocate_decoder'] += [
 (0x7a,'6aa1','hi:ps_allpass_qmf','allpass QMF workspace high after channel compaction')]

def build(archive,output,ar,objcopy,layout_object):
    prior=high.SPECS
    try:
        high.SPECS=SPECS
        evidence=high.build(archive,output,ar,objcopy,layout_object)
    finally:
        high.SPECS=prior
    obj=output/'sbr_dec.c.obj'
    elf=ELFFile(io.BytesIO(obj.read_bytes()))
    rels=elf.get_section_by_name('.rela.text.sbr_dec')
    symbols=elf.get_section(rels['sh_link'])
    calls=[r['r_offset'] for r in rels.iter_relocations()
           if symbols.get_symbol(r['r_info_sym']).name=='calc_sbr_envelope' and r['r_info_type']==19]
    if sorted(calls)!=[0x23c,0xc3a]:
        raise ValueError('Expected both complex and real-only envelope call sites')
    subprocess.run([str(objcopy),'--redefine-sym',
                    'calc_sbr_envelope=aac_smoothing_history_envelope',str(obj)],check=True)
    evidence['envelope_calls']=[hex(x) for x in calls]
    evidence['functions']['sbr_dec']['output_sha256']=hashlib.sha256(obj.read_bytes()).hexdigest()
    evidence['scope']='Four persistent smoothing rows plus temporary fifth; QEMU-only qualification'
    (output/'audit.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
    return evidence

if __name__=='__main__':
    p=argparse.ArgumentParser(__doc__)
    for name in ('archive','output','ar','objcopy','layout-object'):
        p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(build(a.archive,a.output,a.ar,a.objcopy,a.layout_object)['compiler_layout']))
