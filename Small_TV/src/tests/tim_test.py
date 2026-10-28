"""Compare complete factory/current TIM instruction effects and arithmetic edges."""
import argparse
from dataclasses import asdict
import hashlib
from importlib.metadata import version
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import sha
from reverse.rv32_link_match import size_at
from reverse.rv32_link_match import match, model
from reverse.timer_event11_match import objects
from reverse.timer_tim import qualify
from timer_event11_semantics import reader
from tim_instructions import TimProbe
from tim_model import TimState, MASK32, MASK64, expected


def cases():
    """Exercise branch flags separately from time/width boundaries to limit runtime."""
    for byte1,a,b,allowed,b21,b22,b468,context,enabled in product(
            (0,1,2), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1)):
        yield TimState(byte1=byte1,byte21=b21,byte22=b22,byte468=b468,word36=context,
                       enabled52=enabled,period72=1,fallback28=60000000,byte20=255,
                       byte27=255,byte488=255,deadline112=0x100000204), 0x100000010, a,b,allowed
    for now,delta,window,a in product((0,0xfffffff0,0x100000010,MASK64-16),
            (-1,0,1,999,1000,1001,MASK32,1<<32,(1<<32)+1,MASK64), (0,1,1000,MASK32), (0,1)):
        yield TimState(byte1=1,word36=0,deadline112=(now+delta)&MASK64,window60=window,
                       counter8=MASK32,counter12=MASK32), now,a,1-a,1
    # Predicate equality, sign-extension and wrapped-clock cases in real TIM callers.
    for enabled,period,origin,a,b in product((0,1,255),(0,1,4194,4195,65535),
            (0,0xfffffff0,MASK64-16),(0,1),(0,1)):
        threshold=(((period<<9)*1000)&MASK32) if enabled else 10000000
        for delta in sorted({0,1,max(0,threshold-1),threshold,threshold+1,1<<32,MASK64}):
            yield TimState(byte1=1,word36=1,enabled52=enabled,period72=period,fallback28=10000000,
                           last88=origin,last480=origin,deadline112=0,byte488=255), (origin+delta)&MASK64,a,b,1
    # Noncanonical truthy flags must follow the compiled byte/argument comparisons.
    for byte1,a,b,b21,b22,b468 in product((0,1,2,255),(0,255),(0,255),(0,255),(0,255),(0,255)):
        yield TimState(byte1=byte1,byte21=b21,byte22=b22,byte468=b468,word36=1,
                       enabled52=255,period72=0), 12345,a,b,255


def instructions(qualification, factory, native):
    """Compare every write/call and require all TIM instruction starts in both images."""
    reads={'factory':reader(factory),'native':reader(native)}
    probes={v:TimProbe(qualification['layouts'][v],read) for v,read in reads.items()}
    digest, count, samples = hashlib.sha256(), 0, {}
    for state,now,a,b,allowed in cases():
        observed={}
        for variant,probe in probes.items():
            actual=probe.call_tim(state,now,a,b,allowed)
            wanted=expected(variant,state,now,a,b,allowed)
            assert actual==wanted,(variant,asdict(state),now,a,b,allowed,actual,wanted)
            observed[variant]=actual
        record=dict(state=asdict(state),now=now,argument0=a,argument1=b,slice_allowed=allowed,observed=observed)
        digest.update((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
        for category,condition in {
                'factory-null-native-sleep': ['null',1] in observed['factory']['calls'] and ['sleep'] in observed['native']['calls'],
                'factory-null-native-no-request': ['null',0] in observed['factory']['calls'],
                'counter-wrap': [8,4,0] in observed['native']['counter_writes'],
                'coex-full-width-cap': ['coex408',2,0,state.window60] in observed['native']['calls'] and state.deadline112>now+(1<<32),
                'slice-deferred': not allowed and a and state.byte1==1,
                'high-clock-word': now>MASK32 and any(c[0]=='coex408' for c in observed['native']['calls']),
                }.items():
            if condition: samples.setdefault(category,record)
        count+=1
    coverage={}
    for variant,probe in probes.items():
        row=next(r for r in qualification['layouts'][variant]['functions'] if r['name']=='pm_process_tim')
        start=int(row['start'],0); code=reads[variant](start,row['linked_bytes'])
        addresses,offset=set(),0
        while offset<len(code):addresses.add(start+offset);offset+=size_at(code,offset)
        missing=addresses-probe.visited
        assert not missing,(variant,'unvisited TIM instructions',sorted(map(hex,missing)))
        coverage[variant]=dict(name=row['name'],bytes=len(code),instruction_starts=len(addresses),
                               visited=len(addresses&probe.visited),complete_body_instruction_coverage=True)
    assert len(samples)==6
    return dict(passed=True,cases_per_image=count,executions=2*count,trace_sha256=digest.hexdigest(),
                coverage=coverage,samples=samples,external_helpers_stubbed=True,
                transitive_slice_rf_sleep_semantics_proved=False,
                full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,physical_hardware_tested=False)


def run(factory,reference,native,app,old_pp,new_pp):
    """Requalify both production/reference pairs before executing untouched code."""
    qualification=qualify(factory,reference,native,app,old_pp,new_pp)
    result=instructions(qualification,factory,native)
    rejected=[]
    faults={
        'old-native-as-current':lambda:qualify(factory,reference,reference,app,old_pp,new_pp),
        'changed-native-elf':lambda:qualify(factory,reference,native[:-1]+bytes([native[-1]^1]),app,old_pp,new_pp),
        'changed-app':lambda:qualify(factory,reference,native,app[:-1]+bytes([app[-1]^1]),old_pp,new_pp),
        'wrong-sdk':lambda:qualify(factory,reference,native,app,new_pp,old_pp),
        'truncated-reference':lambda:qualify(factory,reference[:-4],native,app,old_pp,new_pp),
    }
    for name,action in faults.items():
        try:action()
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Invalid TIM input accepted: '+name)
    # These checks exercise the full object matcher below the image-hash guard.
    # Mutations are private byte strings; no ELF, library or live VM is written.
    layout=qualification['layouts']['native']
    row=next(r for r in layout['functions'] if r['name']=='pm_process_tim')
    start=int(row['start'],0); raw=reader(native)(start,row['linked_bytes'])
    source=objects(new_pp,'native')['pm.o']
    for name,old,new in (
            ('changed-pm20-store','238a2401','238b2401'),
            ('changed-slice-5000','13068638','13069638'),
            ('wrong-osi-408-slot','83a78719','83a70719'),
            ('lost-counter-increment','0507','0107')):
        before,after=bytes.fromhex(old),bytes.fromhex(new)
        assert before in raw
        changed=raw.replace(before,after,1)
        try:match(model(source,'pm_process_tim'),changed,start,layout['prior']['gp'])
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Invalid TIM body accepted: '+name)
    return dict(passed=True,qualification=qualification,instructions=result,rejected_controls=rejected,
                engines={'unicorn':version('unicorn'),'pyelftools':version('pyelftools')},
                full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Save a new local report without overwriting input artifacts or earlier evidence."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','reference','native','app','old-pp','new-pp','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing TIM evidence')
    root=Path(__file__).resolve().parents[1]
    files=[args.factory,args.reference,args.native,args.app,args.old_pp,args.new_pp]
    source_names=('tests/tim_test.py','tests/tim_model.py','tests/tim_instructions.py','tools/reverse/timer_tim.py',
        'tests/keep_alive_instructions.py','tests/keep_alive_model.py','tests/timer_event11_instructions.py',
        'tests/timer_event11_model.py','tests/timer_event11_semantics.py','tools/reverse/timer_keep_alive.py',
        'tools/reverse/timer_event11_match.py','tools/reverse/rv32_link_match.py',
        'tools/reverse/elf_archive.py','tools/reverse/nothrow_linkage.py','tools/audit_factory_xrefs.py')
    files.extend(root/name for name in source_names)
    pins={str(path.resolve()):sha(path.read_bytes()) for path in files}
    if args.output.resolve() in [path.resolve() for path in files]:raise ValueError('TIM output aliases an input')
    result=run(args.factory.read_bytes(),args.reference.read_bytes(),args.native.read_bytes(),args.app.read_bytes(),args.old_pp,args.new_pp)
    assert all(sha(Path(path).read_bytes())==digest for path,digest in pins.items())
    result.update(inputs_sha256=pins,inputs_unchanged=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,executions=result['instructions']['executions'],
                         coverage=result['instructions']['coverage'],controls=result['rejected_controls'])))


if __name__=='__main__':main()
