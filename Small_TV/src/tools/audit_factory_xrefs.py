"""Cross-check complete-database references against immutable RV32 ELF and GNU code.

This inventories known references and supplements missing gp-relative accesses.
It does not prove absence of arbitrary computed aliases or whole-image equivalence.
No firmware strings, settings contents or raw data sections are exported.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re

from elftools.elf.elffile import ELFFile

FACTORY_SHA='8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882'
LINE=re.compile(r'^\s*([0-9a-f]+):\s+([0-9a-f]{2,16})\s+(\S+)(?:\s+(.*))?$')


def sha(data):
    """Identify original code and analysis inputs without exposing their data."""
    return hashlib.sha256(data).hexdigest()


class Image:
    """Read only initialized ELF sections, with explicit instruction permissions."""
    def __init__(self,data):
        assert sha(data)==FACTORY_SHA,'Unexpected factory ELF'
        elf=ELFFile(io.BytesIO(data))
        self.entry=elf['e_entry']
        self.sections=[dict(name=s.name,start=s['sh_addr'],size=s['sh_size'],
            execute=bool(s['sh_flags']&4),data=s.data()) for s in elf.iter_sections()
            if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS']
        self.metadata={'.shstrtab':elf.get_section_by_name('.shstrtab').data(),
            '_elfHeader':data[:elf['e_ehsize']],
            '_elfProgramHeaders':data[elf['e_phoff']:elf['e_phoff']+elf['e_phentsize']*elf['e_phnum']],
            '_elfSectionHeaders':data[elf['e_shoff']:elf['e_shoff']+elf['e_shentsize']*elf['e_shnum']]}

    def read(self,address,size,execute=False):
        """Reject unmapped or data-only bytes being presented as instructions."""
        rows=[s for s in self.sections if s['start']<=address and address+size<=s['start']+s['size']
              and (s['execute'] or not execute)]
        assert len(rows)==1,hex(address)
        row=rows[0];return row['data'][address-row['start']:address-row['start']+size]


def signed12(value):
    """Sign-extend the I/S immediate used by RV32 integer memory instructions."""
    return value-4096 if value&2048 else value


def gp_access(data,gp):
    """Decode a standard integer load/store using x3; leave other instructions alone."""
    if len(data)!=4:return None
    word=int.from_bytes(data,'little');opcode=word&127;funct=(word>>12)&7
    if (word>>15)&31!=3:return None
    if opcode==3 and funct in (0,1,2,4,5):
        immediate=signed12(word>>20);kind='READ';width={0:1,1:2,2:4,4:1,5:2}[funct]
        register=(word>>7)&31
    elif opcode==35 and funct in (0,1,2):
        immediate=signed12(((word>>25)<<5)|((word>>7)&31));kind='WRITE';width=1<<funct
        register=(word>>20)&31
    else:return None
    return dict(address=hex((gp+immediate)&0xffffffff),kind=kind,width=width,value_register=register)


def startup_gp(image):
    """Derive gp from the real startup AUIPC/ADDI pair, never a decompiler alias."""
    pc=0x4038046c;data=image.read(pc,8,True)
    upper=int.from_bytes(data[:4],'little');lower=int.from_bytes(data[4:],'little')
    assert upper&127==23 and (upper>>7)&31==3
    assert lower&127==19 and (lower>>7)&31==3 and (lower>>15)&31==3 and (lower>>12)&7==0
    return (pc+(upper&0xfffff000)+signed12(lower>>20))&0xffffffff


def instructions(text,image):
    """Require every GNU instruction record to match actual executable ELF bytes."""
    rows={}
    for line in text.splitlines():
        match=LINE.match(line)
        if not match:continue
        address=int(match[1],16);encoded=match[2]
        assert len(encoded)%2==0
        data=bytes.fromhex(encoded)[::-1]
        assert image.read(address,len(data),True)==data,hex(address)
        assert address not in rows
        rows[address]=data
    assert len(rows)>200000,'Incomplete executable disassembly'
    return rows


def audit(ghidra,text,elf,selected):
    """Validate database bytes and compare independently discovered gp accesses."""
    image=Image(elf);assert ghidra['schema_version']==1 and ghidra['program_sha256']==FACTORY_SHA
    assert ghidra['semantic_equivalence_proved'] is False and ghidra['whole_image_completeness_proved'] is False
    assert ghidra['language']=='RISCV:LE:32:default'
    blocks={b['name']:b for b in ghidra['memory_blocks'] if b['initialized']}
    # Ghidra also maps ELF headers/string-table in its non-guest OTHER space.
    assert set(blocks)=={s['name'] for s in image.sections}|set(image.metadata)
    for name,data in image.metadata.items():
        row=blocks[name];assert not row['execute'] and row['size']==len(data) and row['sha256']==sha(data)
    for section in image.sections:
        row=blocks[section['name']]
        assert int(row['start'],0)==section['start'] and row['size']==section['size']
        assert row['sha256']==sha(section['data']) and row['execute']==section['execute']
    rows=instructions(text,image);gp=startup_gp(image)
    decoded={pc:gp_access(data,gp) for pc,data in rows.items() if gp_access(data,gp)}
    observed={int(row['from'],0):row for row in ghidra['gp_accesses']}
    assert len(observed)==len(ghidra['gp_accesses'])
    # Three real instruction sites are absent from the old database. Preserve
    # the discrepancy explicitly; this audit must not certify full coverage.
    gaps=set(decoded)-set(observed)
    assert not set(observed)-set(decoded),'Ghidra-only gp instruction needs investigation'
    assert gaps=={0x42058280,0x420662da,0x420757d2},'New database coverage gap needs review'
    for pc,row in observed.items():assert bytes.fromhex(row['bytes'])==rows[pc]
    checked=data_checked=metadata_checked=entry_checked=0;types=Counter();outside=set();pointers=[]
    functions=ghidra['functions'];entries={(f['space'],f['entry']) for f in functions}
    assert len(entries)==len(functions)
    for function in functions:
        if function['space']=='ram' and function['entry'] not in selected:outside.add(function['entry'])
        for ref in function['references']:
            assert ref['to']==function['entry'] and ref['to_space']==function['space']
            types[ref['type']]+=1
            if 'bytes' in ref:
                pc=int(ref['from'],0);data=bytes.fromhex(ref['bytes'])
                assert ref['from_space']=='ram' and image.read(pc,len(data),True)==data
                assert rows.get(pc)==data;checked+=1
            elif ref['type']=='DATA':
                offset=int(ref['from'],0)
                if ref['from_space']=='ram':
                    value=image.read(offset,4);data_checked+=1
                else:
                    value=image.metadata[ref['from_space']][offset:offset+4];metadata_checked+=1
                    assert len(value)==4
                assert int.from_bytes(value,'little')==int(ref['to'],0),'Wrong literal function pointer'
            else:
                assert ref['type']=='EXTERNAL' and ref['from_space']=='Entry Point'
                assert int(ref['to'],0)==image.entry;entry_checked+=1
            if ref['type'] in ('DATA','PARAM') and function['space']=='ram':
                pointers.append(dict(target=function['entry'],source=ref['from'],type=ref['type']))
    targets={}
    for name,row in ghidra['targets'].items():
        target=int(row['address'],0);refs=row['references']
        for ref in refs:
            assert ref['to']==row['address'] and ref['to_space']=='ram'
            if 'bytes' in ref:assert rows[int(ref['from'],0)]==bytes.fromhex(ref['bytes'])
        supplement=[]
        for pc,access in decoded.items():
            start=int(access['address'],0)
            if start<=target<start+access['width']:
                supplement.append(dict(from_address=hex(pc),bytes=rows[pc].hex(),
                    **access,owner=observed.get(pc,{}).get('owner',{})))
        targets[name]=dict(address=row['address'],database_references=refs,gp_accesses=supplement)
    assert gp==0x3fcb49c0
    assert {r['from'] for r in targets['timer_network']['database_references']}=={'0x42008356'}
    assert {r['from'] for r in targets['timer_slow']['database_references']}=={'0x42008382'}
    assert {r['from'] for r in targets['jpeg_flash_output']['database_references']}=={'0x4200c432','0x4200c54c'}
    assert {r['from_address'] for r in targets['browser_time_active_gp_minus_2000']['gp_accesses']}=={
        '0x4200ee60','0x4200ee6c','0x4200eef8','0x4200efd2'}
    return dict(schema_version=1,passed=True,semantic_equivalence_proved=False,
        whole_image_completeness_proved=False,factory_elf_sha256=FACTORY_SHA,
        ghidra_functions=len(functions),unselected_ram_functions=len(outside),
        ghidra_instruction_count=ghidra['instruction_count'],gnu_instruction_records=len(rows),
        gnu_instruction_map_sha256=sha(b''.join(pc.to_bytes(4,'little')+bytes([len(data)])+data
            for pc,data in sorted(rows.items()))),
        executable_sections=[{k:v for k,v in s.items() if k!='data'} for s in image.sections if s['execute']],
        gp=hex(gp),gp_memory_instructions=len(decoded),verified_code_references=checked,
        verified_literal_function_pointers=data_checked,verified_metadata_references=metadata_checked,
        verified_synthetic_entry_references=entry_checked,
        gp_coverage_agrees=False,verified_common_gp_instructions=len(observed),
        database_gp_gaps=[dict(from_address=hex(pc),bytes=rows[pc].hex(),**decoded[pc]) for pc in sorted(gaps)],
        function_reference_types=dict(sorted(types.items())),pointer_candidate_edges=len(pointers),
        pointer_targets_outside_selected=sorted({p['target'] for p in pointers if p['target'] not in selected}),
        review_window=['0x4200826a','0x42011040'],
        pointer_targets_in_review_window_outside_selected=sorted({p['target'] for p in pointers
            if p['target'] not in selected and 0x4200826a<=int(p['target'],0)<0x42011040}),
        targets=targets,limitations=[
            'Ghidra discovered functions and pointers are analysis results, not a proof that every function was found.',
            'The supplement covers x3-based standard 32-bit integer loads/stores; arbitrary computed aliases remain open.',
            'No dead-code claim follows from an absent direct reference. Bulk settings I/O is a separate alias path.',
            'No guest execution, physical hardware, whole-image semantic or timing equivalence acceptance.'])


def main():
    """Run read-only code tools and save a new, bounded address-only audit artifact."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf',type=Path,required=True)
    parser.add_argument('--ghidra',type=Path,required=True)
    parser.add_argument('--assembly',type=Path,required=True,help='Full GNU executable-section disassembly')
    parser.add_argument('--symbols',type=Path,default=Path(__file__).resolve().parents[1]/'symbol-map.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists(),'Preserve earlier evidence'
    selected={r['address'] for r in json.loads(args.symbols.read_text())['functions']}
    result=audit(json.loads(args.ghidra.read_text()),args.assembly.read_text(),args.elf.read_bytes(),selected)
    result['inputs_sha256']={str(p.resolve()):sha(p.read_bytes()) for p in (Path(__file__),args.elf,args.ghidra,args.assembly,args.symbols)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('targets','inputs_sha256','pointer_targets_outside_selected','limitations','executable_sections')}))


if __name__=='__main__':main()
