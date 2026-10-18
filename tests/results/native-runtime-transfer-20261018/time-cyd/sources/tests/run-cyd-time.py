"""Run actual CYD time settings/service with pthread RTOS, NVS and SNTP seams.

The production worker, explicit record codec, validation and snapshots execute
unchanged. Fake wall/monotonic clocks and controlled worker notifications make
offline/failure/concurrent publication cases deterministic. This does not
qualify physical NVS, network timing, or the target's 2048-byte worker stack.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host
def stripped(path):return re.sub(r'^\s*#\s*include[^\n]*\n','',path.read_text(),flags=re.M)
def execute(cmd,timeout=30):
    r=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout);return r.returncode,r.stdout
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/esp32-cyd2usb-native/main';shared=ROOT/'idf/components/native_time';test=ROOT/'tests/native/cyd_time_test.c'
    files=[Path(__file__).resolve(),test,ROOT/'tests/native/cyd_time_platform.h',ROOT/'tests/native/native_time_platform.h',shared/'include/native_time_sntp.h',*[main/n for n in ('time_settings.c','time_settings.h','time_service.c','time_service.h')]]
    (out/'headers.inc').write_text(stripped(shared/'include/native_time_sntp.h')+stripped(main/'time_settings.h')+stripped(main/'time_service.h'))
    settings=stripped(main/'time_settings.c');service=stripped(main/'time_service.c');(out/'settings.inc').write_text(settings);(out/'service.inc').write_text(service)
    command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-fno-pie','-no-pie','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+host(out),'-I'+host(ROOT/'tests/native'),host(test),'-o',host(out/'time')]
    def build(suffix=''):
        cmd=command.copy();cmd[-1]+=suffix;code,log=execute(cmd,60);(out/('build'+suffix+'.log')).write_bytes(log)
        if code:raise RuntimeError(log.decode(errors='replace'))
        return Path(str(out/'time')+suffix)
    binary=build();cases=['defaults','validation','record_roundtrip','invalid_record','read_errors','wrong_type','save_errors','settings_oom','concurrent_save','offline','first_ip','flaps','apply_failure','offline_save','save_during_apply','sync_clock','timezone_overflow','snapshot_timeout','task_oom','start_mutex_oom','state_mutex_oom','backend_init_failure','sync_lock_retry','saved_apply_failure']
    report={'passed':False,'scope':__doc__,'physical_hardware':False,'cases':{},'negative_controls':{},'command':command,'source_sha256':{}}
    for case in cases:
        code,log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case]);(out/(case+'.log')).write_bytes(log)
        if code:raise RuntimeError(case+': '+log.decode(errors='replace'))
        report['cases'][case]=log.decode().strip()
    mutations={
        'publish_after_failed_commit':('if (result == ESP_OK) {\n        // Only a bounded RAM copy','if (true) {\n        // Only a bounded RAM copy','settings','save_errors','rev==revision'),
        'missing_network_gate':('if (!atomic_load(&s_network_ready)) continue;','/* negative: offline control */','service','offline','backend_notifies'),
        'duplicate_reconnect':('if (!previous) atomic_fetch_add(&s_connection_epoch, 1U);','(void)previous; atomic_fetch_add(&s_connection_epoch, 1U);','service','first_ip','backend_applies==1&&!backend_restarts'),
        'wall_clock_age':('(monotonic - last_sync_us) / 1000','((int64_t)candidate.utc_epoch - (int64_t)candidate.last_sync_epoch) * 1000','service','sync_clock','s.last_sync_age_ms==2000'),
        'false_applied_revision':('s_applied_revision = revision;','s_applied_revision = revision + 1U;','service','save_during_apply','s.applied_revision==1&&s.desired_revision==2'),
        'wrong_offset_sign':('int64_t adjusted = utc + offset;','int64_t adjusted = utc - offset;','service','timezone_overflow','s.clock_valid&&s.local_time.tm_year==123'),
        'hidden_record_tail':('if (memcmp(record, canonical, TIME_RECORD_SIZE)) return false;','/* negative: hidden bytes accepted */','settings','invalid_record','!decode_record(record,&result)'),
    }
    for name,(old,new,unit,case,assertion) in mutations.items():
        original=settings if unit=='settings' else service;assert original.count(old)==1,name;(out/(unit+'.inc')).write_text(original.replace(old,new));negative=build('-negative-'+name)
        code,log=execute(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(negative),case]);(out/('negative-'+name+'.log')).write_bytes(log)
        assert code and b'Assertion' in log and assertion.encode() in log,(name,log)
        assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log
        report['negative_controls'][name]={'case':case,'status':code,'expected_assertion':assertion,'rejected':True};(out/(unit+'.inc')).write_text(original)
    for f in files:
        name=f.relative_to(ROOT).as_posix();target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes());report['source_sha256'][name]=hashlib.sha256(f.read_bytes()).hexdigest()
    report['passed']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases),'cases +',len(mutations),'semantic negatives')
if __name__=='__main__':main()
