"""Synthetic scheduler-census parser controls; no native execution is claimed."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
READER=ROOT/'tests/read-cyd-family1-task-log.py'


def need(value,reason):
    if not value:raise ValueError(reason)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();source=args.contract.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists() and source.is_relative_to(ROOT/'.build'),'fresh local synthetic metadata controls')
    contract=json.loads(source.read_bytes());spec=importlib.util.spec_from_file_location('reviewed_fairness_reader',READER)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    records=[]
    for expected in reader.fairness_expectations(contract):
        position=expected['position'];one=expected['schedule']==1 and expected['complete_transport'];maximum=1 if one else min(257,position)
        reads=(position+maximum-1)//maximum;first=expected['ordinal']*1000000
        row=dict(expected,generation=expected['ordinal'],positive_reads=reads,positive_bytes=position,max_positive_read=maximum,
            one_tick_started=2 if one else 0,one_tick_returned=2 if one else 0,other_started=0,other_returned=0,
            first_delay_read=1 if one else 0,last_delay_read=reads-1 if one else 0,
            first_positive_us=first,last_positive_us=first+90000,first_delay_us=first+20000 if one else 0,
            last_delay_us=first+80000 if one else 0,cleanup_us=first+100000,cleanup_real_returned=1,diagnostic_delays=0,core=0,priority=3)
        records.append(row)
    value=reader.validate_stream_fairness_records(records,contract)
    need(len(value['client_records'])==58 and len(value['complete_one_byte'])==5,'complete unchanged synthetic scope')
    target=next(i for i,row in enumerate(records) if row['fixture']=='full120' and row['schedule']==1)
    controls=[
        ('missing_census',None),('wrong_client',{'ordinal':0}),('wrong_fixture',{'fixture':'default3'}),
        ('wrong_schedule',{'schedule':2}),('wrong_source_generation',{'generation':0}),
        ('shortened_encoded_source',{'encoded_bytes':1}),('missing_positive_byte',{'positive_bytes':records[target]['positive_bytes']-1}),
        ('one_byte_schedule_coalesced',{'max_positive_read':2}),('read_count_not_one_byte',{'positive_reads':records[target]['positive_reads']-1}),
        ('delay_did_not_really_return',{'one_tick_returned':1}),('other_delay_did_not_return',{'other_started':1}),
        ('long_one_byte_never_yielded',{'one_tick_started':0,'one_tick_returned':0,'first_delay_read':0,'last_delay_read':0,'first_delay_us':0,'last_delay_us':0}),
        ('delay_only_after_final_read',{'first_delay_read':records[target]['positive_reads'],'last_delay_read':records[target]['positive_reads']}),
        ('delay_before_positive_input',{'first_delay_read':0}),('delay_after_input_extent',{'last_delay_read':records[target]['positive_reads']+1}),
        ('delay_before_first_positive_time',{'first_delay_us':records[target]['first_positive_us']-1}),
        ('delay_after_real_cleanup',{'last_delay_us':records[target]['cleanup_us']+1}),
        ('cleanup_not_forwarded',{'cleanup_real_returned':0}),('observer_added_delay',{'diagnostic_delays':1}),
        ('wrong_owner_core',{'core':1}),('wrong_owner_priority',{'priority':5}),
        ('complete_input_labelled_partial',{'complete_transport':0,'partial_transport':1}),
        ('unobserved_zero_count_has_time',{'one_tick_started':0,'one_tick_returned':0}),
        ('negative_actual_delay_count',{'one_tick_started':-1,'one_tick_returned':-1}),
    ]
    rejected=[]
    for name,changes in controls:
        changed=copy.deepcopy(records)
        if changes is None:del changed[target]
        else:changed[target].update(changes)
        try:reader.validate_stream_fairness_records(changed,contract)
        except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('contradictory forwarding scheduler census accepted: '+name)
    out.mkdir(parents=True)
    for path,name in [(READER,'reader.py'),(Path(__file__).resolve(),'controller.py')]: (out/name).write_bytes(path.read_bytes())
    report=dict(passed=True,synthetic_parser_contract_vectors=True,actual_native05_status='NONPASS',native05_changed=False,
        native_fairness_qualified=False,SDK_started=False,QEMU_started=False,client_records=len(records),complete_one_byte_cases=5,
        rejected_controls=len(rejected),rejected=rejected,reader_sha256=hashlib.sha256(READER.read_bytes()).hexdigest(),
        contract_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,synthetic_parser_contract_vectors=True,rejected_controls=len(rejected),native_fairness_qualified=False)));return 0


if __name__=='__main__':raise SystemExit(main())
