"""Test keep-alive time boundaries and old/new TX-completion algorithms."""
import argparse
from dataclasses import asdict
import hashlib
from importlib.metadata import version
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import Image, sha
from reverse.timer_keep_alive import qualify
from reverse.rv32_link_match import size_at
from timer_event11_semantics import reader
from keep_alive_instructions import KeepProbe
from keep_alive_model import KeepState, MASK64, expected


def instructions(layouts, factory, native):
    """Execute arithmetic boundaries and the full TX branch Cartesian product."""
    reads = {'factory':reader(factory),'native':reader(native)}
    probes = {variant:KeepProbe(layouts[variant],read) for variant,read in reads.items()}
    digest,counts,samples = hashlib.sha256(),{'predicate':0,'reset':0,'tx-per-image':0,'null-per-image':0},{}
    def verify(variant,name,state,now,**kwargs):
        """Compare actual instruction effects with the independent version-specific model."""
        observed = probes[variant].call(name,state,now,**kwargs)
        model = expected(variant,name,state,now,**kwargs)
        assert observed == model,(variant,name,asdict(state),now,kwargs,observed,model)
        record = dict(variant=variant,function=name,state=asdict(state),now=now,arguments=kwargs,result=observed)
        digest.update((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
        return record
    for enabled,context,period,fallback,origin in product((0,1,255),(0,1),
            (0,1,10,4194,4195,65535),(0,1,10000000,0xffffffff),(0,0xfffffff0,0xfffffffffffffff0)):
        threshold = ((period<<9)*1000)&0xffffffff if enabled else fallback
        for delta in sorted({0,1,max(0,threshold-1),threshold,threshold+1,1<<32,MASK64}):
            now=(origin+delta)&MASK64
            state=KeepState(enabled52=enabled,word36=context,period72=period,fallback28=fallback,
                            last88=origin,last480=origin)
            verify('factory','pm_keep_alive',state,now);counts['predicate']+=1
    for byte14,context,coex,now in product((0,1,255),(0,1),(0,1),(0,0xffffffff,0xfffffffffffffff0)):
        verify('factory','pm_reset_keep_alive',KeepState(byte14=byte14,word36=context),now,coex=coex)
        counts['reset']+=1
    for success,argument2,byte14,byte1,context,enabled,idle,check,byte26,delta in product(
            (0,1),(0,1),(0,1),(0,1,2),(0,1),(0,1),(0,1),(0,1),(0,1),
            (0,99999,100000,100001,1<<32,MASK64)):
        now=0x100000080
        state=KeepState(byte14=byte14,byte1=byte1,word36=context,enabled52=enabled,period72=10,
                        fallback28=10000000,byte26=byte26,last88=0xfffffff0,last480=(now-delta)&MASK64)
        for variant in probes:
            record=verify(variant,'pm_tx_data_done_process',state,now,success=success,argument2=argument2,
                          idle=idle,check=check,coex=0)
            if success and argument2 and byte14 and byte1==1 and context==1 and not enabled and idle and not check and byte26:
                samples.setdefault(str(delta),{})[variant]=record
        counts['tx-per-image']+=1
    pending_samples=[]
    for pending,enabled,context,argument2,station,peerflag in product((0,1),(0,1),(0,1),(0,1),(0,1,2),(0,1)):
        state=KeepState(byte488=pending,enabled52=enabled,word36=context,byte22=1,
                        period72=10,fallback28=10000000,last88=10,last480=20)
        observed={variant:verify(variant,'pm_tx_null_data_done_process',state,0x100000080,
                                 argument1=1,argument2=argument2,check=1,station=station,peerflag=peerflag)
                  for variant in probes}
        if pending and not enabled and context==1 and argument2==1:
            pending_samples.append(observed)
        counts['null-per-image']+=1
    coverage={}
    executed={'factory':('pm_keep_alive','pm_reset_keep_alive','pm_tx_data_done_process'),
              'native':('pm_tx_data_done_process',)}
    for variant,probe in probes.items():
        coverage[variant]=[]
        for row in layouts[variant]['functions']:
            start=int(row['start'],0); raw=reads[variant](start,row['linked_bytes'])
            addresses,offset=set(),0
            while offset<len(raw):addresses.add(start+offset);offset+=size_at(raw,offset)
            missing=addresses-probe.visited
            if row['name'] in executed[variant]:assert not missing,(variant,row['name'],sorted(map(hex,missing)))
            coverage[variant].append(dict(name=row['name'],instruction_starts=len(addresses),
                                         visited=len(addresses&probe.visited),dynamically_covered=not missing))
    return dict(passed=True,counts=counts,executions=counts['predicate']+counts['reset']+2*(counts['tx-per-image']+counts['null-per-image']),
                trace_sha256=digest.hexdigest(),threshold_samples=samples,coverage=coverage,
                pending_samples=pending_samples,complete_null_completion_coverage=False,
                external_helpers_stubbed=True,full_runtime_lifecycle_proved=False,
                whole_image_completeness_proved=False,physical_hardware_tested=False)


def run(factory,native,old_pp,new_pp):
    """Requalify code before every instruction comparison and reject corruptions."""
    qualified=qualify(factory,native,old_pp,new_pp)
    result=instructions(qualified['layouts'],factory,native)
    image=Image(factory)
    row=next(f for f in qualified['layouts']['factory']['functions'] if f['name']=='pm_keep_alive')
    raw=image.read(int(row['start'],0),row['linked_bytes'],True)
    wrong_state=bytearray(raw); assert wrong_state[4:8]==bytes.fromhex('3734cc3f')
    wrong_state[4:8]=bytes.fromhex('3744cc3f')
    wrong_config=bytearray(raw);assert wrong_config[34:38]==bytes.fromhex('9387c114')
    wrong_config[34:38]=bytes.fromhex('93870115')
    tx=next(f for f in qualified['layouts']['native']['functions'] if f['name']=='pm_tx_data_done_process')
    txraw=reader(native)(int(tx['start'],0),tx['linked_bytes'])
    assert txraw.count(bytes.fromhex('9387076a'))==1
    wrong_threshold=txraw.replace(bytes.fromhex('9387076a'),bytes.fromhex('9387f769'))
    faults={'wrong-sdk':lambda:qualify(factory,native,new_pp,old_pp),
            'truncated-predicate':lambda:qualify(factory,native,old_pp,new_pp,
                                                {('factory','pm_keep_alive'):raw[:-2]}),
            'neighboring-predicate':lambda:qualify(factory,native,old_pp,new_pp,
                    {('factory','pm_keep_alive'):image.read(int(row['end'],0),len(raw),True)}),
            'wrong-pm-anchor':lambda:qualify(factory,native,old_pp,new_pp,
                                            {('factory','pm_keep_alive'):bytes(wrong_state)}),
            'wrong-config-anchor':lambda:qualify(factory,native,old_pp,new_pp,
                                            {('factory','pm_keep_alive'):bytes(wrong_config)}),
            'changed-100ms-threshold':lambda:qualify(factory,native,old_pp,new_pp,
                                            {('native','pm_tx_data_done_process'):wrong_threshold})}
    rejected=[]
    for name,action in faults.items():
        try:action()
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Invalid keep-alive body accepted: '+name)
    return dict(passed=True,qualification=qualified,instructions=result,rejected_controls=rejected,
                engines={'unicorn':version('unicorn'),'pyelftools':version('pyelftools')},
                full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,
                physical_hardware_tested=False)


def main():
    """Write a fresh result from unchanged original images and private CPU fixtures."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','native','old-pp','new-pp','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing keep-alive evidence')
    root=Path(__file__).resolve().parents[1]
    files=[args.factory,args.native,args.old_pp,args.new_pp]+[root/name for name in (
        'tests/keep_alive_test.py','tests/keep_alive_instructions.py','tests/keep_alive_model.py',
        'tools/reverse/timer_keep_alive.py','tools/reverse/timer_event11_match.py',
        'tools/reverse/rv32_link_match.py','tools/reverse/elf_archive.py','tools/audit_factory_xrefs.py',
        'tests/timer_event11_instructions.py','tests/timer_event11_model.py','tests/timer_event11_semantics.py')]
    pins={str(path.resolve()):sha(path.read_bytes()) for path in files}
    result=run(args.factory.read_bytes(),args.native.read_bytes(),args.old_pp,args.new_pp)
    assert all(sha(Path(path).read_bytes())==digest for path,digest in pins.items())
    result.update(inputs_sha256=pins,inputs_unchanged=True)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,counts=result['instructions']['counts'],executions=result['instructions']['executions'],
                          controls=result['rejected_controls'],coverage=result['instructions']['coverage'])))


if __name__=='__main__':main()
