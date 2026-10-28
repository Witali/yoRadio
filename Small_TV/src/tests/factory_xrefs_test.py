"""Reject corrupted full-image xref evidence against actual immutable factory code."""
import argparse
import copy
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import audit,sha


def check_controls(ghidra,text,elf,selected):
    """Mutate real observations, not a miniature graph which mirrors the implementation."""
    rejected=[]
    for case in ('wrong-program','changed-block','missing-gp','changed-gp-bytes',
                 'changed-code-reference','changed-data-pointer','missing-timer-store','unknown-mapped-block','changed-elf'):
        wrong=copy.deepcopy(ghidra);image=elf
        if case=='wrong-program':wrong['program_sha256']='00'*32
        elif case=='changed-block':wrong['memory_blocks'][0]['sha256']='00'*32
        elif case=='missing-gp':wrong['gp_accesses'].pop()
        elif case=='changed-gp-bytes':wrong['gp_accesses'][0]['bytes']='00'*4
        elif case=='changed-code-reference':
            next(r for f in wrong['functions'] for r in f['references'] if 'bytes' in r)['bytes']='00'*4
        elif case=='changed-data-pointer':
            next(r for f in wrong['functions'] for r in f['references']
                if 'bytes' not in r and r['type']=='DATA' and r['from_space']=='ram')['from']='0x00000000'
        elif case=='missing-timer-store':wrong['targets']['timer_network']['references']=[]
        elif case=='unknown-mapped-block':
            row=copy.deepcopy(wrong['memory_blocks'][0]);row['name']='unexpected-extra';wrong['memory_blocks'].append(row)
        else:image=elf[:-1]+bytes([elf[-1]^1])
        try:audit(wrong,text,image,selected)
        except (AssertionError,ValueError,KeyError):rejected.append(case)
        else:raise AssertionError('Invalid full-image evidence accepted: '+case)
    return rejected


def replay(proof_path,assembly,elf,root,revision=None):
    """Check exact archived producers and rederive the audit from local code bytes."""
    proof=json.loads(proof_path.read_text());assert proof['schema_version']==1 and proof['passed']
    assert not any(proof[k] for k in ('whole_image_completeness_proved','semantic_equivalence_proved','physical_hardware_tested'))
    files={}
    for row in proof['files']:
        path=(proof_path.parent/row['file']).resolve();assert path.is_relative_to(proof_path.parent.resolve())
        packed=path.read_bytes();assert sha(packed)==row['gzip_sha256'];data=gzip.decompress(packed)
        assert sha(data)==row['sha256'] and len(data)==row['bytes'];assert row['source'] not in files
        files[row['source']]=data
    if revision:
        from verify_photo_format_matrix_evidence import source_hashes
        actual=source_hashes(root,proof['source_pins'],revision)
    else:actual={name:sha((root/name).read_bytes()) for name in proof['source_pins']}
    assert actual==proof['source_pins']
    for name,digest in proof['source_pins'].items():assert sha(files['producer/'+name])==digest
    ghidra=json.loads(files['ghidra.json']);selected={r['address'] for r in json.loads(files['producer/Small_TV/src/symbol-map.json'])['functions']}
    result=audit(ghidra,assembly.read_text(),elf.read_bytes(),selected)
    original=json.loads(files['audit.json']);original.pop('inputs_sha256')
    assert result==original
    controls=check_controls(ghidra,assembly.read_text(),elf.read_bytes(),selected)
    assert controls==proof['rejected_controls']
    return dict(passed=True,functions=result['ghidra_functions'],verified_code_references=result['verified_code_references'],
        gp_instructions=result['gp_memory_instructions'],database_gp_gaps=result['database_gp_gaps'],
        rejected_controls=controls,whole_image_completeness_proved=False)


def main():
    """Use either an actual export or its archived proof; never change the analysis DB."""
    parser=argparse.ArgumentParser(description=__doc__)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--proof',type=Path)
    source.add_argument('--ghidra',type=Path)
    parser.add_argument('--assembly',type=Path,required=True)
    parser.add_argument('--elf',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--output',type=Path)
    parser.add_argument('--source-revision',help='Read historical producer identities without resetting the checkout')
    args=parser.parse_args()
    if args.proof:result=replay(args.proof,args.assembly,args.elf,args.root,args.source_revision)
    else:
        ghidra=json.loads(args.ghidra.read_text());text=args.assembly.read_text();elf=args.elf.read_bytes()
        selected={r['address'] for r in json.loads((args.root/'Small_TV/src/symbol-map.json').read_text())['functions']}
        result=dict(passed=True,baseline=audit(ghidra,text,elf,selected),
            rejected_controls=check_controls(ghidra,text,elf,selected))
    if args.output:
        assert not args.output.exists();args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='baseline'}))


if __name__=='__main__':main()
