"""HOST-only qualification of allocator forwarding and contradictory trace data.

The actual observer is compiled against explicit HOST public-API seams. Numeric
ESP32 addresses are never accessed. Refusal/growth vectors are synthetic public
call schedules, not native allocation failures or production replacement tests.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OBSERVER=ROOT/'tests/target/cyd_family1_playback_task_qemu/project/main/word_alloc_observer.inc'
HOST=ROOT/'tests/native/cyd_family1_word_alloc_host.cpp'
READER=ROOT/'tests/read-cyd-family1-word-alloc.py'

def need(value,reason):
    if not value:raise ValueError(reason)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def host_path(path):
    value=path.resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    out=parser.parse_args().output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh HOST capture');out.mkdir(parents=True);(out/'sources').mkdir();(out/'stubs/soc').mkdir(parents=True)
    report=dict(passed=False,HOST_only=True,SDK_started=False,QEMU_started=False,native_heap=False,native_OOM_injected=False,production_storage_transactions_qualified=False,sources=[],commands=[])
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def execute(name,argv):
        command=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+argv
        start=time.monotonic();p=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        row=dict(name=name,argv=command,pid=p.pid,state='running');report['commands'].append(row);save()
        try:stdout,stderr=p.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            p.kill();stdout,stderr=p.communicate(timeout=15);row['timed_out']=True
        for label,body in [('stdout',stdout),('stderr',stderr)]:
            path=out/(name+'.'+label+'.log');path.write_bytes(body);row[label]=dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
        row.update(state='complete',exit_status=p.returncode,seconds=time.monotonic()-start);save()
        need(p.returncode==0 and not row.get('timed_out'),'authoritative HOST command failed: '+name);return stdout.decode()
    save()
    try:
        for source,name in [(OBSERVER,'word_alloc_observer.inc'),(HOST,'host.cpp'),(READER,'reader.py'),(Path(__file__).resolve(),'controller.py')]:
            target=out/'sources'/name;target.write_bytes(source.read_bytes());report['sources'].append(dict(path=str(source),snapshot=target.relative_to(out).as_posix(),sha256=sha(source),bytes=source.stat().st_size))
        # The HOST TU explicitly supplies all public API seams. No installed
        # SDK header or IRAM/cache behavior is substituted as native evidence.
        for name,body in [('esp_attr.h','#pragma once\n#define IRAM_ATTR\n'),('esp_memory_utils.h','#pragma once\n'),('soc/soc.h','#pragma once\n')]:
            (out/'stubs'/name).write_text(body,encoding='utf-8')
        execute('compiler-version',['g++','--version']);compiler=execute('compiler-path',['which','g++']).strip();execute('compiler-sha',['sha256sum',compiler])
        binary=out/'word-observer-host'
        execute('build',['timeout','--kill-after=5','60','g++','-std=c++17','-O2','-g','-pthread','-Wall','-Wextra','-Werror','-fno-pie','-no-pie','-fno-omit-frame-pointer','-fsanitize=address,undefined','-I'+host_path(out/'stubs'),'-I'+host_path(out/'sources'),host_path(out/'sources/host.cpp'),'-o',host_path(binary)])
        transcript=execute('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','--kill-after=5','60',host_path(binary)])
        match=re.search(r'^HOST_WORD_RESULT groups=(\d+) attempts=(\d+) successes=(\d+) refusals=(\d+) frees=(\d+) foreign_calls=(\d+) hardware=0 native_heap=0$',transcript,re.M)
        need(match and tuple(map(int,match.groups()[:5]))==(7,55,52,3,52) and int(match[6])>0,'complete public forwarding/ownership/refusal HOST vectors')
        spec=importlib.util.spec_from_file_location('frozen_word_reader',out/'sources/reader.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        value=reader.parse_word_allocation_log(transcript);need(value['completed'] and value['counts']['peak_planes']==16,'all old-plus-candidate and terminal pointer identities')
        rows=[reader.record(line) for line in transcript.splitlines() if line.startswith('CYD_F1_WORD_')]
        first=next(i for i,(tag,row) in enumerate(rows) if tag=='CYD_F1_WORD_HEAP' and row['stage']=='BEFORE')
        allocated=next(i for i,(tag,row) in enumerate(rows) if tag=='CYD_F1_WORD_HEAP' and row['operation']=='ALLOC' and row['stage']=='AFTER' and row['pointer'])
        free=next(i for i,(tag,row) in enumerate(rows) if tag=='CYD_F1_WORD_HEAP' and row['operation']=='FREE' and row['stage']=='BEFORE')
        refused=next(i for i,(tag,row) in enumerate(rows) if tag=='CYD_F1_WORD_HEAP' and row['operation']=='ALLOC' and row['stage']=='AFTER' and not row['pointer'])
        alias=next(i for i,(tag,row) in enumerate(rows) if tag=='CYD_F1_WORD_HEAP' and row['pointer']==0x400bc000 and row['stage']=='AFTER' and row['operation']=='ALLOC')
        def text(changed):return '\n'.join(tag+' '+ ' '.join(key+'='+str(value) for key,value in row.items()) for tag,row in changed)+'\n'
        partial=reader.parse_word_allocation_log(text(rows[:-1]),require_terminal=False)
        need(not partial['completed'] and partial['terminal'] is None,'partial traces never claim terminal qualification')
        need(rows[alias][1]['executable']==0 and rows[alias][1]['diram_iram']==1 and rows[first][1]['largest8']>rows[first][1]['free8'],
             'positive upper-alias SDK predicate and non-atomic heap samples preserved')
        controls=[
            ('wrong_owner_core',first,{'core':0}),('wrong_owner_priority',first,{'priority':6}),
            ('unreturned_free',free+1,{'real_returned':0}),('before_claims_return',first,{'real_returned':1}),
            ('counter_false_success',refused,{'successes':rows[refused][1]['successes']+1}),
            ('lost_refusal',-1,{'refusals':2}),('terminal_live_plane',-1,{'live_planes':1}),
            ('terminal_live_bytes',-1,{'live_bytes':4}),('terminal_inflight',-1,{'inflight':1}),
            ('invented_application_fit',-1,{'application_memory_qualified':1}),('lost_atomic_counters',-1,{'atomic_counters':0}),
            ('missing_final_maintenance',-1,{'final_maintenance':0}),('added_diagnostic_delay',-1,{'diagnostic_delays':1}),
            ('wrong_request_caps',first,{'caps':2054}),('oversized_plane',first,{'bytes':11524}),
            ('halfword_allocation',first,{'bytes':2}),('unaligned_pointer',allocated,{'pointer':rows[allocated][1]['pointer']+1}),
            ('wrong_free_pointer',free,{'pointer':rows[free][1]['pointer']+4}),
            ('wrong_free_generation',free,{'generation':rows[free][1]['generation']+1}),
            ('wrong_free_allocation',free,{'allocation':999}),('wrong_after_identity',allocated,{'generation':99}),
            ('allocation_counter_gap',allocated,{'attempts':2}),('fake_free_count',free+1,{'frees':2}),
            ('exclusive_heap_claim',first,{'heap_snapshot_atomic':1}),('negative_public_heap',first,{'free8':-1}),
            ('fake_executable_upper_alias',alias,{'executable':1}),('IRAM_mislabelled_byte_accessible',alias,{'byte_accessible':1}),
            ('wrong_shared_alias',alias,{'alias_last_word':rows[alias][1]['alias_last_word']+4}),
            ('alias_dereferenced',alias,{'alias_dereferenced':1}),('wrong_pure_IRAM_class',alias,{'pure_iram':1}),
            ('owner_clock_reversed',allocated,{'time_us':0}),('unexpected_field',first,{'undocumented':1}),
        ]
        rejected=[]
        def reject(name,log):
            try:reader.parse_word_allocation_log(log)
            except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
            else:raise ValueError('Contradictory word trace accepted: '+name)
        for name,index,change in controls:
            changed=copy.deepcopy(rows);changed[index][1].update(change);reject(name,text(changed))
        for name,index in [('missing_real_after',allocated),('missing_terminal',len(rows)-1),('missing_refused_after',refused),('missing_last_free_after',len(rows)-2)]:
            changed=copy.deepcopy(rows);del changed[index];reject(name,text(changed))
        changed=copy.deepcopy(rows);changed.append(copy.deepcopy(rows[-1]));reject('duplicate_terminal',text(changed))
        changed=copy.deepcopy(rows);del changed[first][1]['largest32'];reject('truncated_record',text(changed))
        changed=copy.deepcopy(rows);changed[first]=('CYD_F1_WORD_OTHER',changed[first][1]);reject('unknown_word_record',text(changed))
        reject('duplicate_field',text(rows).replace('operation=ALLOC stage=BEFORE','operation=ALLOC stage=BEFORE caps=2050',1))
        reject('interleaved_record','prefix '+text(rows))
        def replace_pointer(changed,allocation,pointer):
            for tag,row in changed:
                if tag=='CYD_F1_WORD_HEAP' and row['allocation']==allocation and row['pointer']:
                    row['pointer']=pointer;row.update(reader.pointer_class(pointer,row['bytes'])[0])
        changed=copy.deepcopy(rows);replace_pointer(changed,2,rows[allocated][1]['pointer']);reject('duplicate_live_public_pointer',text(changed))
        changed=copy.deepcopy(rows);replace_pointer(changed,1,0x400bc000)
        canonical=reader.pointer_class(0x400bc000,3840)[1][0];replace_pointer(changed,2,canonical);reject('same_physical_RAM_through_two_live_aliases',text(changed))
        need(all(sha(Path(row['path']))==row['sha256'] and sha(out/row['snapshot'])==row['sha256'] for row in report['sources']),'all actual compiled/read sources unchanged')
        report.update(passed=True,all_source_bindings_unchanged=True,groups=7,counts=value['counts'],paired_public_calls=value['paired_public_calls'],foreign_forward_calls=int(match[6]),rejected_controls=len(rejected),rejected=rejected,
            partial_trace_does_not_claim_complete=True,non_atomic_heap_samples_accepted=True,upper_shared_alias_false_executable_flag_accepted=True,
            binary=dict(path=binary.name,bytes=binary.stat().st_size,sha256=sha(binary)))
    except BaseException as error:report['error']=type(error).__name__+': '+str(error);raise
    finally:save()
    print(json.dumps(dict(passed=True,HOST_only=True,groups=7,rejected_controls=report['rejected_controls'],native_heap=False,native_OOM_injected=False)))

if __name__=='__main__':main()
