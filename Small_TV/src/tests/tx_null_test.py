"""Compare full null-completion effects and real quick-wake/state helpers."""
import argparse
from dataclasses import asdict
import hashlib
from importlib.metadata import version
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import Image,sha
from reverse.rv32_link_match import size_at,model,match
from reverse.timer_event11_match import objects
from reverse.tx_null import qualify
from timer_event11_semantics import reader
from tx_null_instructions import NullProbe
from tx_null_model import NullState,MASK32,MASK64,expected

PARENT='pm_tx_null_data_done_process'
QUICK='pm_tx_null_data_done_quick_wake_process'
SETTER='pm_set_state'


def cases():
    """Cover parent decision combinations, helper states and arithmetic separately."""
    for a,b,b15,b16,retry,pending,b21,b22,check,b14 in product(
            (0,1,2),(0,1,2),(0,1),(0,1),(0,15,16,255),(0,1),(0,1),(0,1),(0,1),(0,1)):
        yield 'parent-decisions',NullState(byte15=b15,byte16=b16,byte9=retry,byte488=pending,
            byte21=b21,byte22=b22,byte14=b14,byte26=1,byte20=1),dict(argument0=a,argument1=b,check=check)
    for active,flag19,flag20,b22,idle,b,b1,b456,b26 in product(
            (0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1,2,255),(0,1),(0,1)):
        yield 'parent-quick-wake',NullState(byte15=0,byte21=1,byte22=b22,byte468=active,
            byte19=flag19,byte20=flag20,byte456=b456,byte26=b26,byte1=b1,counter32=MASK32),dict(argument1=b,idle=idle)
    for b1,active,flag27,coex,flag543,now,deadline in product(
            (0,1,2),(0,1),(0,1),(0,1),(0,1),(0xfffffff0,0x100000010,MASK64-16),
            (0,1,0xfffffff0,0x100000010,0x100000011,MASK64)):
        yield 'sleep-deadline',NullState(byte15=0,byte22=1,byte1=b1,byte468=active,
            byte27=flag27,byte543=flag543,deadline568=deadline,counter28=MASK32),dict(argument0=1,argument1=1,coex=coex,now=now)
    for station,peerflag,c,a,b,enabled,context,pending in product(
            (0,1,2),(0,1,255),(0,1,255),(0,1),(0,1),(0,1),(0,1),(0,1)):
        yield 'pending-station-gates',NullState(byte15=0,byte21=1,byte22=1,byte488=pending,
            enabled52=enabled,word36=context,period72=10,fallback28=60000000,byte26=0),dict(
                argument0=a,argument1=b,argument2=c,station=station,peerflag=peerflag)
    for a,b,retry9,retry10,b26,slice_allowed in product(
            (0,1,2,255),(0,2,255),(0,14,15,16,255),(0,254,255),(0,1),(0,1)):
        yield 'retry-boundaries',NullState(byte15=1,byte16=0,byte21=1,byte22=1,
            byte9=retry9,byte10=retry10,byte26=b26),dict(argument0=a,argument1=b,slice_allowed=slice_allowed)
    for active,b19,b20,b22,idle,completed in product((0,1),(0,1,255),(0,1,255),(0,1),(0,1),(0,1,255)):
        yield 'direct-quick',NullState(byte468=active,byte19=b19,byte20=b20,byte22=b22),dict(
            argument0=completed,idle=idle,function=QUICK)
    for initial,wanted in product((0,1,2,5,255),(0,1,2,5,255,256,MASK32)):
        yield 'direct-setter',NullState(byte1=initial),dict(argument0=wanted,function=SETTER)


def instructions(qualification,factory,native):
    """Compare complete effects and require every selected instruction start."""
    reads={'factory':reader(factory),'native':reader(native)}
    probes={v:NullProbe(qualification['layouts'][v],read) for v,read in reads.items()}
    digest,counts,samples=hashlib.sha256(),{},{}
    for category,state,kwargs in cases():
        now=kwargs.get('now',0x100000080);arguments={k:v for k,v in kwargs.items() if k!='now'}
        observed={}
        for variant,probe in probes.items():
            actual=probe.call_null(state,now,**arguments)
            wanted=expected(variant,state,now,**arguments)
            assert actual==wanted,(variant,category,asdict(state),now,arguments,actual,wanted)
            observed[variant]=actual
        record=dict(category=category,state=asdict(state),now=now,arguments=arguments,observed=observed)
        digest.update((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
        counts[category]=counts.get(category,0)+1
        for name,condition in {
            'pending-changes-ready': state.byte488 and state.byte15==0 and arguments.get('argument1',0)!=1
                and observed['factory']['writes']!=observed['native']['writes'],
            'missing-station-return':observed['native']['station_reads']==['station-pointer'],
            'missing-peer-skips':observed['native']['station_reads']==['station-pointer','peer-pointer'],
            'peer-byte820-read': 'peer-byte820' in observed['native']['station_reads'],
            'counter32-wrap':[32,4,0] in observed['native']['counter_writes'],
            'counter28-wrap':[28,4,0] in observed['native']['counter_writes'],
            'retry10-wrap':[10,1,0] in observed['native']['writes'] and state.byte10==255
                and ['null',1] in observed['native']['calls'],
            'sleep-deadline-difference': category=='sleep-deadline' and ['sleep'] in observed['native']['calls']
                and ['sleep-delay'] in observed['factory']['calls'],
            'quick-returns-original-byte': category=='direct-quick' and observed['native']['return_value']==255,
        }.items():
            if condition:samples.setdefault(name,record)
    coverage={}
    for variant,probe in probes.items():
        coverage[variant]=[]
        for name in (PARENT,QUICK,SETTER):
            row=next(r for r in qualification['layouts'][variant]['functions'] if r['name']==name)
            start=int(row['start'],0);code=reads[variant](start,row['linked_bytes'])
            addresses,offset=set(),0
            while offset<len(code):addresses.add(start+offset);offset+=size_at(code,offset)
            missing=addresses-probe.visited
            assert not missing,(variant,name,sorted(map(hex,missing)))
            coverage[variant].append(dict(name=name,bytes=len(code),instruction_starts=len(addresses),
                visited=len(addresses&probe.visited),complete_body_instruction_coverage=True))
    assert len(samples)==9,sorted(samples)
    return dict(passed=True,cases_per_image=sum(counts.values()),executions=2*sum(counts.values()),counts=counts,
        trace_sha256=digest.hexdigest(),coverage=coverage,samples=samples,external_helpers_stubbed=True,
        station_pointer_lifetime_proved=False,transitive_rf_scheduler_semantics_proved=False,
        full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,physical_hardware_tested=False)


def run(factory,reference,native,app,old_pp,new_pp):
    """Requalify strict identities and reject concrete helper/body corruptions."""
    qualified=qualify(factory,reference,native,app,old_pp,new_pp)
    result=instructions(qualified,factory,native)
    rejected=[];image=Image(factory)
    old=next(r for r in qualified['layouts']['factory']['extra_helpers'] if r['name']==QUICK)
    raw=image.read(int(old['start'],0),old['linked_bytes'],True)
    changed=raw.replace(bytes.fromhex('83c7471d'),bytes.fromhex('83c7571d'),1)
    assert changed!=raw
    actions={
        'wrong-sdk':lambda:qualify(factory,reference,native,app,new_pp,old_pp),
        'historical-as-current':lambda:qualify(factory,reference,reference,app,old_pp,new_pp),
        'truncated-quick':lambda:qualify(factory,reference,native,app,old_pp,new_pp,{('factory',QUICK):raw[:-2]}),
        'neighboring-quick':lambda:qualify(factory,reference,native,app,old_pp,new_pp,
            {('factory',QUICK):image.read(int(old['end'],0),len(raw),True)}),
        'changed-active-flag':lambda:qualify(factory,reference,native,app,old_pp,new_pp,{('factory',QUICK):changed}),
    }
    for name,action in actions.items():
        try:action()
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Invalid null completion helper accepted: '+name)
    layout=qualified['layouts']['native']
    parent=next(row for row in layout['functions'] if row['name']==PARENT)
    start=int(parent['start'],0);body=reader(native)(start,parent['linked_bytes'])
    source=objects(new_pp,'native')['pm.o']
    # Exercise actual instruction/field changes below the full-image hash guard.
    for name,before,after in (
            ('wrong-pending-byte','03c7871e','03c7971e'),
            ('wrong-deadline-high-word','8327c423','8327c422'),
            ('wrong-deadline-flag','8347f421','8347e421'),
            ('changed-retry-threshold','bd47','b947')):
        old,new=bytes.fromhex(before),bytes.fromhex(after)
        assert old in body
        changed=body.replace(old,new,1)
        try:match(model(source,PARENT),changed,start,layout['prior']['gp'])
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Invalid null completion body accepted: '+name)
    return dict(passed=True,qualification=qualified,instructions=result,rejected_controls=rejected,
        engines={'unicorn':version('unicorn'),'pyelftools':version('pyelftools')},
        full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Save a fresh report while preserving all code/library/firmware inputs."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','reference','native','app','old-pp','new-pp','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing null-completion report')
    root=Path(__file__).resolve().parents[1]
    sources=('tests/tx_null_test.py','tests/tx_null_model.py','tests/tx_null_instructions.py','tools/reverse/tx_null.py',
        'tests/keep_alive_instructions.py','tests/keep_alive_model.py','tests/timer_event11_instructions.py',
        'tests/timer_event11_model.py','tests/timer_event11_semantics.py','tools/reverse/timer_tim.py',
        'tools/reverse/timer_keep_alive.py','tools/reverse/timer_event11_match.py','tools/reverse/rv32_link_match.py',
        'tools/reverse/elf_archive.py','tools/reverse/nothrow_linkage.py','tools/audit_factory_xrefs.py')
    files=[args.factory,args.reference,args.native,args.app,args.old_pp,args.new_pp,*[root/name for name in sources]]
    pins={str(path.resolve()):sha(path.read_bytes()) for path in files}
    if args.output.resolve() in [path.resolve() for path in files]:raise ValueError('Null-completion output aliases an input')
    result=run(args.factory.read_bytes(),args.reference.read_bytes(),args.native.read_bytes(),args.app.read_bytes(),args.old_pp,args.new_pp)
    assert all(sha(Path(path).read_bytes())==digest for path,digest in pins.items())
    result.update(inputs_sha256=pins,inputs_unchanged=True)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,executions=result['instructions']['executions'],
        counts=result['instructions']['counts'],coverage=result['instructions']['coverage'],controls=result['rejected_controls'])))


if __name__=='__main__':main()
