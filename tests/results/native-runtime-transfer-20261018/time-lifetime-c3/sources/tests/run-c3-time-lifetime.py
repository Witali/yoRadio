"""Reproduce donor SNTP name corruption with actual pinned SDK async wrappers.

Requires the qualified native_time campaign output, reusing its frozen SDK/DNS
translation unit rather than a second implementation. TCPIP/DNS scheduling is
controlled on the host; this does not qualify target scheduling or networking.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--backend-evidence',type=Path,default=ROOT/'.build/native-time-qualified-01')
    p.add_argument('--historical-ref',default='642ee17f')
    p.add_argument('--sdk',type=Path,default=Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6'))
    args=p.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    evidence=args.backend_evidence.resolve();qualified=json.loads((evidence/'report.json').read_text());assert qualified['passed']
    main=ROOT/'idf/esp32c3-oled-native/main';component=ROOT/'idf/components/native_time';test=ROOT/'tests/native';sdk=args.sdk.resolve()
    frozen=evidence/sdk.name
    pinned=(frozen/'pinned.inc').read_text();backend=(frozen/'backend.inc').read_text()
    spec=importlib.util.spec_from_file_location('native_time_helpers',ROOT/'tests/run-native-time.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
    core=sdk/'components/lwip/lwip/src/apps/sntp/sntp.c';dns=sdk/'components/lwip/lwip/src/core/dns.c';extension=sdk/'components/lwip/apps/sntp/sntp.c'
    managed=sdk/'components/esp_netif/lwip/esp_netif_sntp.c'
    assert helpers.stripped(component/'native_time_sntp_internal.h')+helpers.stripped(component/'native_time_sntp.c')+helpers.stripped(component/'native_time_sntp_context.c')==backend
    assert helpers.stripped(core) in pinned
    managed_body=helpers.stripped(managed).replace('#undef SNTP_OPMODE_POLL','#undef SNTP_OPMODE_POLL\n#define SNTP_OPMODE_POLL 0')
    assert managed_body in pinned
    assert helpers.function(dns.read_text(),'dns_enqueue') in pinned
    ext=helpers.stripped(extension);raw=ext[ext.index('static void do_setoperatingmode'):]
    old=subprocess.check_output(['git','show',args.historical_ref+':'+(main/'time_service.c').relative_to(ROOT).as_posix()],cwd=ROOT)
    assert b'if (esp_sntp_enabled()) esp_sntp_stop();' in old
    (out/'historical-source.c').write_bytes(old)
    platform=(test/'native_time_platform.h').read_text()
    old_async='static int tcpip_callback(void(*fn)(void*),void *ctx){(void)fn;(void)ctx;assert(!"asynchronous SNTP API used");return -1;}'
    assert platform.count(old_async)==1
    platform=platform.replace(old_async,'static int tcpip_callback(void(*fn)(void*),void *ctx);')
    old_ipc='static esp_err_t esp_netif_tcpip_exec(esp_err_t(*fn)(void*),void *ctx){ipc_calls++;if(ipc_calls==fail_ipc_at)return ESP_FAIL;assert(!in_tcpip);assert(!pthread_mutex_lock(&tcpip_lock));in_tcpip=true;esp_err_t e=fn(ctx);in_tcpip=false;assert(!pthread_mutex_unlock(&tcpip_lock));return e;}'
    assert platform.count(old_ipc)==1
    platform=platform.replace(old_ipc,'static esp_err_t esp_netif_tcpip_exec(esp_err_t(*fn)(void*),void *ctx);')
    dns_call='(void)address;assert(in_tcpip);return dns_enqueue(name,strlen(name),callback,context);'
    assert pinned.count(dns_call)==1
    pinned=pinned.replace(dns_call,'(void)address;assert(in_tcpip);host_dns_pause(name);return dns_enqueue(name,strlen(name),callback,context);')
    for name,body in [('platform.inc',platform),('pinned.inc',pinned),('backend.inc',backend),('raw-wrappers.inc',raw)]: (out/name).write_text(body)
    (out/'esp_err.h').write_text('#pragma once\n')
    files=[Path(__file__).resolve(),test/'c3_time_lifetime_test.c',test/'native_time_platform.h',ROOT/'tests/run-native-time.py',
           *[main/n for n in ('time_service.c','time_service.h','runtime_settings.h')],
           *[component/n for n in ('native_time_sntp.c','native_time_sntp_context.c','native_time_sntp_internal.h','include/native_time_sntp.h')]]
    hashes={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    report=dict(passed=False,scope=__doc__,physical_hardware=False,historical_ref=args.historical_ref,historical_git_blob_sha256=hashlib.sha256(old).hexdigest(),source_sha256=hashes,sdk_sha256={},variants={},foundation_report_sha256=hashlib.sha256((evidence/'report.json').read_bytes()).hexdigest())
    (out/'foundation-report.json').write_bytes((evidence/'report.json').read_bytes())
    for f in files:
        dest=out/'sources'/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes())
    sdk_files=[core,dns,extension,managed,sdk/'components/lwip/lwip/src/include/lwip/apps/sntp.h',sdk/'components/lwip/lwip/src/include/lwip/apps/sntp_opts.h',sdk/'components/lwip/include/apps/esp_sntp.h',sdk/'components/esp_netif/include/esp_netif_sntp.h',sdk/'components/lwip/port/esp32xx/include/arch/cc.h']
    for f in sdk_files:
        key=f.relative_to(sdk).as_posix();sha=hashlib.sha256(f.read_bytes()).hexdigest()
        assert qualified['source_sha256']['sdk/'+sdk.name+'/'+key]==sha
        dest=out/'sdk-sources'/key;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes());report['sdk_sha256'][key]=sha
    for mode,text in [('current',(main/'time_service.c').read_text()),('historical',old.decode())]:
        (out/'donor.inc').write_text(re.sub(r'^#include[^\n]*\n','',text,flags=re.M));binary=out/mode
        cmd=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-Wno-sign-compare','-pthread','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
             '-I'+host(out),'-I'+host(main),host(test/'c3_time_lifetime_test.c'),'-o',host(binary)]
        if mode=='historical':cmd.insert(1,'-DOLD_SOURCE=1')
        try:(out/(mode+'-build.log')).write_bytes(run(cmd))
        except subprocess.CalledProcessError as e:(out/(mode+'-build.log')).write_bytes(e.output);print(e.output.decode(errors='replace'));raise
        try:log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)]);code=0
        except subprocess.CalledProcessError as e:log=e.output;code=e.returncode
        (out/(mode+'.log')).write_bytes(log);print(log.decode(errors='replace'),end='')
        assert code==(1 if mode=='historical' else 0),(mode,code)
        assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log
        if mode=='historical':assert b'NEGATIVE_CONTROL_FAIL: actual historical C3 apply overwrote borrowed DNS name before queued SDK stop ACK' in log
        report['variants'][mode]=dict(status=code,semantic_negative=mode=='historical',output=log.decode().strip(),command=cmd)
    report['generated_unit_sha256']={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ('platform.inc','pinned.inc','backend.inc','raw-wrappers.inc')}
    report['source_files_still_match_snapshot']=all(hashlib.sha256(f.read_bytes()).hexdigest()==hashes[f.relative_to(ROOT).as_posix()] for f in files)
    assert report['source_files_still_match_snapshot'];report['passed']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
