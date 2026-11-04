"""HOST sanitizer/public-forwarding checks and contradictory data controls.

All callback/refusal schedules and numeric addresses here are explicit HOST
doubles. No native OOM, SDK, decoder, QEMU or whole-task PASS is manufactured.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
MAIN=ROOT/'tests/target/cyd_family1_playback_task_qemu/project/main'
PRODUCTION=ROOT/'idf/esp32-cyd2usb-native/main'


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def linux(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def local(value):
    if sys.platform=='win32' and re.match('/mnt/[a-z]/',value):return Path(value[5].upper()+':/'+value[7:])
    return Path(value)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    out=parser.parse_args().output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local HOST evidence')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'stubs/soc').mkdir(parents=True)
    report=dict(passed=False,HOST_only=True,SDK_started=False,QEMU_started=False,actual_Xtensa_started=False,
        native_heap=False,native_OOM_injection_qualified=False,whole_task_transcript_qualified=False,
        callback_schedules_are_HOST_doubles=True,sources=[],commands=[])
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def run(name,argv,success=True):
        argv=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,argv))
        started=time.monotonic();p=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        command=dict(name=name,argv=argv,pid=p.pid,state='running');report['commands'].append(command);save()
        try:stdout,stderr=p.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            p.kill();stdout,stderr=p.communicate(timeout=15);command['timed_out']=True
        for label,body in [('stdout',stdout),('stderr',stderr)]:
            (out/(name+'.'+label+'.log')).write_bytes(body)
            command[label]=dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
        command.update(state='complete',exit_status=p.returncode,seconds=time.monotonic()-started);save()
        need(not command.get('timed_out') and (p.returncode==0 if success else p.returncode!=0),
             'authoritative HOST terminal status: '+name)
        need(not re.search(rb'AddressSanitizer|runtime error:|UndefinedBehaviorSanitizer',stderr),'no sanitizer violation: '+name)
        return stdout.decode('utf-8'),stderr.decode('utf-8')
    save()
    try:
        sources=[(MAIN/'allocation_fault_observer.inc','allocation_fault_observer.inc'),
            (MAIN/'word_alloc_observer.inc','word_alloc_observer.inc'),
            (ROOT/'tests/native/cyd_family1_allocation_fault_host.cpp','host.cpp'),
            (ROOT/'tests/read-cyd-family1-allocation-faults.py','read-cyd-family1-allocation-faults.py'),
            (ROOT/'tests/read-cyd-family1-word-alloc.py','read-cyd-family1-word-alloc.py'),
            (ROOT/'tests/read-cyd-family1-task-log.py','read-cyd-family1-task-log.py'),
            (PRODUCTION/'native_health.h','native_health.h'),(PRODUCTION/'native_output_metrics.h','native_output_metrics.h'),
            (Path(__file__).resolve(),'controller.py')]
        for path,name in sources:
            target=out/'sources'/name;target.write_bytes(path.read_bytes())
            report['sources'].append(dict(path=str(path),snapshot=target.relative_to(out).as_posix(),sha256=sha(path),bytes=path.stat().st_size))
        sdk=ROOT.parents[1]/'.idf/v6.0.2'
        contracts=['components/heap/heap_caps.c','components/heap/heap_caps_base.c',
            'components/heap/include/esp_heap_caps.h','components/esp_libc/src/heap.c',
            'components/freertos/esp_additions/include/freertos/idf_additions.h',
            'components/esp_hw_support/include/esp_cpu.h']
        for relative in contracts:
            path=sdk/relative;target=out/'sources/SDK-contract'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
            report['sources'].append(dict(path=str(path),snapshot=target.relative_to(out).as_posix(),sha256=sha(path),bytes=path.stat().st_size,contract_only_not_HOST_compiled=True))
        config=ROOT/'.build/cyd-family1-playback-task-20261103-03/sdkconfig';text=config.read_text()
        need('# CONFIG_SPIRAM is not set' in text and '# CONFIG_HEAP_ABORT_WHEN_ALLOCATION_FAILS is not set' in text and
             'CONFIG_ESP_TASK_WDT_TIMEOUT_S=20' in text and 'CONFIG_ESP_TASK_WDT_PANIC=y' in text and
             'CONFIG_ESP_INT_WDT_TIMEOUT_MS=1000' in text,'exact unchanged finite native03 diagnostic configuration')
        target=out/'sources/native03-sdkconfig';target.write_bytes(config.read_bytes())
        report['sources'].append(dict(path=str(config),snapshot=target.relative_to(out).as_posix(),sha256=sha(config),bytes=config.stat().st_size,contract_only_not_HOST_compiled=True))
        report['primary_SDK_callback_contract']=dict(pinned_SDK_commit='7101770dc6db2667b3c477cc31365dd1acd6db4e',
            source_bindings=contracts,configuration_sha256=sha(config),
            actual_source_path='realloc -> heap_caps_realloc_default -> heap_caps_realloc -> heap_caps_realloc_base',
            disabled_external_allocation_branch=True,actual_callback_caps=6144,actual_callback_function='heap_caps_realloc',
            callback_count_per_nonzero_real_NULL=1,
            basis='heap_caps_realloc calls heap_caps_alloc_failed once after its base returns NULL; the base uses heap_caps_aligned_alloc_base,not the public failure-reporting heap_caps_malloc/realloc entry points. heap_caps_alloc_failed synchronously invokes the one registered callback. This is a pinned source/configuration contract,not a function-name inference.')
        for name,body in [('esp_attr.h','#pragma once\n#define IRAM_ATTR\n#define DRAM_ATTR\n'),
            ('esp_memory_utils.h','#pragma once\n'),('esp_cpu.h','#pragma once\n'),('soc/soc.h','#pragma once\n'),
            ('esp_err.h','#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_ERR_INVALID_ARG 0x102\n')]:
            (out/'stubs'/name).write_text(body,encoding='utf-8',newline='\n')
        run('compiler-version',['g++','--version']);compiler=run('compiler-path',['which','g++'])[0].strip()
        run('compiler-sha',['sha256sum',compiler])
        binary=out/'allocation-fault-host'
        run('build',['timeout','--kill-after=5','60','g++','-std=c++17','-O2','-g','-pthread','-Wall','-Wextra','-Werror',
            '-fno-pie','-no-pie','-fno-omit-frame-pointer','-fsanitize=address,undefined','-MMD','-MF',linux(out/'host.d'),
            '-I'+linux(out/'stubs'),'-I'+linux(out/'sources'),linux(out/'sources/host.cpp'),'-o',linux(binary)])
        dependency_text=(out/'host.d').read_text().replace('\\\n',' ')
        deps=[local(value) for value in shlex.split(dependency_text.split(':',1)[1])]
        report['actual_HOST_dependencies']=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in deps]
        run_args=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','--kill-after=5','60',linux(binary)]
        transcripts={}
        for mode in ('zero','recovered','recovered_initial','opaque'):
            transcripts[mode]=run('test-'+mode,[*run_args,mode])[0]
        for mode in ('unknown','overflow','unpublished'):
            text,error=run('test-'+mode,[*run_args,mode],success=False)
            need('all_real_allocator_callbacks_attributed_and_forwarded' in error and 'CYD_F1_ALLOC_COMPLETE ' in text,
                 'unknown/overflow refusal is the intended observer assertion,after complete retained counters')
            transcripts[mode]=text
        read=module('frozen_primary_public_fields',out/'sources/read-cyd-family1-task-log.py')
        faults=module('frozen_passive_fault_data',out/'sources/read-cyd-family1-allocation-faults.py')
        word=module('frozen_public_word_data',out/'sources/read-cyd-family1-word-alloc.py')
        contract=dict(entries=[dict(id=0,channels=8,coupled=3,mapping=[0,6,1,2,3,4,5,7],pcm_bytes=15360)],
            cases=[dict(name='fallback',links=[dict(reference=0)])])
        (out/'HOST-contract.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
        def rows(text):return [read.fields(line) for line in text.splitlines() if line.startswith('CYD_F1_')]
        def encode(records):return '\n'.join(tag+' '+' '.join(k+'='+str(v) for k,v in row.items()) for tag,row in records)+'\n'
        def evaluate(text):
            parsed=faults.validate_allocation_faults(rows(text),contract);word.parse_word_allocation_log(text);return parsed
        positive={mode:evaluate(transcripts[mode]) for mode in ('zero','recovered','recovered_initial')}
        need(len(positive['zero']['callbacks'])==0 and len(positive['recovered']['callbacks'])==len(positive['recovered_initial']['callbacks'])==1,
             'explicit synthetic zero-event,real-return failure and initial NULL vectors')
        need(positive['recovered']['actual_null_returns'][0]['old_pointer']>0 and positive['recovered_initial']['actual_null_returns'][0]['old_pointer']==0,
             'actual original pointer forwarded on both initial and growth-shaped calls')
        need('opaque_dereferenced=0' in transcripts['opaque'],'ISR callback opaque function pointer is never inspected')
        base=rows(transcripts['recovered']);rejected=[]
        def reject(name,text):
            try:evaluate(text)
            except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
            else:raise ValueError('contradictory passive-allocation trace accepted: '+name)
        def changed(tag,updates,index=0):
            values=copy.deepcopy(base);at=[i for i,(found,_) in enumerate(values) if found==tag][index]
            values[at][1].update(updates);return encode(values)
        controls=[
            ('health_count_hidden','CYD_F1_NATIVE_FAULTS',{'allocation_failures':0}),
            ('last_health_size_changed','CYD_F1_NATIVE_FAULTS',{'allocation_size':1}),
            ('last_health_caps_changed','CYD_F1_NATIVE_FAULTS',{'allocation_caps':4}),
            ('decoder_failure_hidden','CYD_F1_NATIVE_FAULTS',{'decoder_failures':1}),
            ('stream_failure_hidden','CYD_F1_NATIVE_FAULTS',{'stream_result':-1}),
            ('output_failure_detail_hidden','CYD_F1_NATIVE_FAULTS',{'output_write_errors':1}),
            ('callback_not_forwarded','CYD_F1_ALLOC_CALLBACK',{'forwarded':0}),
            ('callback_wrong_function','CYD_F1_ALLOC_CALLBACK',{'function':'heap_caps_malloc'}),
            ('callback_wrong_caps','CYD_F1_ALLOC_CALLBACK',{'caps':2050}),
            ('callback_wrong_size','CYD_F1_ALLOC_CALLBACK',{'bytes':15364}),
            ('callback_wrong_attempt','CYD_F1_ALLOC_CALLBACK',{'attempt':2}),
            ('callback_wrong_generation','CYD_F1_ALLOC_CALLBACK',{'generation':2}),
            ('foreign_callback','CYD_F1_ALLOC_CALLBACK',{'decoder_owner':0}),
            ('ISR_callback','CYD_F1_ALLOC_CALLBACK',{'isr':1}),
            ('callback_wrong_core','CYD_F1_ALLOC_CALLBACK',{'core':0}),
            ('callback_SP_below_decoder_stack','CYD_F1_ALLOC_CALLBACK',{'stack_pointer':0x3ffafffc}),
            ('callback_SP_at_high_bound','CYD_F1_ALLOC_CALLBACK',{'stack_pointer':0x3ffb4000}),
            ('callback_sequence_gap','CYD_F1_ALLOC_CALLBACK',{'sequence':2}),
            ('unknown_callback','CYD_F1_ALLOC_COMPLETE',{'unknown':1}),
            ('callback_overflow','CYD_F1_ALLOC_COMPLETE',{'overflow':1}),
            ('extra_registration','CYD_F1_ALLOC_COMPLETE',{'registrations':2}),
            ('registration_failure','CYD_F1_ALLOC_COMPLETE',{'registration_errors':1}),
            ('inflight_call_at_terminal','CYD_F1_ALLOC_COMPLETE',{'inflight':1}),
            ('lost_real_realloc_return','CYD_F1_ALLOC_COMPLETE',{'realloc_returns':0}),
            ('hidden_original_callback','CYD_F1_ALLOC_COMPLETE',{'forwarded':0}),
            ('observer_DRAM_exceeds_bound','CYD_F1_ALLOC_COMPLETE',{'observer_static_bytes':1025}),
            ('invented_callback_capacity','CYD_F1_ALLOC_COMPLETE',{'callback_capacity':99}),
            ('no_final_maintenance','CYD_F1_ALLOC_COMPLETE',{'final_maintenance':0}),
            ('added_diagnostic_delay','CYD_F1_ALLOC_COMPLETE',{'diagnostic_delays':1}),
            ('private_heap_claim','CYD_F1_ALLOC_COMPLETE',{'private_heap':1}),
            ('hardware_claim','CYD_F1_ALLOC_COMPLETE',{'hardware':1}),
            ('wrong_decoder_stack_size','CYD_F1_ALLOC_OWNER',{'stack_bytes':16380}),
            ('overflowing_stack_bound','CYD_F1_ALLOC_OWNER',{'stack_high':2**32}),
            ('overlapping_public_task_stacks','CYD_F1_ALLOC_OWNER',{'stream_stack_low':0x3ffb0000,'stream_stack_high':0x3ffb1800}),
            ('unpublished_stack','CYD_F1_ALLOC_OWNER',{'stack_low':0}),
            ('callback_calls_Flash_task_getter','CYD_F1_ALLOC_OWNER',{'callback_task_lookup':1}),
            ('private_stack_memory_read','CYD_F1_ALLOC_OWNER',{'stack_dereferenced':1}),
            ('missing_synchronous_callback','CYD_F1_REALLOC_NULL',{'callback_count':0}),
            ('wrong_callback_identity','CYD_F1_REALLOC_NULL',{'callback_first':2}),
            ('NULL_was_not_returned','CYD_F1_REALLOC_NULL',{'real_returned':0}),
            ('invented_success_pointer','CYD_F1_REALLOC_NULL',{'returned_pointer':123}),
            ('oversized_small_request','CYD_F1_REALLOC_NULL',{'bytes':23056}),
            ('fractional_channel_plane','CYD_F1_REALLOC_NULL',{'bytes':15361}),
            ('wrong_logical_reference','CYD_F1_REALLOC_NULL',{'reference':1}),
            ('wrong_logical_link','CYD_F1_REALLOC_NULL',{'link':1}),
            ('wrong_NULL_generation','CYD_F1_REALLOC_NULL',{'generation':2}),
            ('wrong_NULL_owner','CYD_F1_REALLOC_NULL',{'priority':6}),
            ('foreign_public_open_generation','CYD_F1_OBS_OPEN',{'generation':2}),
            ('wrong_complete_PCM_extent','CYD_F1_LINK',{'bytes':15358}),
            ('wrong_complete_PCM_reference','CYD_F1_LINK',{'reference':1}),
        ]
        for name,tag,changes in controls:reject(name,changed(tag,changes))
        for tag in ['CYD_F1_REALLOC_NULL','CYD_F1_ALLOC_CALLBACK','CYD_F1_NATIVE_FAULTS','CYD_F1_ALLOC_COMPLETE','CYD_F1_WORD_COMPLETE','CYD_F1_LINK','CYD_F1_ALLOC_OWNER']:
            reject('missing_'+tag,encode([(found,row) for found,row in base if found!=tag]))
        lost=copy.deepcopy(base);lost=[(tag,row) for tag,row in lost if not(tag=='CYD_F1_WORD_HEAP' and row['allocation']==8 and row['operation']=='ALLOC')]
        reject('partial_candidate_group',encode(lost))
        reject('one_stream_never_resumed',encode([(tag,row) for tag,row in base if not(tag=='CYD_F1_OBS_CALL' and row['stream']==4)]))
        values=copy.deepcopy(base);at=next(i for i,(tag,_) in enumerate(values) if tag=='CYD_F1_LINK');values.insert(at,('CYD_F1_CONTROL_HTTP_OPEN',dict(generation=2)))
        reject('whole_PCM_belongs_to_later_generation',encode(values))
        values=copy.deepcopy(base);at=next(i for i,(tag,row) in enumerate(values) if tag=='CYD_F1_WORD_HEAP' and row['operation']=='FREE' and row['stage']=='AFTER');values[at][1]['pointer']+=4
        reject('free_does_not_match_actual_pointer',encode(values))
        values=copy.deepcopy(base);owner=next(i for i,(tag,_) in enumerate(values) if tag=='CYD_F1_ALLOC_OWNER');item=values.pop(owner);at=next(i for i,(tag,_) in enumerate(values) if tag=='CYD_F1_REALLOC_NULL');values.insert(at+1,item)
        reject('owner_publication_after_failed_return',encode(values))
        for mode in ('unknown','overflow','unpublished'):reject('actual_HOST_observer_rejects_'+mode,transcripts[mode])
        zero=rows(transcripts['zero']);at=next(i for i,(tag,_) in enumerate(zero) if tag=='CYD_F1_NATIVE_FAULTS');zero[at][1]['allocation_size']=123
        reject('zero_event_health_detail_is_not_zero',encode(zero))
        need(all(sha(pin['path'])==pin['sha256']==sha(out/pin['snapshot']) for pin in report['sources']),'all actual HOST/source snapshots remain current')
        report.update(passed=True,positive_vectors=positive,opaque_callback_pointer_test=True,unknown_and_overflow_fail_closed=True,
            rejected_controls=rejected,all_source_bindings_current=True,HOST_observer_static_bytes=positive['zero']['terminal']['observer_static_bytes'],
            target_static_bytes_unmeasured=True,native03_status='NONPASS;not reclassified;no missing records synthesized',
            unchanged_native_profile=dict(task_watchdog_seconds=20,task_watchdog_panic=True,interrupt_watchdog_ms=1000,
                ordinary_entry_seconds=30,reference_entry_seconds=90,QEMU_seconds=600,SDK_seconds=1200))
    finally:save()
    print(json.dumps(dict(passed=report['passed'],HOST_only=True,positive_vectors=3,rejected_controls=len(report['rejected_controls']),
        HOST_observer_static_bytes=report['HOST_observer_static_bytes'],SDK_started=False,QEMU_started=False)))


if __name__=='__main__':main()
