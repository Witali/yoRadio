"""Rebuild scoped factory-runtime gap evidence from pinned objects and unchanged images."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.runtime_call_gaps import OBJECTS, qualify
from runtime_call_controls import controls
from runtime_call_instructions import execute
from verify_rv32_disassembly_evidence import payload


def same(recorded, measured):
    """Require every target, body, event count and limitation to survive independent replay."""
    if recorded != measured:
        raise ValueError('Runtime call evidence differs from recomputation')


def verify(proof_path, root, factory, native):
    """Use no compiler runtime installation, VM, network, board or mutable analysis project."""
    proof=json.loads(proof_path.read_bytes())
    assert proof['schema']=='runtime-call-gap-evidence-v1' and proof['passed']
    for name,digest in proof['source_pins'].items():
        path=(root/name).resolve();assert path.is_relative_to(root.resolve()) and sha(path.read_bytes())==digest
    files={name:payload(proof_path.parent,reference) for name,reference in proof['files'].items()}
    parts={name:files['object:'+name] for name in OBJECTS}
    original=factory.read_bytes();current=native.read_bytes()
    measured=qualify(original,current,parts)
    recorded=json.loads(files['qualification']);assert recorded.pop('inputs_unchanged') is True
    same(recorded,measured)
    run=execute(original,current,measured);same(json.loads(files['instructions']),run)
    mutations=controls(original,current,parts,measured)
    same(json.loads(files['controls']),mutations)
    rejected=[]
    for fault in ('call-identity','missing-gap','native-counterpart','natural-landing-pad','compiler-version','physical-pass'):
        changed=deepcopy(measured)
        if fault=='call-identity':changed['gaps'][2]['callee']='wrong_callback'
        elif fault=='missing-gap':changed['gaps'].pop()
        elif fault=='native-counterpart':changed['variants']['native']['absent_linked_symbols']=[]
        elif fault=='natural-landing-pad':changed['natural_exception_reachability_proved']=True
        elif fault=='compiler-version':changed['factory_compiler_version_identified']=True
        else:changed['physical_hardware_tested']=True
        try:same(changed,measured)
        except ValueError:rejected.append(fault)
        else:raise AssertionError('Forged runtime claim accepted')
    changed=deepcopy(run);changed['desired_nothrow_oom_contract_passed']=True
    try:same(changed,run)
    except ValueError:rejected.append('desired-oom-contract-forgery')
    else:raise AssertionError('Forged nothrow correction accepted')
    assert factory.read_bytes()==original and native.read_bytes()==current
    return dict(passed=True,functions={k:len(v['functions']) for k,v in measured['variants'].items()},
                identified_gaps=len(measured['gaps']),literal_cases=run['cases'],
                desired_nothrow_oom_contract_passed=False,
                altered_inputs_rejected=len(mutations['rejected']),altered_reports_rejected=rejected,
                whole_image_completeness_proved=False,natural_exception_reachability_proved=False,
                physical_hardware_tested=False)


def main():
    """Replay archived objects against the explicit original factory/native ELF paths."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    for name in ('proof','factory','native'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();print(json.dumps(verify(args.proof,args.root,args.factory,args.native)))


if __name__=='__main__':main()
