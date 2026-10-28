"""Exercise every negotiated BSS period through the corrected real timer backends."""
import argparse
import hashlib
from importlib.metadata import version
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.rv32_link_match import size_at
from reverse.nothrow_linkage import LinkedRuntime
from verify_wifi_keep_alive import verify
from keep_alive_range_instructions import RangeProbe

MASK32=(1<<32)-1


def expected(enabled=1,period=1,adjustment=500000,fallback=60000000,cancel=False,
             switch_adapter=False,mutate_config=False,initialized=True,start_result=0,
             stop_result=0,backend=None,backend_delay=0,repeat=False):
    """Specify full-width timeout, unit choice and cancellation independently of C code."""
    effects=[];reads=[];alarm=RangeProbe.NOW+17;stopped=None
    if backend:
        delay=backend_delay*(1000 if backend=='ms' else 1);unit=backend
    elif enabled:
        value=period*1024000-adjustment
        delay=value if value>=0 else value&MASK32
        unit='us' if delay<=MASK32 else 'ms'
        if unit=='ms':delay=((delay+999)//1000)*1000
    else:delay=fallback;unit='us'
    active=backend is not None or bool(enabled or fallback)
    switched=False
    if active:
        if not backend:
            reads.append([228,'A'])
            if initialized:effects.append(['stop']);alarm=0;switched=True
            reads.append([224 if unit=='ms' else 240,'B' if switch_adapter and switched else 'A'])
        if not initialized:effects.append(['assert']);stopped='uninitialized'
        else:
            effects.append(['stop']);alarm=0;switched=True
            effects.append(['periodic' if backend and repeat else 'once',delay])
            if start_result:effects.append(['error-check']);stopped='backend-error'
            else:alarm=RangeProbe.NOW+delay
    if cancel and stopped is None:
        reads.append([228,'B' if switch_adapter and switched else 'A'])
        if initialized:effects.append(['stop']);alarm=0;switched=True
    return dict(effects=effects,adapter_reads=reads,alarm=alarm,stopped=stopped,
                config_changed_by_platform=mutate_config and switched)


def instructions(elf,app,qualified):
    """Compare every real backend timeout, input byte, adapter read and preserved register."""
    probe=RangeProbe(elf,app,qualified)
    digest,counts,samples=hashlib.sha256(),{},{}
    def check(family,arguments):
        """Run one bounded private CPU call and retain a deterministic trace digest."""
        actual=probe.call(**arguments);wanted=expected(**arguments)
        assert actual==wanted,(family,arguments,actual,wanted)
        row=dict(family=family,arguments=arguments,result=actual)
        digest.update((json.dumps(row,sort_keys=True,separators=(',',':'))+'\n').encode())
        counts[family]=counts.get(family,0)+1
        return row
    for period in range(1,65536):
        row=check('all-negotiated-periods',dict(period=period,adjustment=500000 if period<=3 else 2000000))
        if period in (1,3,4,4196,4197,32772,65535):samples['period-'+str(period)]=row
        if period%16384==0:print(json.dumps(dict(periods_executed=period)),flush=True)
    for enabled,fallback,cancel in product((0,),(0,1,999,1000,60000000,0x80000000,MASK32),(False,True)):
        check('fallback-and-disabled',dict(enabled=enabled,fallback=fallback,cancel=cancel))
    for period,adjustment,cancel,switch,mutate in product(
            (0,1,4196,4197,65535),(0,1,999,1000,2000001,MASK32),(False,True),(False,True),(False,True)):
        row=check('rounding-snapshot-cancel',dict(enabled=255,period=period,adjustment=adjustment,
                  cancel=cancel,switch_adapter=switch,mutate_config=mutate))
        if period==65535 and adjustment==2000001 and cancel and switch and mutate:samples['rounded-snapshot-cancel']=row
    for backend,delay,repeat,error in product(('ms','us'),(0,1,4295728,67105840,MASK32),(False,True),(0,0x103)):
        check('real-backend-abi',dict(backend=backend,backend_delay=delay,repeat=repeat,start_result=error))
    for period,initialized,error in ((4197,False,0),(1,False,0),(4197,True,0x103),(1,True,0x103)):
        check('nonreturning-backend-checks',dict(period=period,adjustment=2000000 if period>3 else 500000,
                                               initialized=initialized,start_result=error))
    for backend in ('ms','us'):
        check('uninitialized-direct-backend',dict(backend=backend,backend_delay=1,initialized=False))
    check('ignored-stop-status',dict(period=4197,adjustment=2000000,stop_result=0x103,cancel=True))
    linked=LinkedRuntime(elf,app);coverage=[]
    for name,row in probe.rows.items():
        start=int(row['start'],0);code=linked.read(start,row['linked_bytes'],True)
        addresses=set();offset=0
        while offset<len(code):addresses.add(start+offset);offset+=size_at(code,offset)
        missing=addresses-probe.visited
        assert not missing,(name,'unvisited',sorted(map(hex,missing)))
        coverage.append(dict(name=name,bytes=len(code),instruction_starts=len(addresses),visited=len(addresses)))
    return dict(passed=True,counts=counts,executions=sum(counts.values()),trace_sha256=digest.hexdigest(),
        coverage=coverage,samples=samples,all_65535_negotiated_periods_executed=True,
        public_esp_timer_operations_stubbed=True,full_runtime_lifecycle_proved=False,
        whole_image_completeness_proved=False,physical_hardware_tested=False)


def descriptor_pair(elf,app):
    """Create only a private descriptor-consistent mutant for tests below the hash guard."""
    changed=bytearray(app);changed[176:208]=bytes.fromhex(sha(elf));return bytes(changed)


def change_word(elf,pc,word):
    """Patch an exact copied executable word without changing any original artifact."""
    linked=LinkedRuntime(elf,descriptor_pair(elf,b'\xe9'+bytes(207)))
    sections=[s for s in linked.elf.iter_sections() if s['sh_flags']&4 and s['sh_addr']<=pc<pc+4<=s['sh_addr']+s['sh_size']]
    assert len(sections)==1
    s=sections[0];offset=s['sh_offset']+pc-s['sh_addr'];changed=bytearray(elf)
    changed[offset:offset+4]=word.to_bytes(4,'little');return bytes(changed)


def controls(elf,app,libraries,own,timer,source,before_elf,before_app,qualified):
    """Reject bad source/object identities and concrete linked-unit/caller mutations."""
    linked=LinkedRuntime(elf,app)
    row=qualified['functions'][0];start=int(row['start'],0);code=linked.read(start,row['linked_bytes'],True)
    offset=0;wrong_unit=None
    while offset<len(code):
        size=size_at(code,offset);word=int.from_bytes(code[offset:offset+size],'little')
        if size==4 and word&127==3 and (word>>12)&7==2 and word>>20==224:
            wrong_unit=change_word(elf,start+offset,(word&0x000fffff)|(240<<20));break
        offset+=size
    assert wrong_unit is not None
    caller=qualified['callers'][0]
    # All four calls to the relocated app function use a standard JAL here.
    from reverse.rv32_link_match import model
    from reverse.elf_archive import members
    src=next(raw for name,raw in members((libraries/'libnet80211.a').read_bytes()) if name=='wl_cnx.o')
    spec=model(src,caller['name'])
    relative=next(offset for offset,entries in spec['relocs'].items() if any(r['name']=='pm_enable_keep_alive_timer' for r in entries))
    event=next(r for r in caller['transformations'] if r['object_offset']==relative)
    pc=int(event['pc'],0);raw=linked.read(pc,4,True);word=int.from_bytes(raw,'little')
    assert word&127==111
    target=int(qualified['disable']['start'],0);delta=target-pc
    assert delta%2==0 and -(1<<20)<=delta<(1<<20)
    immediate=delta&0x1fffff
    jump=(word&0xfff)|((immediate>>20)<<31)|(((immediate>>1)&1023)<<21)|(((immediate>>11)&1)<<20)|(((immediate>>12)&255)<<12)
    bypass=change_word(elf,pc,jump)
    actions={
        'before-has-no-redirect':lambda:verify(before_elf,before_app,libraries,own,timer,source),
        'wrong-app-pair':lambda:verify(elf,before_app,libraries,own,timer,source),
        'wrong-local-object':lambda:verify(elf,app,libraries,timer,timer,source),
        'wrong-timer-object':lambda:verify(elf,app,libraries,own,own,source),
        'changed-backend-source':lambda:verify(elf,app,libraries,own,timer,source+b'\n'),
        'ms-path-changed-to-us':lambda:verify(wrong_unit,descriptor_pair(wrong_unit,app),libraries,own,timer,source),
        'sdk-caller-bypasses-redirect':lambda:verify(bypass,descriptor_pair(bypass,app),libraries,own,timer,source),
    }
    rejected=[]
    for name,action in actions.items():
        try:action()
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Invalid keep-alive fix accepted: '+name)
    return rejected


def run(elf,app,libraries,own,timer,source,before_elf,before_app):
    """Qualify actual production bytes before exhaustive CPU/backend verification."""
    qualified=verify(elf,app,libraries,own,timer,source)
    result=instructions(elf,app,qualified)
    rejected=controls(elf,app,libraries,own,timer,source,before_elf,before_app,qualified)
    return dict(passed=True,qualification=qualified,instructions=result,rejected_controls=rejected,
        engines={'unicorn':version('unicorn'),'pyelftools':version('pyelftools')},
        full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Write a new deterministic report without overwriting a source or earlier result."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('elf','app','sdk-libraries','object','timer-object','timer-source','before-elf','before-app','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing keep-alive range evidence')
    files=[args.elf,args.app,args.object,args.timer_object,args.timer_source,args.before_elf,args.before_app,*sorted(args.sdk_libraries.glob('*.a'))]
    root=Path(__file__).resolve().parents[1]
    files.extend(root/name for name in ('tests/keep_alive_range_test.py','tests/keep_alive_range_instructions.py',
        'tests/runtime_call_instructions.py','tools/verify_wifi_keep_alive.py','tools/reverse/elf_archive.py',
        'tools/reverse/rv32_link_match.py','tools/reverse/nothrow_linkage.py','tools/reverse/timer_event11_match.py',
        'tools/reverse/runtime_call_gaps.py','tools/audit_factory_xrefs.py','app/network/wifi_keep_alive.c'))
    if args.output.resolve() in [p.resolve() for p in files]:raise ValueError('Range report aliases input')
    pins={str(p.resolve()):sha(p.read_bytes()) for p in files}
    result=run(args.elf.read_bytes(),args.app.read_bytes(),args.sdk_libraries,args.object.read_bytes(),
        args.timer_object.read_bytes(),args.timer_source.read_bytes(),args.before_elf.read_bytes(),args.before_app.read_bytes())
    assert all(sha(Path(p).read_bytes())==digest for p,digest in pins.items())
    result.update(inputs_sha256=pins,inputs_unchanged=True)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,executions=result['instructions']['executions'],counts=result['instructions']['counts'],
        coverage=result['instructions']['coverage'],controls=result['rejected_controls'])))


if __name__=='__main__':main()
