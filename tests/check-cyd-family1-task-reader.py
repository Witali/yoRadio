"""Reject contradictory copies of a genuine completed full family1 task gate.

This starts no compiler/SDK/decoder/QEMU and never changes original evidence.
The original independent Decimal golden package is authenticated and reused;
these contradiction checks do not claim to rerun its numerical calculation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]
READER=ROOT/'tests/read-cyd-family1-task-log.py'
OUTPUT=ROOT/'tests/prepare-cyd-family1-task-output.py'
FAULT_READER=ROOT/'tests/read-cyd-family1-allocation-faults.py'
WORD_READER=ROOT/'tests/read-cyd-family1-word-alloc.py'
SOURCE_RELEASE=ROOT/'.build/cyd-family1-source-release-20261103-02.json'
SOURCE_SHA='745e7482cd90517c4e5778717dd7e1016d4e8c692d125f4a3cf15302e7dc9381'
SUCCESSOR_PRODUCER_SHA='89fdf896046b51ed81df07965461ee7805af23a20b9bd89a89a7fc325f0e6962'


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))


def contained(base,name):
    p=Path(name);need(not p.is_absolute() and '..' not in p.parts,'contained relative evidence path')
    p=(base/p).resolve();need(p.is_relative_to(base.resolve()),'evidence cannot escape through symlink');return p


def pinned(path,pin,reason):
    need(identity(path)==dict(bytes=pin['bytes'],sha256=pin['sha256']),reason)


def native_inputs(native,report,sources,allow_reader_metadata=False):
    """Authenticate recorded build data without executing its tools or scripts."""
    bundle=json.loads((native/'execution-bundle.json').read_bytes())
    closure=json.loads((native/'actual-compiler-closure.json').read_bytes())
    child=json.loads((native/'sdk-child.json').read_bytes())
    need(bundle['sources']==sources and bundle['pcm_reference']==bundle['expected_cases']==report['pcm_reference'],
         'complete original source graph and exact fixture contract')
    need(bundle['sdk_commit']=='7101770dc6db2667b3c477cc31365dd1acd6db4e' and
         bundle['vendor_commit']=='67b8d0e98f58c774b8652480893037273190e8dc','recorded pinned SDK/vendor identities')
    need(child['pid']>0 and child['exit_status']==0 and report['target_executed'] and report['all_bound_inputs_current'],
         'original real SDK child and source checks completed')
    for row in report['commands']:
        need(re.fullmatch('[A-Za-z0-9_-]+',row['name']) and row['pid']>0 and row['state']=='complete' and row['exit_status']==0,
             'all original actual processes are terminal zero')
        for stream in ('stdout','stderr'):
            need(sha(contained(native,row['name']+'.'+stream+'.log'))==row[stream+'_sha256'],'original raw command logs authenticated')
    need(sum(row['name']=='build' for row in report['commands'])==sum(row['name']=='qemu' for row in report['commands'])==1,
         'one actual original build and guest')
    for name,digest in bundle['artifacts'].items():need(sha(contained(native,name))==digest,'all original build/image/ELF/map/config artifacts')
    for original,pin in sources.items():
        snapshot=contained(native,pin['snapshot']);pinned(snapshot,pin,'unchanged original frozen source bytes')
        if allow_reader_metadata and Path(original).resolve()==READER:
            before=snapshot.read_bytes();after=READER.read_bytes()
            old=b"    words={'fixture','id','kind','sha256','stage','hex','role','sdk','operation','phase','function'};row={}\n"
            new=b"    words={'fixture','id','kind','sha256','stage','hex','role','sdk','operation','phase','function',\n           'owner_role','priority_provenance'};row={}\n"
            need(pin['sha256']=='9dad2bb62b597887d44475e61728658b6b8c9e5cdc10dc775f3130e6baa3f3f0' and
                 before.count(old)==1 and before.replace(old,new,1)==after,'only exact reviewed two textual parser keys differ')
            need(original not in {r['manifest_original'] for r in closure['dependencies'].values()},'parser exception is never compiled')
        else:pinned(original,pin,'every current original source/config/dependency remains exact')
    for path,pin in closure['dependencies'].items():
        need(pin['manifest_original'] in sources and sha(path)==pin['sha256']==sources[pin['manifest_original']]['sha256'],
             'all actual compiler dependencies remain current without compiled exceptions')
    for unit in closure['translation_units']:
        path=Path(unit['output']);path=path if path.is_absolute() else Path(unit['directory'])/path;path=path.resolve()
        need(path.is_relative_to(native) and path.relative_to(native).as_posix() in bundle['artifacts'] and
             sha(path)==bundle['artifacts'][path.relative_to(native).as_posix()],'all actual compiled objects authenticated')
        need(all(p in closure['dependencies'] for p in unit['actual_dependency_paths']),'whole actual TU dependency lists bound')
    need(sha(SOURCE_RELEASE)==SOURCE_SHA and report['production_source_release_sha256']==SOURCE_SHA,'exact original production35 release')
    production=json.loads(SOURCE_RELEASE.read_bytes());need(len(production['files'])==35,'all35 production inputs')
    for name,pin in production['files'].items():
        pinned(ROOT/name,pin,'current exact production35 source')
        need(sources[str(ROOT/name)]['sha256']==pin['sha256'],'released production joins original compiler graph')
    for label,digest in bundle['runtime'].items():
        path=shutil.which(label.split(':',1)[1]) if label.startswith('runtime-path-redacted:') else label
        need(path and sha(path)==digest,'current original tool/ROM identities')
    return bundle,closure


def data_successor(native,successor,report,sources):
    need(successor.is_relative_to(ROOT/'.build') and successor.is_dir() and successor!=native and
         not successor.is_relative_to(native) and not native.is_relative_to(successor),'separate explicit local data successor')
    value=json.loads((successor/'report.json').read_bytes())
    required=dict(schema='cyd-family1-data-successor-v1',passed=True,completed=True,preflight_passed=True,
        metadata_only_successor=True,original_capture=native.relative_to(ROOT).as_posix(),original_status='NONPASS; unmodified',
        native_executed_here=False,SDK_build_started_here=False,inherited_native_execution=True,archived_code_executed=False,
        current_live_validators_executed=True,new_numeric_tolerance=False,full_pcm_independent_oracle=True,
        physical_hardware=False,performance_or_full_radio_resource_claim=False,reader_complete_cases=48,
        direct_reference_captures=13,owner_provenance_observed=True,all_bindings_current_after=True)
    need(all(type(value.get(k)) is type(v) and value[k]==v for k,v in required.items()),'exact completed data-only successor scope')
    need(not report['passed'] and not report['completed'] and report['failure_type']=='ValueError' and
         report['failure']=='strict actual integer observation','original NONPASS remains unchanged and is never relabelled')
    metadata={'report.json','execution-bundle.json','source-manifest.json','actual-compiler-closure.json','sdk-child.json','reference-contract.json'}
    need(set(value['original_metadata_pins'])==metadata,'complete original metadata identity set')
    for name,digest in value['original_metadata_pins'].items():need(sha(native/name)==digest,'successor binds exact original metadata bytes')
    artifacts={'bindings-before.json','bindings-after.json','measurements.json','word-allocations.json','post-output-oracle.json',
        'reviewed-reader-change.patch'}|{'reference-'+str(i)+'.pcm' for i in range(13)}|{
        'current-validators/'+p.name for p in (READER,OUTPUT,FAULT_READER,WORD_READER)}
    need(set(value['post_artifacts'])==artifacts,'all complete successor PCM/oracle/current-validator artifacts required')
    for name,pin in value['post_artifacts'].items():pinned(contained(successor,name),pin,'all successor artifacts unchanged')
    before=json.loads((successor/'bindings-before.json').read_bytes());after=json.loads((successor/'bindings-after.json').read_bytes())
    need(before==after and before['current-data-tool:script']==dict(bytes=14987,sha256=SUCCESSOR_PRODUCER_SHA),
         'exact reviewed data producer and before/after binding census')
    for path in (READER,OUTPUT,FAULT_READER,WORD_READER):
        relative=path.relative_to(ROOT).as_posix();pinned(path,before['validator:'+relative],'current executed successor validators exact')
        pinned(successor/'current-validators'/path.name,before['validator:'+relative],'frozen successor validators exact')
    bundle,closure=native_inputs(native,report,sources,allow_reader_metadata=True)
    for index,(original,pin) in enumerate(sources.items()):pinned(original,before['source:'+str(index)],'successor source binding is current')
    for name,pin in value['original_metadata_pins'].items():pinned(native/name,before['original:'+name],'successor original metadata binding current')
    for name in bundle['artifacts']:pinned(contained(native,name),before['artifact:'+name],'successor inherited artifact binding current')
    for row in report['commands']:
        for stream in ('stdout','stderr'):
            name=row['name']+'.'+stream+'.log';pinned(native/name,before['command:'+name],'successor inherited process log binding current')
    inherited=value['inherited_execution']
    need(inherited['source_snapshots']==len(sources)==560 and inherited['actual_compiler_dependencies']==len(closure['dependencies'])==471 and
         inherited['actual_translation_units']==len(closure['translation_units'])==18 and inherited['compiled_source_exceptions']==0 and
         inherited['only_current_source_exception']==READER.relative_to(ROOT).as_posix(),'whole inherited compiler graph and sole metadata exception')
    oracle=json.loads((successor/'post-output-oracle.json').read_bytes())
    need(oracle['passed'] and oracle['complete_cases']==48 and oracle['decimal_precision_digits']==[100,160] and
         oracle['new_tolerance_applied'] is False,'original full independent Decimal package authenticated, not recalculated')
    return value,json.loads((successor/'measurements.json').read_bytes()),json.loads((successor/'word-allocations.json').read_bytes()),oracle


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--capture',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--data-successor',type=Path,help='Explicit completed data-only successor; original native NONPASS is preserved')
    args=parser.parse_args();native=args.capture.resolve();out=args.output.resolve()
    need(native.is_relative_to(ROOT/'.build') and native.is_dir() and out!=ROOT/'.build' and out.is_relative_to(ROOT/'.build') and not out.exists() and
         not out.is_relative_to(native) and not native.is_relative_to(out),'genuine native capture and fresh separate local witness')
    report=json.loads((native/'report.json').read_bytes());sources=json.loads((native/'source-manifest.json').read_bytes())
    successor=args.data_successor.resolve() if args.data_successor else None
    if successor:
        need(not out.is_relative_to(successor) and not successor.is_relative_to(out),'witness cannot overlap original data successor')
        successor_report,expected_measured,expected_word,oracle=data_successor(native,successor,report,sources)
        data_root=successor
    else:
        need(report['passed'] and report['completed'] and report['target_executed'] and report['all_bound_inputs_current'] and report['post_output_oracle']['passed'],
             'original actual native and full independent Decimal gate completed')
        native_inputs(native,report,sources)
        for path in (READER,OUTPUT,FAULT_READER,WORD_READER):
            pin=sources[str(path.resolve())]
            need(path.read_bytes()==(native/pin['snapshot']).read_bytes() and sha(path)==pin['sha256'],'current exact executed canonical reader/oracle')
        for name,pin in report['post_output_artifacts'].items():pinned(contained(native,name),pin,'complete original post-oracle artifacts unchanged')
        expected_measured,expected_word,oracle=report['measurements'],report['word_allocations'],report['post_output_oracle']
        data_root=native
    read=module('current_reviewed_family1_task_log',READER);output=module('current_reviewed_family1_output_data',OUTPUT)
    word=module('current_reviewed_family1_word_log',WORD_READER)
    original=((native/'qemu.stdout.log').read_text('utf-8')+'\n'+(native/'qemu.stderr.log').read_text('utf-8')).replace('\r\n','\n')
    measured,pcm=read.validate(original,report['pcm_reference'])
    need(json.loads(json.dumps(measured))==expected_measured,'whole original genuine transcript accepted against explicit data proof')
    need(word.parse_word_allocation_log(original)==expected_word,'complete original public word-pointer trace accepted')
    need(all((data_root/('reference-'+str(i)+'.pcm')).read_bytes()==body for i,body in enumerate(pcm)),
         'all13 retained reference PCM are the actual unchanged original UART bytes')
    stocks={index:body for index,body in enumerate(pcm)}
    for index,pin in output.LEGACY_PCM.items():
        raw=(ROOT/pin['path']).read_bytes();need(len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256'],'complete original stock reference')
        stocks[index]=raw[pin['offset']:pin['offset']+pin['logical_bytes']]
    expected_cases=[]
    for plan in report['pcm_reference']['cases']:
        digest=hashlib.sha256()
        for link in plan['links']:digest.update(stocks[link['reference']])
        expected_cases.append(digest.hexdigest())
    golden={(row['reference'],row['gain_q8'],row['volume']):row for row in oracle['full_mono_references']}
    def evaluate(text):
        value,_=read.validate(text,report['pcm_reference']);word.parse_word_allocation_log(text);cursor=0
        for case,plan,expected in zip(value['cases'],report['pcm_reference']['cases'],expected_cases):
            need(case['sha256']==expected,'whole actual source case equals independent captured integer PCM')
            for link in plan['links']:
                pin=golden[(link['reference'],link['gain_q8'],plan['volume'])];row=value['render_links'][cursor];cursor+=1
                need(row['sha256']==pin['sha256'] and row['bytes']==pin['bytes'],'actual complete mono equals original independent Decimal golden')
        need([row['sha256'] for row in value['render_cases']]==[row['sha256'] for row in measured['render_cases']],
             'whole original independently qualified driver-chain hashes retained')
        return value
    evaluate(original)
    preserved={native/'report.json',native/'execution-bundle.json',native/'source-manifest.json',native/'actual-compiler-closure.json',
               native/'sdk-child.json',native/'qemu.stdout.log',native/'qemu.stderr.log',data_root/'post-output-oracle.json',READER,OUTPUT,FAULT_READER,WORD_READER}
    if successor:preserved|={successor/'report.json',*(contained(successor,name) for name in successor_report['post_artifacts'])}
    originals={str(path):sha(path) for path in preserved}
    def alter(tag,match,changes=None,remove=False,text=None):
        lines=(original if text is None else text).splitlines()
        for index,line in enumerate(lines):
            if not line.startswith(tag+' '):continue
            _,row=read.fields(line)
            if not all(str(row.get(key))==str(value) for key,value in match.items()):continue
            if remove:del lines[index]
            else:
                for key,value in changes.items():need(key in row,'control changes actual original field');row[key]=value(row[key]) if callable(value) else value
                lines[index]=tag+' '+' '.join(key+'='+str(value) for key,value in row.items())
            return '\n'.join(lines)
        raise ValueError('genuine mutation target missing: '+tag)
    case='CYD_F1_TASK_CASE';end='CYD_F1_TASK_COMPLETE';link='CYD_F1_LINK';render='CYD_F1_RENDER_LINK'
    controls=[
        ('missing_active_C8_120_maintenance',lambda:alter(case,{'fixture':'active8_120','id':'T2'},remove=True)),
        ('C8_120_shortened_to20ms',lambda:alter(link,{'fixture':'active8_120'},{'bytes':25600})),
        ('C8_truncated_stereo',lambda:alter(link,{'fixture':'default8'},{'channels':2})),
        ('mapped_layout_lost',lambda:alter('CYD_F1_METADATA',{'fixture':'default6'},{'layout':0})),
        ('legacy_layout_reset_lost',lambda:alter('CYD_F1_METADATA',{'fixture':'LAYOUT_GAIN_CHAIN','index':2},{'layout':1})),
        ('queued_header_gain_lost',lambda:alter('CYD_F1_METADATA',{'fixture':'LAYOUT_GAIN_CHAIN','index':1},{'gain_q8':1536})),
        ('logical_channel_metadata_lost',lambda:alter('CYD_F1_METADATA',{'fixture':'default8'},{'channels':2})),
        ('public_state_truncated',lambda:alter('CYD_F1_STATE_INFO',{'fixture':'default8'},{'channels':0})),
        ('reference_full_hash_changed',lambda:alter('CYD_F1_REFERENCE_CASE',{'index':12},{'sha256':'0'*64})),
        ('reference_pixel_byte_changed',lambda:alter('CYD_F1_REFERENCE_PCM',{'index':12},{'hex':lambda value:('00' if value[:2]!='00' else '01')+value[2:]})),
        ('reference_offset_gap',lambda:alter('CYD_F1_REFERENCE_PCM',{'index':12},{'offset':1})),
        ('reference_helpers_not_independent',lambda:alter('CYD_F1_REFERENCE_CASE',{'index':12},{'private_helpers':1})),
        ('reference_worker_wrong_core',lambda:alter('CYD_F1_REFERENCE_CASE',{'index':12},{'core':0})),
        ('reference_real_public_open_failed',lambda:alter('CYD_F1_REFERENCE_OPEN',{'index':12},{'result':-3})),
        ('reference_missing_real_close',lambda:alter('CYD_F1_REFERENCE_CLOSE',{'index':12},remove=True)),
        ('wrong_stream_core',lambda:alter('CYD_F1_TASK_PROFILE',{'role':'stream'},{'core':1})),
        ('wrong_decoder_stack',lambda:alter('CYD_F1_TASK_PROFILE',{'role':'decode'},{'stack':8192})),
        ('wrong_output_priority',lambda:alter('CYD_F1_TASK_PROFILE',{'role':'output'},{'priority':5})),
        ('Stop_discard_wrong_owner',lambda:alter('CYD_F1_CONTROL_DISCARD',{}, {'core':0})),
        ('Stop_wrong_discard_sequence',lambda:alter('CYD_F1_CONTROL_STOP_QUIET',{'fixture':'active8_120'},{'discard_sequence':lambda value:value+1})),
        ('Stop_output_continues',lambda:alter('CYD_F1_CONTROL_STOP_QUIET',{'fixture':'default8'},{'driver_writes':lambda value:value+1})),
        ('Stop_input_held',lambda:alter('CYD_F1_CONTROL_STOP_QUIET',{'fixture':'default6'},{'input_reading':1})),
        ('Stop_wrong_early_boundary',lambda:alter('CYD_F1_CONTROL_TRANSPORT_HELD',{'fixture':'active8_120'},{'position':lambda value:value+1})),
        ('held_read_faked',lambda:alter('CYD_F1_CONTROL_TRANSPORT_HELD',{}, {'genuine_read':0})),
        ('stale_token_accepted',lambda:alter(case,{'fixture':'active8_120','id':'T2'},{'stale_rejected':0})),
        ('maintenance_play_not_blocked',lambda:alter(case,{'fixture':'default6','id':'T2'},{'play_blocked':0})),
        ('raw_public_error_relabelled_success',lambda:alter('CYD_F1_OBS_CALL',{'kind':'raw'},{'result':-3})),
        ('raw_consumed_overrun',lambda:alter('CYD_F1_OBS_CALL',{'kind':'raw'},{'consumed':lambda value:value+100000})),
        ('raw_missing_public_close',lambda:alter('CYD_F1_OBS_CLOSE',{'kind':'raw'},remove=True)),
        ('raw_buffer_still_pending_at_close',lambda:alter('CYD_F1_OBS_CLOSE',{'kind':'raw'},{'buffer_pending':1})),
        ('legacy_not_drained',lambda:alter('CYD_F1_OBS_CLOSE',{'kind':'simple'},{'drained':0})),
        ('source_full_case_hash_changed',lambda:alter(case,{'fixture':'active8_120','id':'T0'},{'sha256':'0'*64})),
        ('final_mono_hash_changed',lambda:alter(render,{'fixture':'active8_120'},{'sha256':'0'*64})),
        ('final_chain_mono_hash_changed',lambda:alter('CYD_F1_RENDER_CASE',{'fixture':'LAYOUT_GAIN_CHAIN'},{'sha256':'0'*64})),
        ('decoder_owner_leak',lambda:alter(end,{}, {'closes':194})),
        ('HTTP_owner_leak',lambda:alter(end,{}, {'http_cleanup':57})),
        ('PDM_owner_leak',lambda:alter(end,{}, {'driver_deleted':0})),
        ('ordered_packet_stamp_missing',lambda:alter('CYD_F1_ORDERED_PACKET_CENSUS',{}, {'layout_stamps':0})),
        ('impossible_internal_heap',lambda:alter('CYD_F1_MEMORY',{}, {'largest_internal':0})),
        ('unsupported_numeric_conformance_claim',lambda:alter(end,{}, {'independent_codec_conformance':1})),
        ('progress_deadline_reset_enabled',lambda:alter('CYD_F1_REFERENCE_BUDGET',{}, {'reset_on_progress':1})),
        ('ordinary_deadline_weakened',lambda:alter('CYD_F1_REFERENCE_BUDGET',{}, {'ordinary_ms':90000})),
        ('missing_native_fault_snapshot',lambda:alter('CYD_F1_NATIVE_FAULTS',{},remove=True)),
        ('hidden_allocator_callback',lambda:alter('CYD_F1_NATIVE_FAULTS',{}, {'allocation_failures':lambda value:value+1})),
        ('hidden_output_failure_detail',lambda:alter('CYD_F1_NATIVE_FAULTS',{}, {'output_write_errors':1})),
        ('unknown_allocator_callback',lambda:alter('CYD_F1_ALLOC_COMPLETE',{}, {'unknown':1})),
        ('overflowed_allocator_observer',lambda:alter('CYD_F1_ALLOC_COMPLETE',{}, {'overflow':1})),
        ('missing_allocator_terminal',lambda:alter('CYD_F1_ALLOC_COMPLETE',{},remove=True)),
    ]
    if measured['allocation_faults']['callbacks']:
        controls += [
            ('original_health_callback_not_forwarded',lambda:alter('CYD_F1_ALLOC_CALLBACK',{}, {'forwarded':0})),
            ('unobserved_realloc_recovery',lambda:alter('CYD_F1_REALLOC_NULL',{},remove=True)),
        ]
    original_control_count=len(controls)
    if successor:need(original_control_count==50,'all50 previous actual-data rejection controls retained')
    first_pause=measured['cancellation']['pause_starts'][0]['pause']
    controller_handle=measured['cancellation']['public_owner_provenance'][0]['task_handle']
    def paired_pause(changes):
        text=alter('CYD_F1_CONTROL_PAUSE_START',{'pause':first_pause},changes)
        return alter('CYD_F1_CONTROL_PAUSE_RETURN',{'pause':first_pause},changes,text=text)
    controls += [
        ('missing_actual_owner_provenance',lambda:alter('CYD_F1_CONTROL_OWNER',{'role':'output'},remove=True)),
        ('duplicate_actual_owner_handle',lambda:alter('CYD_F1_CONTROL_OWNER',{'role':'output'},{'task_handle':controller_handle})),
        ('changed_declared_creation_priority',lambda:alter('CYD_F1_CONTROL_OWNER',{'role':'decode'},{'declared_priority':6})),
        ('false_live_base_priority_query',lambda:alter('CYD_F1_CONTROL_OWNER',{}, {'live_base_query':1})),
        ('changed_registered_owner_core',lambda:alter('CYD_F1_CONTROL_OWNER',{'role':'output'},{'core':0})),
        ('pause_wrong_stable_owner_role',lambda:paired_pause({'owner_role':'stream'})),
        ('pause_unknown_stable_task_handle',lambda:paired_pause({'task_handle':0})),
        ('pause_wrong_declared_priority',lambda:paired_pause({'declared_priority':3})),
        ('pause_wrong_stable_provenance',lambda:paired_pause({'priority_provenance':'live_base_query'})),
        ('pause_wrong_stable_caller_core',lambda:paired_pause({'core':1})),
        ('effective_priority_below_declared',lambda:paired_pause({'priority':0})),
        ('effective_priority_outside_scheduler',lambda:paired_pause({'priority':25})),
        ('effective_priority_non_numeric',lambda:paired_pause({'priority':'controller'})),
        ('pause_return_changes_actual_identity',lambda:alter('CYD_F1_CONTROL_PAUSE_RETURN',{'pause':first_pause},{'task_handle':0})),
    ]
    rejected=[]
    for name,make in controls:
        try:evaluate(make())
        except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('contradictory original-data copy accepted: '+name)
    need(all(sha(path)==digest for path,digest in originals.items()),'all original native/source/post-oracle evidence unchanged')
    native_inputs(native,report,sources,allow_reader_metadata=bool(successor))
    out.mkdir(parents=True)
    for path,name in [(Path(__file__).resolve(),'controller.py'),(READER,'reader.py'),(OUTPUT,'independent-output-oracle.py'),
                      (FAULT_READER,FAULT_READER.name),(WORD_READER,WORD_READER.name)]: (out/name).write_bytes(path.read_bytes())
    value=dict(passed=True,original_transcript_accepted=True,original_post_oracle_accepted=True,rejected_controls=len(rejected),rejected=rejected,
        original_bindings=originals,reader_sha256=sha(READER),originals_modified=False,native_campaign_repeated=False,
        Decimal_computation_repeated=False,independent_codec_conformance=False,original_negative_controls_retained=original_control_count,
        new_owner_negative_controls=len(controls)-original_control_count,original_native_passed=report['passed'],
        explicit_data_successor=successor.relative_to(ROOT).as_posix() if successor else None,
        original_status_preserved='NONPASS' if successor else 'PASS')
    (out/'report.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,rejected_controls=len(rejected),native_campaign_repeated=False)));return 0


if __name__=='__main__':raise SystemExit(main())
