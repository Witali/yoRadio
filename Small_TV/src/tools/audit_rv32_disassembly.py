"""Compare ISA-qualified GNU records with original bytes and a saved Ghidra call inventory."""
import argparse
from collections import Counter
import json
from pathlib import Path

from audit_factory_xrefs import Image, LINE, instructions, gp_access, sha, startup_gp
from reverse.rv32_disassembly import compressed_jal_target


def records(text, image):
    """Bind each decoded row to immutable executable bytes before interpreting its mnemonic."""
    raw=instructions(text,image)
    decoded={int(m[1],16):dict(op=m[3],operands=m[4] or '') for line in text.splitlines() if (m:=LINE.match(line))}
    return raw,decoded


def map_hash(rows):
    """Hash addresses, lengths and code bytes independently of paths, spacing and mnemonics."""
    return sha(b''.join(pc.to_bytes(4,'little')+bytes([len(raw)])+raw for pc,raw in sorted(rows.items())))


def audit(factory, old_text, new_text, graph):
    """Check complete exported-byte coverage and retain unresolved call candidates explicitly."""
    image=Image(factory);before,old_ops=records(old_text,image);after,new_ops=records(new_text,image)
    if any(pc not in after or after[pc]!=raw for pc,raw in before.items()):
        raise ValueError('Previously verified instruction bytes or boundaries changed')
    added={pc:raw for pc,raw in after.items() if pc not in before}
    if any(any(raw) for raw in added.values()):raise ValueError('Unexpected nonzero bytes added to old record coverage')
    coverage=[]
    for region in image.sections:
        if not region['execute']:continue
        cursor=region['start'];end=cursor+region['size'];count=0
        for pc,raw in sorted(after.items()):
            if not region['start']<=pc<end:continue
            if pc!=cursor:raise ValueError('Gap or overlap in exported executable bytes')
            cursor+=len(raw);count+=1
        if cursor!=end:raise ValueError('Truncated executable region export')
        coverage.append(dict(name=region['name'],start=region['start'],bytes=region['size'],records=count))
    if graph['program_sha256']!=sha(factory) or graph['language']!='RISCV:LE:32:default':
        raise ValueError('Wrong Ghidra program/ISA')
    blocks={b['name']:b for b in graph['memory_blocks']}
    for region in image.sections:
        if region['execute']:
            block=blocks[region['name']]
            if (int(block['start'],0),block['size'],block['sha256'])!=(region['start'],region['size'],sha(region['data'])):
                raise ValueError('Ghidra executable block differs from original ELF')
    entries={int(f['entry'],0) for f in graph['functions'] if f['space']=='ram'}
    references={}
    for function in graph['functions']:
        for ref in function['references']:
            if ref.get('from_space')=='ram':references.setdefault(int(ref['from'],0),[]).append(ref)
    calls=[]
    for pc,raw in sorted(after.items()):
        word=int.from_bytes(raw,'little')
        if len(raw)!=2 or word&0xe003!=0x2001:continue
        target=compressed_jal_target(word,pc);decoded=new_ops[pc]
        if decoded['op'] not in ('c.jal','jal') or int(decoded['operands'].split()[0],16)!=target:
            raise ValueError('GNU still misdecodes an RV32 C.JAL candidate')
        matches=[]
        for ref in references.get(pc,[]):
            if 'bytes' in ref and image.read(pc,len(bytes.fromhex(ref['bytes'])),True)!=bytes.fromhex(ref['bytes']):
                raise ValueError('Ghidra reference instruction bytes changed')
            if int(ref['to'],0)==target and ref.get('bytes')==raw.hex():matches.append(ref['type'])
        calls.append(dict(pc=pc,bytes_hex=raw.hex(),target=target,old=old_ops.get(pc),new=decoded,
                          target_known=target in entries,ghidra_reference_types=matches))
    gp=startup_gp(image)
    old_gp={pc:gp_access(raw,gp) for pc,raw in before.items() if gp_access(raw,gp)}
    new_gp={pc:gp_access(raw,gp) for pc,raw in after.items() if gp_access(raw,gp)}
    if old_gp!=new_gp:raise ValueError('ISA view changed the prior raw GP-access audit')
    return dict(schema='rv32-disassembly-audit-v1',passed=True,factory_elf_sha256=sha(factory),
        ghidra_graph_sha256=sha(json.dumps(graph,sort_keys=True,separators=(',',':')).encode()),
        old_records=len(before),new_records=len(after),prior_rows_preserved=True,
        added_zero_rows=len(added),added_zero_bytes=sum(len(raw) for raw in added.values()),
        old_instruction_map_sha256=map_hash(before),new_instruction_map_sha256=map_hash(after),
        executable_regions=coverage,exported_code_bytes=sum(row['bytes'] for row in coverage),
        compressed_call_candidates=len(calls),old_mnemonics=dict(Counter(row['old']['op'] if row['old'] else '<missing>' for row in calls)),
        ghidra_functions=len(graph['functions']),ghidra_matched_calls=sum(bool(row['ghidra_reference_types']) for row in calls),
        known_call_targets=sum(row['target_known'] for row in calls),calls=calls,
        unmatched_candidates=[dict(pc=r['pc'],target=r['target'],target_known=r['target_known']) for r in calls if not r['ghidra_reference_types']],
        gp_accesses_preserved=len(new_gp),whole_image_completeness_proved=False,
        candidate_reachability_proved=False,semantic_equivalence_proved=False,physical_hardware_tested=False)


def main():
    """Read immutable originals and save a fresh address-only comparison report."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('elf','before','after','ghidra','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing disassembly audit')
    files=[args.elf,args.before,args.after,args.ghidra,Path(__file__),Path(__file__).with_name('audit_factory_xrefs.py'),
           Path(__file__).parent/'reverse/rv32_disassembly.py']
    pins={str(path.resolve()):sha(path.read_bytes()) for path in files}
    result=audit(args.elf.read_bytes(),args.before.read_text(encoding='utf8'),args.after.read_text(encoding='utf8'),json.loads(args.ghidra.read_bytes()))
    result.update(inputs_sha256=pins,input_roles={name:str(getattr(args,name).resolve()) for name in ('elf','before','after','ghidra')},
                  inputs_unchanged=all(sha(Path(path).read_bytes())==digest for path,digest in pins.items()))
    if not result['inputs_unchanged']:raise ValueError('Disassembly audit input changed')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ('calls','inputs_sha256')}))


if __name__=='__main__':main()
