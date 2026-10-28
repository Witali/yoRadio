"""Compare full PM start/stop instructions, state writes and repeated transitions."""
import argparse
from itertools import product
import hashlib
from importlib.metadata import version
import io
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.timer_pm_lifecycle import qualify
from reverse.timer_pm_lifecycle import read_allocated
from elftools.elf.elffile import ELFFile
from reverse.rv32_link_match import size_at
from timer_event11_semantics import reader
from pm_lifecycle_instructions import LifecycleProbe
from pm_lifecycle_model import expected, MASK64


def state(probe,fill,active=0,byte1=0,wake=0,connectionless=0,pending_timer=0,filter_=0):
    """Fill untouched state with a canary and set only the named branch inputs."""
    pm=bytearray([fill]*probe.layout['g_pm_bytes']);cfg=bytearray([fill]*probe.layout['g_pm_cfg_bytes'])
    for offset,value in ((14,active),(1,byte1),(16,wake),(289,connectionless)):
        pm[offset]=value
    pm[292:296]=pending_timer.to_bytes(4,'little');cfg[2]=filter_
    pm[144:152]=(0xfffffff0).to_bytes(8,'little')
    pm[152:160]=(0x123456789abcdef0).to_bytes(8,'little')
    return bytes(pm),bytes(cfg)


def run_instructions(layouts,factory,native):
    """Exercise branch products and retain real state through complete call sequences."""
    reads={'factory':reader(factory),'native':reader(native)}
    probes={v:LifecycleProbe(layouts[v],read) for v,read in reads.items()}
    digest=hashlib.sha256();counts={'start':0,'stop':0,'sequence':0};samples={}
    def verify(variant,name,pm,cfg,args,env,label):
        """Compare every direct effect and complete PM/configuration bytes."""
        probe=probes[variant];result=probe.invoke(name,args,env)
        reference=expected(variant,name,pm,cfg,args,env)
        assert result['trace']==reference['trace'],(variant,name,label,result['trace'],reference['trace'])
        assert result['pm']==reference['pm'],(variant,name,label,[(i,a,b) for i,(a,b) in enumerate(zip(result['pm'],reference['pm'])) if a!=b])
        assert result['cfg']==reference['cfg'],(variant,name,label,'configuration differs')
        for offset,value in result['trace']['global_writes']:
            assert probe.word(probe.pm+offset)==value
        record=dict(variant=variant,function=name,label=label,trace=result['trace'],
                    pm_sha256=sha(result['pm']),cfg_sha256=sha(result['cfg']))
        digest.update((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
        return result,record
    ordinal=0
    for active,conn,period,coex,pti,callback,fill in product((0,1),(0,1,2),(0,1,100,65535,0x400000),
            product((0,1),repeat=2),(0,4,255),(False,True),(0,0xa5)):
        env=dict(now=(0,0xfffffff0,MASK64-15)[ordinal%3],coex=coex,pti=pti,
                 beacon48=callback,beacon52=False,beacon_target=LifecycleProbe.CALL48,mac=bytes.fromhex('020000123456'))
        args=[0x10123,0x12345678,LifecycleProbe.MAC,period,0x1234,0x89abcdef,0x01234567]
        label=dict(active=active,connectionless=conn,period=period,coex=coex,pti=pti,callback=callback,fill=fill)
        for variant,probe in probes.items():
            pm,cfg=state(probe,fill,active=active,connectionless=conn);probe.prepare(pm,cfg,env)
            verify(variant,'pm_start',pm,cfg,args,env,label)
        counts['start']+=1;ordinal+=1
    for active,byte1,wake,conn,pending,filter_,coex,callback,fill in product((0,1),(0,1,2),(0,1),(0,1,2),
            (0,1),(0,1),(0,1),(False,True),(0,0xa5)):
        env=dict(now=(0,0x100000080,MASK64-15)[ordinal%3],coex=(coex,coex),pti=4,
                 beacon48=False,beacon52=callback,beacon_target=LifecycleProbe.CALL48,mac=bytes.fromhex('020000123456'))
        label=dict(active=active,byte1=byte1,wake=wake,connectionless=conn,pending=pending,
                   filter=filter_,coex=coex,callback=callback,fill=fill)
        for variant,probe in probes.items():
            pm,cfg=state(probe,fill,active,byte1,wake,conn,pending,filter_);probe.prepare(pm,cfg,env)
            _,record=verify(variant,'pm_stop',pm,cfg,[],env,label)
            if active and byte1==0 and wake==0 and conn==0 and not pending and not filter_ and not coex and not callback and fill==0xa5:
                samples[variant]=record
        counts['stop']+=1;ordinal+=1
    sequences=[]
    for variant,probe in probes.items():
        for fill,coex in product((0,0xa5),(0,1)):
            env=dict(now=0xfffffff0,coex=(coex,coex),pti=4,beacon48=True,beacon52=True,beacon_target=LifecycleProbe.CALL48,
                     mac=bytes.fromhex('020000123456'))
            pm,cfg=state(probe,fill,connectionless=1);probe.prepare(pm,cfg,env)
            args=[1,42,probe.MAC,100,0x1234,0x89abcdef,0x01234567]
            sequence=[]
            for index,name in enumerate(('pm_start','pm_start','pm_stop','pm_stop','pm_start')):
                env=dict(env,now=(0xfffffff0+index*5000000)&MASK64)
                result,record=verify(variant,name,pm,cfg,args if name=='pm_start' else [],env,
                                     dict(sequence=True,fill=fill,coex=coex,index=index))
                if index in (1,3):assert result['trace']==dict(calls=[],writes=[],cfg_writes=[],global_writes=[])
                pm,cfg=result['pm'],result['cfg'];sequence.append(record)
                counts['sequence']+=1
            sequences.append(sequence)
    coverage={}
    for variant,probe in probes.items():
        rows=[f for f in layouts[variant]['prior']['functions'] if f['name'] in ('pm_start','pm_stop')]
        rows += layouts[variant]['helpers']+layouts[variant]['rom']['functions']
        coverage[variant]=[]
        for row in rows:
            start=int(row['start'],0)
            raw=bytes.fromhex(row['bytes_hex']) if 'bytes_hex' in row else reads[variant](start,row['linked_bytes'])
            positions,offset=set(),0
            while offset<len(raw):positions.add(start+offset);offset+=size_at(raw,offset)
            missing=positions-probe.visited;assert not missing,(variant,row['name'],sorted(map(hex,missing)))
            coverage[variant].append(dict(name=row['name'],instruction_starts=len(positions),visited=len(positions)))
    return dict(passed=True,counts=counts,executions=2*(counts['start']+counts['stop'])+counts['sequence'],
                trace_sha256=digest.hexdigest(),coverage=coverage,stop_samples=samples,sequences=sequences,
                platform_effects_stubbed=True,rom_state_binding_synthetic=True,
                full_runtime_lifecycle_proved=False,physical_hardware_tested=False)


def run(factory,native,old_pp,new_pp,rom):
    """Requalify every body before interpreting a complete transition."""
    layout=qualify(factory,native,old_pp,new_pp,rom)
    observed=run_instructions(layout['layouts'],factory,native)
    faults={
        'wrong-rom':lambda:qualify(factory,native,old_pp,new_pp,rom[:-1]),
        'wrong-native':lambda:qualify(factory,native[:-1],old_pp,new_pp,rom),
        'wrong-factory':lambda:qualify(factory[:-1],native,old_pp,new_pp,rom),
        'swapped-sdk':lambda:qualify(factory,native,new_pp,old_pp,rom),
        'data-as-code':lambda:read_allocated(ELFFile(io.BytesIO(native)),
            layout['layouts']['native']['prior']['prior']['osi_table']['address'],4,True)}
    rejected=[]
    for name,action in faults.items():
        try:action()
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Invalid lifecycle qualification accepted: '+name)
    return dict(passed=True,qualification=layout,instructions=observed,rejected_controls=rejected,
                engines={'unicorn':version('unicorn'),'pyelftools':version('pyelftools')},
                full_runtime_lifecycle_proved=False,transitive_platform_effects_proved=False,
                physical_hardware_tested=False,whole_image_completeness_proved=False)


def main():
    """Read immutable images and write a new deterministic host-only checkpoint."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','native','old-pp','new-pp','rom','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve prior lifecycle evidence')
    root=Path(__file__).resolve().parents[1]
    paths=[args.factory,args.native,args.old_pp,args.new_pp,args.rom]+[root/name for name in (
        'tests/pm_lifecycle_test.py','tests/pm_lifecycle_instructions.py','tests/pm_lifecycle_model.py',
        'tools/reverse/timer_pm_lifecycle.py','tests/keep_alive_instructions.py','tests/keep_alive_model.py',
        'tools/reverse/timer_keep_alive.py','tools/reverse/timer_event11_match.py','tools/reverse/rv32_link_match.py',
        'tools/reverse/elf_archive.py','tools/audit_factory_xrefs.py','tests/timer_event11_instructions.py',
        'tests/timer_event11_semantics.py','tests/timer_event11_model.py')]
    pins={str(p.resolve()):sha(p.read_bytes()) for p in paths}
    result=run(args.factory.read_bytes(),args.native.read_bytes(),args.old_pp,args.new_pp,args.rom.read_bytes())
    assert all(sha(Path(p).read_bytes())==expected for p,expected in pins.items())
    result.update(inputs_unchanged=True,inputs_sha256=pins)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,counts=result['instructions']['counts'],executions=result['instructions']['executions'],
                          coverage=result['instructions']['coverage'])))


if __name__=='__main__':main()
