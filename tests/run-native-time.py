"""Qualify actual native_time plus both pinned SNTP cores/managed functions.

Actual DNS enqueue + entry/request structures are extracted unchanged; DNS
networking/completion, TCPIP executor, RTOS, UDP/pbuf/timers and system clock
are explicit host seams. This is lifetime/protocol evidence, not target RAM.
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

def execute(args,timeout=30):
    result=subprocess.run((['wsl.exe','--exec'] if sys.platform=='win32' else [])+args,
        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
    return result.returncode,result.stdout

def stripped(path):
    return re.sub(r'^\s*#\s*include[^\n]*\n','',path.read_text(),flags=re.M)

def function(text,name):
    match=re.search(r'(?:static )?err_t\s*\n'+name+r'\(',text)
    assert match,name
    start=text.index('{',match.start());level=1;end=start+1
    while level:
        level+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[match.start():end]+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    main=ROOT/'idf/components/native_time';harness=ROOT/'tests/native/native_time_test.c'
    files=[Path(__file__).resolve(),harness,ROOT/'tests/native/native_time_platform.h',main/'native_time_sntp.c',main/'native_time_sntp_context.c',main/'native_time_sntp_internal.h',main/'include/native_time_sntp.h',main/'CMakeLists.txt']
    report={'passed':False,'scope':__doc__,'physical_hardware':False,'variants':{},'negative_controls':{},'source_sha256':{}}
    for pin in ('v6.0.2','v6.1-9a97f6c54ec6'):
        sdk=ROOT.parents[1]/'.idf'/pin
        if not sdk.exists():sdk=Path('C:/Work/yoRadio/.idf')/pin
        lwip=sdk/'components/lwip';netif=sdk/'components/esp_netif'
        selected=[lwip/'lwip/src/apps/sntp/sntp.c',lwip/'lwip/src/core/dns.c',lwip/'lwip/src/include/lwip/apps/sntp.h',lwip/'lwip/src/include/lwip/apps/sntp_opts.h',lwip/'include/apps/esp_sntp.h',lwip/'apps/sntp/sntp.c',netif/'include/esp_netif_sntp.h',netif/'lwip/esp_netif_sntp.c',lwip/'port/esp32xx/include/arch/cc.h']
        pinout=out/pin;pinout.mkdir()
        core,dns,public,opts,esp,extension,managed_header,managed,_=selected
        dns_text=dns.read_text();structures=dns_text[dns_text.index('/* DNS table entry states */'):dns_text.index('#if DNS_LOCAL_HOSTLIST',dns_text.index('/* DNS table entry states */'))]
        dns_source=structures+'\nstatic struct dns_table_entry dns_table[DNS_TABLE_SIZE];\nstatic struct dns_req_entry dns_requests[DNS_MAX_REQUESTS];\nstatic u8_t dns_seqno;\n'+function(dns_text,'dns_enqueue')+'\nstatic void dns_check_entry(u8_t index){dns_table[index].state=DNS_STATE_ASKING;}\nstatic err_t dns_gethostbyname(const char *name,ip_addr_t *address,dns_found_callback callback,void *context){(void)address;assert(in_tcpip);return dns_enqueue(name,strlen(name),callback,context);}\n'
        ext=stripped(extension);ext=ext[:ext.index('static void do_setoperatingmode')];ext=ext.replace('#undef SNTP_OPMODE_POLL','#undef SNTP_OPMODE_POLL\n#define SNTP_OPMODE_POLL 0')
        prefix='#define ESP_LWIP_COMPONENT_BUILD\n'+stripped(opts)+stripped(esp)+'\n#undef SNTP_OPMODE_POLL\n'+stripped(public)+stripped(managed_header)+stripped(main/'include/native_time_sntp.h')
        pinned=prefix+'\n'+dns_source+'\n#define TAG SDK_EXTENSION_TAG\n#define settimeofday host_settimeofday\n#define gettimeofday host_gettimeofday\n#define adjtime host_adjtime\n'+ext+'\n#undef TAG\n#undef settimeofday\n#undef gettimeofday\n#undef adjtime\n'+stripped(core)+'\n#define TAG SDK_MANAGED_TAG\n#define calloc host_calloc\n'+stripped(managed)+'\n#undef calloc\n#undef TAG\n'
        # Each original SDK TU includes the raw header after undefining the
        # compatibility macro. The concatenated host TU restores its constant.
        pinned=pinned.replace('#undef SNTP_OPMODE_POLL','#undef SNTP_OPMODE_POLL\n#define SNTP_OPMODE_POLL 0')
        (pinout/'pinned.inc').write_text(pinned)
        backend=stripped(main/'native_time_sntp_internal.h')+stripped(main/'native_time_sntp.c')+stripped(main/'native_time_sntp_context.c')
        (pinout/'backend.inc').write_text(backend)
        for cap in (1,2):
            command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-Wno-sign-compare','-fno-pie','-no-pie','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DCONFIG_LWIP_SNTP_MAX_SERVERS='+str(cap),'-I'+host(pinout),'-I'+host(ROOT/'tests/native'),'-I'+host(main/'include'),host(harness),'-o',host(pinout/('time-'+str(cap)))]
            def build(extra=(),suffix=''):
                cmd=command.copy();cmd[-1]+=suffix;cmd[1:1]=extra
                code,log=execute(cmd,60);(pinout/('build-'+str(cap)+suffix+'.log')).write_bytes(log)
                if code:raise RuntimeError(log.decode(errors='replace'))
                return Path(str(pinout/('time-'+str(cap)))+suffix)
            binary=build();cases=['foreign_ip_'+str(index) for index in range(cap)]+['readiness','init','mutex_oom','lock_timeout','validation','capacity','immutable','equal_no_restart','late_dns','late_dns_failure','managed_oom','managed_ipc','apply_ipc','foreign_client','concurrent','sync_packet']+(['all_slots','all_bank_refs'] if cap==2 else [])
            results={}
            for case in cases:
                code,log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),case]);(pinout/(str(cap)+'-'+case+'.log')).write_bytes(log)
                if code:raise RuntimeError(case+': '+log.decode(errors='replace'))
                results[case]=log.decode().strip()
            code,log=execute([host(binary),'pcb_oom']);(pinout/(str(cap)+'-sdk-pcb-assert.log')).write_bytes(log)
            assert code and b'Failed to allocate udp pcb for sntp client' in log
            noassert=build(('-DHOST_NO_LWIP_ASSERT=1',),'-noassert')
            for case in ('pcb_oom','failed_restart_dns'):
                code,log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(noassert),case]);(pinout/(str(cap)+'-noassert-'+case+'.log')).write_bytes(log)
                if code:raise RuntimeError(log.decode(errors='replace'))
                results['noassert-'+case]=log.decode().strip()
            report['variants'][pin+'/'+str(cap)]={'cases':results,'sdk_assertion_boundary':True,'command':command}
            if cap==2:
                mutations={
                    'readiness_bypass':('if (!atomic_load(&s_tcpip_ready)) return ESP_ERR_INVALID_STATE;','/* negative: missing ready latch */','readiness','native_time_sntp_apply(&a)==ESP_ERR_INVALID_STATE'),
                    'stale_resolved_slot':('sntp_setserver((uint8_t)index, NULL);','sntp_setservername((uint8_t)index, NULL);','all_slots','sntp_getservername(1)==NULL&&sntp_getserver(1)->addr==0'),
                    'unproven_bank_reuse':('if (bank_referenced(bank)) {','if (false) {','all_bank_refs','native_time_sntp_apply(&c)==ESP_ERR_INVALID_STATE'),
                    'borrowed_caller_name':('sntp_setservername((uint8_t)index, destination->servers[index]);','sntp_setservername((uint8_t)index, config->servers[index]);','immutable','borrowed!=a.servers[0]'),
                    'wrong_interval':('native_time_sntp_context_interval((uint32_t)config->sync_interval_minutes * 60000U);','native_time_sntp_context_interval(3600000U);','sync_packet','hourly'),
                    'backoff_reset':('if (s_bound && sntp_enabled() &&','if (false && s_bound && sntp_enabled() &&','equal_no_restart','udp_created==count&&timer_count()==timers_before'),
                }
                for name,(old,new,case,assertion) in mutations.items():
                    assert old in backend,name
                    (pinout/'backend.inc').write_text(backend.replace(old,new))
                    negative=build((),'-negative-'+name)
                    code,log=execute(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(negative),case]);(pinout/('negative-'+name+'.log')).write_bytes(log)
                    assert code and assertion.encode() in log and b'Assertion' in log,(name,log)
                    assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log
                    report['negative_controls'][pin+'/'+name]={'case':case,'status':code,'expected_assertion':assertion,'rejected':True}
                (pinout/'backend.inc').write_text(backend)
            # Name-only ownership checking was the historical numeric-IP gap.
            # Execute that exact former condition for EVERY configured slot,
            # both capacities and both pinned SDK cores, not just slot zero.
            old='if (sntp_getservername((uint8_t)index) ||\n            !ip_addr_isany(sntp_getserver((uint8_t)index)))'
            new='if (sntp_getservername((uint8_t)index))'
            assert backend.count(old)==1
            (pinout/'backend.inc').write_text(backend.replace(old,new))
            negative=build((),'-negative-foreign-ip')
            for index in range(cap):
                case='foreign_ip_'+str(index)
                code,log=execute(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(negative),case])
                (pinout/('negative-'+str(cap)+'-'+case+'.log')).write_bytes(log)
                assertion='result == ESP_ERR_INVALID_STATE'
                assert code and assertion.encode() in log and b'Assertion' in log,(pin,cap,index,log)
                assert b'result=0 managed=1 enabled=1 foreign_ip_preserved=0' in log
                assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log
                report['negative_controls'][pin+'/'+str(cap)+'/'+case]={'case':case,'status':code,'expected_assertion':assertion,'rejected':True}
            (pinout/'backend.inc').write_text(backend)
        for f in selected:
            name='sdk/'+pin+'/'+f.relative_to(sdk).as_posix();target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes());report['source_sha256'][name]=hashlib.sha256(f.read_bytes()).hexdigest()
    for f in files:
        name=f.relative_to(ROOT).as_posix();target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes());report['source_sha256'][name]=hashlib.sha256(f.read_bytes()).hexdigest()
    report['passed']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',sum(len(v['cases']) for v in report['variants'].values()),'groups')

if __name__=='__main__':main()
