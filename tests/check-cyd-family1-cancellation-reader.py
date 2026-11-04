"""Synthetic read-only public-cancellation parser controls; no native trace invented.

Native03's exact return/hash conjunct remains unknown. These contract vectors
exercise the independent reader, not a decoder, RTOS task or public API double.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
READER=ROOT/'tests/read-cyd-family1-task-log.py'
OWNER_PROFILES={role:dict(task_handle=handle,core=core,declared_priority=priority,priority_provenance=provenance)
    for role,handle,core,priority,provenance in [('controller',100,0,1,'sdk_main_startup'),
        ('stream',200,0,3,'wrapped_task_creation'),('decode',300,1,5,'wrapped_task_creation'),
        ('output',400,1,6,'wrapped_task_creation')]}


def need(value,reason):
    if not value:raise ValueError(reason)


def contract_rows():
    rows=[]
    def add(tag,**row):rows.append(('CYD_F1_'+tag,row))
    for role,owner in OWNER_PROFILES.items():
        add('CONTROL_OWNER',role=role,**owner,effective_priority_limit=25,live_base_query=0,creation_profile_checked=1)
    for index,name,base,source in [(1,'default3',1000,5),(2,'FINAL',1200,6)]:
        pause=2*index-1
        add('CONTROL_ACQUIRE_START',fixture=name,acquire=index,time_us=base,timeout_ms=10000,source_generation=source,core=0,priority=1)
        add('CONTROL_PAUSE_START',fixture=name,pause=pause,acquire=index,acquire_active=1,requested=1,time_us=base+10,core=0,priority=1)
        if index==1:
            # Real request return can follow the observed concurrent write
            # return; only its existence before real HELD is required.
            add('WRITE_RETURN',fixture=name,call=1,source_generation=source,acquire_entry=0,acquire_return=index,
                pause_start=pause,pause_return=0,pause_acquire=index,pause_requested=1,cancelling=1,start_us=base+5,return_us=base+15,
                result=0x103,data_bytes=768,before_status=0,before_bytes=32,after_status=0,after_bytes=32,equal=1,core=1,priority=6)
        else:
            add('WRITE_RETURN',fixture=name,call=3,source_generation=source,acquire_entry=0,acquire_return=index,
                pause_start=pause,pause_return=1,pause_acquire=index,pause_requested=1,cancelling=1,start_us=base+5,return_us=base+15,
                result=0x103,data_bytes=768,before_status=0,before_bytes=32,after_status=0,after_bytes=32,equal=1,core=1,priority=6)
        add('CONTROL_PAUSE_RETURN',fixture=name,pause=pause,acquire=index,acquire_active=1,requested=1,time_us=base+20,real_returned=1,core=0,priority=1)
        add('CONTROL_ACQUIRE_RETURN',fixture=name,acquire=index,time_us=base+30,result=0,token_epoch=index,source_generation=source,real_returned=1)
        add('CONTROL_ACQUIRE_HELD',fixture=name,acquire=index,time_us=base+40,token_epoch=index,live_clients=0,live_decoders=0,
            input_available=1,input_leased=1,input_ready=0,input_reading=0,input_writing=0,pauses_before=index-1,pauses_after=index,driver_live=0)
        if index==1:
            add('CONTROL_PAUSE_START',fixture=name,pause=2,acquire=1,acquire_active=0,requested=0,time_us=1100,core=0,priority=1)
            add('CONTROL_PAUSE_RETURN',fixture=name,pause=2,acquire=1,acquire_active=0,requested=0,time_us=1110,real_returned=1,core=0,priority=1)
            add('WRITE_RETURN',fixture=name,call=2,source_generation=6,acquire_entry=0,acquire_return=0,pause_start=1,pause_return=1,pause_acquire=1,
                pause_requested=0,cancelling=0,start_us=1120,return_us=1130,result=0,data_bytes=768,before_status=0,before_bytes=32,
                after_status=0,after_bytes=32,equal=1,core=1,priority=6)
    for tag,row in rows:
        if tag not in ('CYD_F1_CONTROL_PAUSE_START','CYD_F1_CONTROL_PAUSE_RETURN'):continue
        role='controller' if row['requested'] else 'stream';owner=OWNER_PROFILES[role]
        row.update(owner,owner_role=role,priority=owner['declared_priority'])
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    out=parser.parse_args().output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local parser control result')
    spec=importlib.util.spec_from_file_location('reviewed_cancellation_contract_reader',READER)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    original=contract_rows();expected=['default3','FINAL'];reader.validate_cancellation_records(original,expected)
    serialized=[tag+' '+' '.join(key+'='+str(value) for key,value in row.items()) for tag,row in original]
    parsed=[reader.fields(line) for line in serialized]
    need(parsed==original,'complete serialized public owner observations preserve integer and text fields')
    reader.validate_cancellation_records(parsed,expected)
    serialized_rejected=[]
    for line in ('CYD_F1_CONTROL_OWNER task_handle=unknown',
                 'CYD_F1_CONTROL_PAUSE_START priority=boosted',
                 'CYD_F1_CONTROL_PAUSE_RETURN declared_priority=controller'):
        try:reader.fields(line)
        except ValueError:serialized_rejected.append(line.split()[1].split('=')[0])
        else:raise ValueError('serialized numeric owner observation accepted text')
    def changed(tag,match,values=None,remove=False):
        rows=copy.deepcopy(original)
        for index,(found,row) in enumerate(rows):
            if found!='CYD_F1_'+tag or not all(row.get(key)==value for key,value in match.items()):continue
            if remove:del rows[index]
            else:row.update(values)
            return rows
        raise ValueError('contract mutation target absent')
    controls=[
        ('mutation_despite_cancellation','WRITE_RETURN',{'call':1},{'equal':0}),
        ('after_hash_failure_despite_cancellation','WRITE_RETURN',{'call':1},{'after_status':-1,'after_bytes':0,'equal':-1}),
        ('before_hash_failure','WRITE_RETURN',{'call':1},{'before_status':-1,'before_bytes':0}),
        ('wrong_return_inside_interval','WRITE_RETURN',{'call':1},{'result':-1}),
        ('memory_error_is_not_cancellation','WRITE_RETURN',{'call':1},{'result':0x101}),
        ('error_outside_acquire','WRITE_RETURN',{'call':1},{'acquire_return':0}),
        ('error_outside_interval_time','WRITE_RETURN',{'call':1},{'return_us':1050}),
        ('error_before_public_request','WRITE_RETURN',{'call':1},{'return_us':1006}),
        ('intent_without_real_pause','WRITE_RETURN',{'call':1},{'pause_start':0}),
        ('missing_cancel_intent','WRITE_RETURN',{'call':1},{'cancelling':0}),
        ('not_requested','WRITE_RETURN',{'call':1},{'pause_requested':0}),
        ('wrong_pause_lifecycle','WRITE_RETURN',{'call':1},{'pause_acquire':2}),
        ('wrong_source_identity','WRITE_RETURN',{'call':1},{'source_generation':99}),
        ('false_call_claimed_as_true_return','WRITE_RETURN',{'call':3},{'pause_return':2}),
        ('unhashed_source','WRITE_RETURN',{'call':1},{'after_bytes':31}),
        ('wrong_output_core','WRITE_RETURN',{'call':1},{'core':0}),
        ('wrong_output_priority','WRITE_RETURN',{'call':1},{'priority':5}),
        ('odd_source_extent','WRITE_RETURN',{'call':1},{'data_bytes':769}),
        ('oversized_source_extent','WRITE_RETURN',{'call':1},{'data_bytes':3074}),
        ('missing_write_return','WRITE_RETURN',{'call':1},None),
        ('pause_not_forwarded','CONTROL_PAUSE_RETURN',{'pause':1},{'real_returned':0}),
        ('missing_pause_return','CONTROL_PAUSE_RETURN',{'pause':1},None),
        ('missing_pause_false_return','CONTROL_PAUSE_RETURN',{'pause':2},None),
        ('missing_HELD','CONTROL_ACQUIRE_HELD',{'acquire':1},None),
        ('acquire_failed','CONTROL_ACQUIRE_RETURN',{'acquire':1},{'result':0x103}),
        ('missing_real_acquire_return','CONTROL_ACQUIRE_RETURN',{'acquire':1},{'real_returned':0}),
        ('missing_token','CONTROL_ACQUIRE_RETURN',{'acquire':1},{'token_epoch':0}),
        ('live_decoder_at_HELD','CONTROL_ACQUIRE_HELD',{'acquire':1},{'live_decoders':1}),
        ('driver_still_live_at_HELD','CONTROL_ACQUIRE_HELD',{'acquire':1},{'driver_live':1}),
        ('no_real_pause_completion','CONTROL_ACQUIRE_HELD',{'acquire':1},{'pauses_after':0}),
        ('real_request_after_HELD','CONTROL_PAUSE_START',{'pause':1},{'time_us':1045}),
        ('wrong_fixture','WRITE_RETURN',{'call':1},{'fixture':'default6'}),
    ]
    rejected=[]
    for name,tag,match,values in controls:
        try:reader.validate_cancellation_records(changed(tag,match,values,remove=values is None),expected)
        except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('contradictory cancellation contract accepted: '+name)
    need(len(rejected)==32,'all independent cancellation/hash/owner controls executed')
    # Effective priority is sampled independently at each real public-call
    # boundary. Public identity and creation provenance stay exact throughout.
    def pause_pair(rows,pause,role=None,start_priority=None,return_priority=None):
        for tag,row in rows:
            if tag not in ('CYD_F1_CONTROL_PAUSE_START','CYD_F1_CONTROL_PAUSE_RETURN') or row['pause']!=pause:continue
            if role is not None:
                owner=OWNER_PROFILES[role];row.update(owner,owner_role=role,priority=owner['declared_priority'])
            value=start_priority if tag.endswith('_START') else return_priority
            if value is not None:row['priority']=value
        return rows
    accepted=[]
    for name,rows in [
        ('controller_effective1_to6',pause_pair(copy.deepcopy(original),1,start_priority=1,return_priority=6)),
        ('controller_effective6_to1',pause_pair(copy.deepcopy(original),1,start_priority=6,return_priority=1)),
        ('controller_stable_effective6',pause_pair(copy.deepcopy(original),1,start_priority=6,return_priority=6)),
        *[(role+'_real_resume_owner',pause_pair(copy.deepcopy(original),2,role=role)) for role in ('stream','decode','output')],
    ]:
        reader.validate_cancellation_records(rows,expected);accepted.append(name)
    extra=[
        ('pause_task_identity_changed','CONTROL_PAUSE_RETURN',{'pause':1},{'task_handle':200}),
        ('pause_owner_role_changed','CONTROL_PAUSE_RETURN',{'pause':1},{'owner_role':'stream'}),
        ('pause_declared_priority_changed','CONTROL_PAUSE_RETURN',{'pause':1},{'declared_priority':3}),
        ('pause_creation_provenance_changed','CONTROL_PAUSE_RETURN',{'pause':1},{'priority_provenance':'live_base_query'}),
        ('controller_effective_below_declared','CONTROL_PAUSE_RETURN',{'pause':1},{'priority':0}),
        ('controller_effective_out_of_range','CONTROL_PAUSE_RETURN',{'pause':1},{'priority':25}),
        ('unknown_public_caller_handle','CONTROL_PAUSE_START',{'pause':1},{'task_handle':999}),
        ('resume_wrong_declared_priority','CONTROL_PAUSE_START',{'pause':2},{'declared_priority':1}),
        ('resume_wrong_core','CONTROL_PAUSE_START',{'pause':2},{'core':1}),
        ('resume_effective_below_declared','CONTROL_PAUSE_RETURN',{'pause':2},{'priority':2}),
        ('missing_public_owner_registry','CONTROL_OWNER',{'role':'controller'},None),
        ('duplicate_public_task_handle','CONTROL_OWNER',{'role':'stream'},{'task_handle':100}),
        ('wrong_created_profile','CONTROL_OWNER',{'role':'decode'},{'declared_priority':6}),
        ('wrong_created_core','CONTROL_OWNER',{'role':'output'},{'core':0}),
        ('invented_live_base_query','CONTROL_OWNER',{'role':'controller'},{'live_base_query':1}),
        ('loosened_effective_priority_limit','CONTROL_OWNER',{'role':'controller'},{'effective_priority_limit':26}),
    ]
    owner_rejected=[]
    def deny(name,rows):
        try:reader.validate_cancellation_records(rows,expected)
        except ValueError as error:owner_rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('contradictory public owner contract accepted: '+name)
    for name,tag,match,values in extra:deny(name,changed(tag,match,values,remove=values is None))
    deny('registered_stream_cannot_issue_true_request',pause_pair(copy.deepcopy(original),1,role='stream'))
    deny('controller_resume_after_HELD_is_not_an_abort_path',pause_pair(copy.deepcopy(original),2,role='controller'))
    for name,fields in [('unknown_matching_caller_handle',{'task_handle':999}),
        ('matching_wrong_owner_role',{'owner_role':'decode'}),('matching_wrong_declared_priority',{'declared_priority':1}),
        ('matching_wrong_core',{'core':1}),('matching_wrong_provenance',{'priority_provenance':'sdk_main_startup'})]:
        candidate=copy.deepcopy(original)
        for tag,row in candidate:
            if tag in ('CYD_F1_CONTROL_PAUSE_START','CYD_F1_CONTROL_PAUSE_RETURN') and row['pause']==2:row.update(fields)
        deny(name,candidate)
    for role in ('decode','output'):
        owner=OWNER_PROFILES[role]
        deny(role+'_resume_below_declared',pause_pair(copy.deepcopy(original),2,role=role,return_priority=owner['declared_priority']-1))
    missing=changed('CONTROL_PAUSE_START',{'pause':1},{})
    del next(row for tag,row in missing if tag=='CYD_F1_CONTROL_PAUSE_START' and row['pause']==1)['task_handle']
    deny('missing_pause_task_handle',missing)
    out.mkdir(parents=True);(out/'reader.py').write_bytes(READER.read_bytes());(out/'controller.py').write_bytes(Path(__file__).read_bytes())
    report=dict(passed=True,synthetic_parser_contract_vectors=True,native03_specific_failed_conjunct_known=False,
        source_mutation_proven=False,original_native03_modified=False,SDK_started=False,QEMU_started=False,
        rejected_controls=len(rejected),rejected=rejected,owner_positive_controls=accepted,
        owner_rejected_controls=owner_rejected,live_base_priority_query=False,
        serialized_owner_roundtrip=True,serialized_numeric_rejections=serialized_rejected,
        reader_sha256=hashlib.sha256(READER.read_bytes()).hexdigest())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,rejected_controls=32,owner_positive_controls=len(accepted),
        owner_rejected_controls=len(owner_rejected),synthetic_parser_contract_vectors=True,native03_specific_failed_conjunct_known=False)));return 0


if __name__=='__main__':raise SystemExit(main())
