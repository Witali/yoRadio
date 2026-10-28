"""Verify callback producer arguments and the real BSS peer/PM timer data path."""
import argparse
from dataclasses import asdict,replace
import hashlib
from importlib.metadata import version
from itertools import product
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import Image,sha
from reverse.rv32_link_match import size_at
from reverse.wifi_producers import qualify
from timer_event11_model import State
from timer_event11_semantics import reader
from tx_null_model import NullState
from wifi_producer_instructions import CallbackProbe,BssProbe
from wifi_producer_model import callback_expected,bss_expected,period_domain

PERIODS=(0,1,2,3,4,5,8,10,100,4194,4195,4196,4197,4198,32767,32768,32771,32772,32773,65535)


def callback_cases():
    """Cover every status byte and representative independent descriptor flag bits."""
    for sleep,status,flags,pending in product((0,1),range(256),(0,1,2,3,0x80000000,0x80000001,0xffffffff),(0,1)):
        yield NullState(byte21=1,byte22=1,byte488=pending,enabled52=1,word36=1,period72=10),dict(
            sleep=sleep,status=status,flags=flags,peerflag=1)
    for sleep,status,flags,b15,b16,b9 in product((0,1),(0,1,2,255),(0,1),(0,1),(0,1),(0,15,16,255)):
        yield NullState(byte15=b15,byte16=b16,byte9=b9,byte21=1,byte22=1,byte488=1,byte26=1),dict(
            sleep=sleep,status=status,flags=flags,peerflag=1)


def instructions(qualification,factory,native):
    """Run untouched producer/consumer code and compare every declared observable effect."""
    reads={'factory':reader(factory),'native':reader(native)}
    callbacks={v:CallbackProbe(qualification['layouts'][v],read) for v,read in reads.items()}
    bss={v:BssProbe(qualification['layouts'][v],read) for v,read in reads.items()}
    digest,counts,samples=hashlib.sha256(),{'callback_per_image':0,'bss_per_image':0,'feature_per_image':0},{}
    for state,kwargs in callback_cases():
        observed={}
        for variant,probe in callbacks.items():
            actual=probe.call_callback(state,0x100000080,**kwargs)
            wanted=callback_expected(variant,state,0x100000080,**kwargs)
            assert actual==wanted,(variant,asdict(state),kwargs,actual,wanted)
            observed[variant]=actual
        record=dict(kind='callback',state=asdict(state),arguments=kwargs,observed=observed)
        digest.update((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
        counts['callback_per_image']+=1
        if kwargs['status']==1 and state.byte488 and kwargs['flags'] in (0,1):
            samples.setdefault('callback-flag-'+str(kwargs['flags']),record)
    state=State(word36=0,enabled52=255,period72=123,fallback28=60000000,adjustment56=17)
    cases=[(state,p,o,True,True,None) for p,o in product(PERIODS,range(256))]
    cases.extend((replace(state,word36=w,fallback28=f),p,o,present,True,None)
        for w,f,p,o,present in product((0,1),(0,60000000),(0,1,4197,32772,65535),(0,255),(False,True)))
    cases.extend((state,0,0,False,False,word) for word in (0,1,255,256,257,511,512,0x80000000,0xffffffff))
    for state,period,options,present,connect,feature_word in cases:
        observed={}
        for variant,probe in bss.items():
            actual=probe.call_chain(state,period,options,present,connect,feature_word)
            wanted=bss_expected(variant,state,period,options,present,connect,feature_word)
            assert actual==wanted,(variant,asdict(state),period,options,present,feature_word,actual,wanted)
            observed[variant]=actual
        record=dict(kind='bss',state=asdict(state),period=period,options=options,present=present,
            connect=connect,feature_word=feature_word,observed=observed)
        digest.update((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
        counts['feature_per_image' if feature_word is not None else 'bss_per_image']+=1
        if period in (4196,4197,32772,65535) and present and feature_word is None:
            samples.setdefault('period-'+str(period),record)
        if not present and feature_word is None:samples.setdefault('absent-ie-retains-peer',record)
    coverage={}
    for variant in reads:
        coverage[variant]=[]
        for names,probe in ((('pm_send_sleep_null_cb','pm_send_wake_null_cb'),callbacks[variant]),
                (('ieee80211_set_bss_max_idle_period','cnx_sta_pm.part.0','sta_is_bss_max_idle_enabled'),bss[variant])):
            for name in names:
                row=next(r for r in qualification['layouts'][variant]['functions'] if r['name']==name)
                start=int(row['start'],0);code=reads[variant](start,row['linked_bytes']);addresses=set();offset=0
                while offset<len(code):addresses.add(start+offset);offset+=size_at(code,offset)
                missing=addresses-probe.visited
                assert not missing,(variant,name,sorted(map(hex,missing)))
                coverage[variant].append(dict(name=name,bytes=len(code),instruction_starts=len(addresses),visited=len(addresses)))
    assert len(samples)==7
    native_timer=next(call for call in samples['period-4197']['observed']['native']['calls'] if call[0]=='arm240')
    factory_timer=next(call for call in samples['period-32772']['observed']['factory']['calls'] if call[0]=='arm224')
    assert native_timer==['arm240',760704,0] and factory_timer==['arm224',0,0]
    defects=dict(native=dict(input_period=4197,actual_microseconds=native_timer[1],
                            expected_microseconds=4295728000),
                 factory=dict(input_period=32772,enabled=True,actual_milliseconds=factory_timer[1]))
    return dict(passed=True,counts=counts,executions=2*sum(counts.values()),trace_sha256=digest.hexdigest(),
        coverage=coverage,samples=samples,period_domain=period_domain(),conditional_defect_witnesses=defects,
        timer_safety_gate_passed=False,pm_start_and_platform_helpers_stubbed=True,
        full_association_body_executed=False,runtime_registration_proved=False,station_pointer_lifetime_proved=False,
        whole_image_completeness_proved=False,physical_hardware_tested=False)


def run(factory,reference,native,app,old_pp,new_pp,old_net,new_net,sdkconfig):
    """Keep conditional timer failures visible rather than treating them as acceptance."""
    qualified=qualify(factory,reference,native,app,old_pp,new_pp,old_net,new_net)
    result=instructions(qualified,factory,native)
    text=sdkconfig.decode('utf-8')
    assert re.search(r'^# CONFIG_ESP_WIFI_BSS_MAX_IDLE_SUPPORT is not set\r?$',text,re.M)
    rejected=[];image=Image(factory)
    row=next(r for r in qualified['layouts']['factory']['functions'] if r['name']=='pm_send_sleep_null_cb')
    raw=image.read(int(row['start'],0),row['linked_bytes'],True)
    changed=raw.replace(bytes.fromhex('83c53701'),bytes.fromhex('83c54701'),1)
    assert changed!=raw
    ie=next(r for r in qualified['layouts']['factory']['functions'] if r['name']=='ieee80211_set_bss_max_idle_period')
    ie_raw=image.read(int(ie['start'],0),ie['linked_bytes'],True)
    wrong_period=ie_raw.replace(bytes.fromhex('2319e532'),bytes.fromhex('2319e531'),1)
    wrong_options=ie_raw.replace(bytes.fromhex('858b'),bytes.fromhex('898b'),1)
    assert wrong_period!=ie_raw and wrong_options!=ie_raw
    faults={
        'wrong-net-library':lambda:qualify(factory,reference,native,app,old_pp,new_pp,new_net,old_net),
        'truncated-callback':lambda:qualify(factory,reference,native,app,old_pp,new_pp,old_net,new_net,
            {('factory','pm_send_sleep_null_cb'):raw[:-2]}),
        'wrong-status-field':lambda:qualify(factory,reference,native,app,old_pp,new_pp,old_net,new_net,
            {('factory','pm_send_sleep_null_cb'):changed}),
        'wrong-peer-period':lambda:qualify(factory,reference,native,app,old_pp,new_pp,old_net,new_net,
            {('factory','ieee80211_set_bss_max_idle_period'):wrong_period}),
        'wrong-options-mask':lambda:qualify(factory,reference,native,app,old_pp,new_pp,old_net,new_net,
            {('factory','ieee80211_set_bss_max_idle_period'):wrong_options}),
    }
    for name,action in faults.items():
        try:action()
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Invalid producer accepted: '+name)
    return dict(passed=True,qualification=qualified,instructions=result,rejected_controls=rejected,
        archived_sdkconfig_sha256=sha(sdkconfig),archived_sdkconfig_bss_max_idle_enabled=False,
        conditional_timer_range_defects_present=True,production_runtime_enablement_proved=False,
        engines={'unicorn':version('unicorn'),'pyelftools':version('pyelftools')},
        full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Write a fresh offline result while preserving all original proof inputs."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','reference','native','app','old-pp','new-pp','old-net','new-net','sdkconfig','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve producer evidence')
    root=Path(__file__).resolve().parents[1]
    sources=('tests/wifi_producer_test.py','tests/wifi_producer_model.py','tests/wifi_producer_instructions.py',
        'tools/reverse/wifi_producers.py','tests/tx_null_instructions.py','tests/tx_null_model.py',
        'tools/reverse/tx_null.py','tests/keep_alive_instructions.py','tests/keep_alive_model.py',
        'tests/timer_event11_instructions.py','tests/timer_event11_model.py','tests/timer_event11_semantics.py',
        'tools/reverse/timer_tim.py','tools/reverse/timer_keep_alive.py','tools/reverse/timer_event11_match.py',
        'tools/reverse/rv32_link_match.py','tools/reverse/elf_archive.py','tools/reverse/nothrow_linkage.py','tools/audit_factory_xrefs.py')
    files=[getattr(args,n.replace('-','_')) for n in ('factory','reference','native','app','old-pp','new-pp','old-net','new-net','sdkconfig')]
    files.extend(root/name for name in sources)
    pins={str(path.resolve()):sha(path.read_bytes()) for path in files}
    if args.output.resolve() in [path.resolve() for path in files]:raise ValueError('Producer output aliases input')
    result=run(args.factory.read_bytes(),args.reference.read_bytes(),args.native.read_bytes(),args.app.read_bytes(),
        args.old_pp,args.new_pp,args.old_net,args.new_net,args.sdkconfig.read_bytes())
    assert all(sha(Path(path).read_bytes())==digest for path,digest in pins.items())
    result.update(inputs_sha256=pins,inputs_unchanged=True)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,counts=result['instructions']['counts'],executions=result['instructions']['executions'],
        coverage=result['instructions']['coverage'],period_domain=result['instructions']['period_domain'],controls=result['rejected_controls'])))


if __name__=='__main__':main()
