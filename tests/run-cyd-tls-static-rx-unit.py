"""Whole new registry module + exact pinned SDK RX/config lifetime spans.

Host layout/crypto/RTOS/capacity inputs and adaptive metadata remain explicit
seams. Canonical reclaim source is whole. No SDK build/QEMU/hardware/real OOM or
TLS conformance claim. Numeric/pointer userdata is never interpreted by module.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"tests/native/cyd_tls_static_rx"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def host(path):
    text=path.resolve().as_posix();return '/mnt/'+text[0].lower()+text[2:] if sys.platform=='win32' else text
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def replace(data,old,new):
    newline=b'\r\n' if b'\r\n' in data else b'\n';old=old.replace(b'\r\n',b'\n').replace(b'\n',newline);new=new.replace(b'\r\n',b'\n').replace(b'\n',newline)
    assert data.count(old)==1,(old,data.count(old));return data.replace(old,new,1)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sdk',type=Path,required=True);p.add_argument("--output",type=Path,required=True);p.add_argument("--preflight-only",action="store_true");p.add_argument("--prepare-only",action="store_true");a=p.parse_args()
    sdk=a.sdk.resolve();out=a.output.resolve();assert out.is_relative_to(ROOT/".build") and not out.exists()
    contract=load(HERE/"source_contract.py","unit_source_contract")
    if a.preflight_only:print(json.dumps(contract.preflight(ROOT,sdk)));return
    out.mkdir(parents=True)
    report={'passed':False,'scope':__doc__,'inputs':{},'commands':[],'positive_cases':{},'controls':{},'compile_rejections':{},'target_build':False,'qemu':False,'physical_benefit':False}
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    def freeze(path,relative):
        dest=out/'inputs'/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes());report['inputs'][str(path)]={'sha256':sha(path),'snapshot':dest.relative_to(out).as_posix()};return dest
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    def execute(label,command):
        argv=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,command))
        try:r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=60);code,raw=r.returncode,r.stdout
        except subprocess.TimeoutExpired as e:code,raw='timeout',e.output or b''
        (out/(label+'.log')).write_bytes(raw);report['commands'].append({'label':label,'argv':argv,'exit_status':code,'log_sha256':hashlib.sha256(raw).hexdigest()});save()
        return code,raw.decode(errors='replace')
    try:
        candidate=out/'inputs/candidate'
        main=ROOT/'idf/esp32-cyd2usb-native/main'
        freeze(HERE/'source_contract.py',Path('source_contract.py'));contract=load(out/'inputs/source_contract.py','frozen_unit_source_contract')
        report['module_contract']=contract.validate_module(main/'native_tls_rx_reserve.c')
        for name in ['native_tls_rx_reserve.c','native_tls_rx_reserve.h']:freeze(main/name,Path('candidate')/name)
        freeze(main/'compat/tls_static_rx/enable.cmake',Path('candidate/enable.cmake'))
        freeze(main/'compat/tls_static_rx/sdk-source-guards.json',Path('candidate/sdk-source-guards.json'))
        freeze(ROOT/'tools/patch_cyd_tls_static_rx.py',Path('candidate/patch_cyd_tls_static_rx.py'))
        for name in ['platform.h','test.c']:freeze(HERE/'unit'/name,Path('harness')/name)
        freeze(HERE/'sdk_spans.py',Path('sdk_spans.py'));freeze(Path(__file__),Path('run-host.py'));freeze(HERE/'unit/stale-storage.cpp',Path('harness/stale-storage.cpp'))
        for name in ['native_input_reclaim.c','native_input_reclaim.h']:freeze(ROOT/'idf/esp32-cyd2usb-native/main'/name,Path('reclaim')/name)
        patcher=load(candidate/'patch_cyd_tls_static_rx.py','frozen_registry_patcher');extract=load(out/'inputs/sdk_spans.py','frozen_registry_extract')
        checked=patcher.validate_sdk_guards(sdk,candidate/'sdk-source-guards.json');assert len(checked)==19
        for relative in checked:freeze(sdk/relative,Path('sdk')/relative)
        sdk_copy=out/'inputs/sdk';raw=(sdk_copy/'components/mbedtls/mbedtls/library/ssl_tls.c').read_bytes();overlay=patcher.patch(raw)
        (out/'sdk-overlay.c').write_bytes(overlay)
        anchors=[b'static int ssl_handshake_init(',b'void mbedtls_ssl_init(',b'int mbedtls_ssl_setup(',b'void mbedtls_ssl_session_reset_msg_layer(',b'void mbedtls_ssl_free(',b'void mbedtls_ssl_config_init(',b'void mbedtls_ssl_config_free(']
        spans=b'\n\n'.join(extract.function(overlay,anchor) for anchor in anchors)
        spans+=b'\n\n'+extract.function((sdk_copy/'components/mbedtls/mbedtls/tf-psa-crypto/platform/platform_util.c').read_bytes(),b'void mbedtls_zeroize_and_free(')+b'\n'
        sdk_body=b'#include "platform.h"\n#include "native_tls_rx_reserve.h"\n'+spans
        (out/'sdk-spans.c').write_bytes(sdk_body)
        report['exact_sdk_spans']={anchor.decode():hashlib.sha256(extract.function(overlay,anchor)).hexdigest() for anchor in anchors}
        module=(candidate/'native_tls_rx_reserve.c').read_bytes();assert b'mbedtls_ssl_conf_' not in module and b'user_data' not in module
        report['module_sha256']=hashlib.sha256(module).hexdigest();report['userdata_getter_setter_absent']=True
        stubs=out/'stubs';stubs.mkdir();ssl=(sdk_copy/'components/mbedtls/mbedtls/include/mbedtls/ssl.h').read_bytes()
        (stubs/'public_user_data.h').write_bytes(b'\n'.join(extract.function(ssl,anchor) for anchor in [b'static inline void mbedtls_ssl_conf_set_user_data_p(',b'static inline void *mbedtls_ssl_conf_get_user_data_p(',b'static inline void mbedtls_ssl_conf_set_user_data_n(',b'static inline uintptr_t mbedtls_ssl_conf_get_user_data_n('])+b'\n')
        misc=(sdk_copy/'components/mbedtls/mbedtls/library/ssl_misc.h').read_bytes()
        (stubs/'capacity.h').write_bytes(b'\n'.join(extract.macro(misc,name) for name in ['MBEDTLS_SSL_PAYLOAD_OVERHEAD','MBEDTLS_SSL_IN_PAYLOAD_LEN','MBEDTLS_SSL_OUT_PAYLOAD_LEN','MBEDTLS_SSL_HEADER_LEN','MBEDTLS_SSL_IN_BUFFER_LEN','MBEDTLS_SSL_OUT_BUFFER_LEN'])+b'\n')
        for name in ['esp_err.h','esp_crt_bundle.h','freertos/FreeRTOS.h','freertos/task.h','mbedtls/ssl.h','mbedtls/platform.h','mbedtls/platform_util.h','ssl_misc.h','tf_psa_crypto_common.h','adaptive_input.h']:
            path=stubs/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('#pragma once\n#include "platform.h"\n')
        required=['YORADIO_TLS_STATIC_RX_RESERVE','IDF_TARGET_ESP32','ESP_TLS_USING_MBEDTLS','MBEDTLS_INTERNAL_MEM_ALLOC','MBEDTLS_CERTIFICATE_BUNDLE']
        def config(d,zero=None,absent=None,extra='',version='60002'):
            (d/'sdkconfig.h').write_text(''.join('#define CONFIG_'+flag+' '+('0' if flag==zero else '1')+'\n' for flag in required if flag!=absent)+extra)
            (d/'esp_idf_version.h').write_text('#define ESP_IDF_VERSION_VAL(a,b,c) ((a)*10000+(b)*100+(c))\n#define ESP_IDF_VERSION '+version+'\n')
        def flags(d):return ['/usr/bin/gcc','-std=c11','-D_XOPEN_SOURCE=700','-O1','-g','-Wall','-Wextra','-Werror','-Wno-undef','-pedantic','-H','-pthread','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-fno-pie','-no-pie',*['-I'+host(v) for v in [d,stubs,out/'inputs/harness',candidate,out/'inputs/reclaim']]]
        tools=['/usr/bin/python3','-c','import hashlib,json,pathlib,subprocess; names=["/usr/bin/gcc","/usr/bin/g++","/usr/bin/as","/usr/bin/ld"]; names += [subprocess.check_output(["/usr/bin/gcc",v],text=True).strip() for v in ["-print-prog-name=cc1","-print-prog-name=cc1plus","-print-prog-name=collect2","-print-file-name=libasan.so","-print-file-name=libubsan.so"]]; print(json.dumps({str(pathlib.Path(p).resolve()):hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in names})); print(subprocess.check_output(["/usr/bin/gcc","--version"],text=True))']
        if a.prepare_only:
            report['status']='inputs_prepared_uncompiled_unrun';report['prepared_inputs_only']=True;save();print(json.dumps({'prepared':True,'passed':False,'compiled':False}));return
        code,log=execute('tools-before',tools);assert code==0,log;report['tools_before']=json.loads(log.splitlines()[0])
        cpp=out/'stale-storage.o'
        # A separate language mode preserves strict C flags for the production
        # module/SDK spans; the placement-new fixture has no exceptions or RTTI.
        cppdir=out/'cpp-config';cppdir.mkdir();config(cppdir)
        cpp_flags=[value for value in flags(cppdir) if value not in ['-std=c11','-H','-no-pie']]
        code,log=execute('cpp-lifetime-build',['/usr/bin/g++','-std=c++17','-fno-exceptions','-fno-rtti',*cpp_flags[1:],'-c',host(out/'inputs/harness/stale-storage.cpp'),'-o',host(cpp)]);assert code==0,log
        controls=[
            ('skip-init',None,'init','lifetime','init_revokes_stale_identity'),
            ('skip-free',None,'free','lifetime','free_revokes_stale_identity'),
            ('evict-full',(b'if (empty != RX_CONFIGURATION_CAPACITY)\n        s_radio_configurations[empty] = identity;',b'if (empty != RX_CONFIGURATION_CAPACITY)\n        s_radio_configurations[empty] = identity;\n    else s_radio_configurations[0] = identity;'),None,'registry_full','full_registry_does_not_evict'),
            ('forget-resets-loan',(b'    if (!configuration) return;\n    const uintptr_t identity = (uintptr_t)configuration;\n    portENTER_CRITICAL_SAFE(&s_lock);\n    for (unsigned index = 0;',b'    if (!configuration) return;\n    const uintptr_t identity = (uintptr_t)configuration;\n    portENTER_CRITICAL_SAFE(&s_lock);\n    if (s_state == RX_LOANED) s_state = RX_FREE;\n    for (unsigned index = 0;'),None,'lifetime','config_free_keeps_exclusive_loan'),
            ('task-only-init',(b'    if (!configuration) return;\n    const uintptr_t identity = (uintptr_t)configuration;\n    portENTER_CRITICAL_SAFE(&s_lock);',b'    if (!configuration) return;\n    const uintptr_t identity = (uintptr_t)configuration;\n    portENTER_CRITICAL(&s_lock);'),None,'lifetime','task_critical_not_isr'),
            ('skip-exclusive',(b'== identity && s_state == RX_FREE)',b'== identity)'),None,'concurrent','parallel_shared_or_distinct_exactly_one_loan'),
            ('early-publish-phase',(b's_state = RX_RETURNING;',b's_state = host_erase_control_active() ? RX_FREE : RX_RETURNING;'),None,'concurrent','no_reloan_during_erase_after_config_reuse'),
            ('ordinary-free-static',(b'if (pointer != s_rx) return false;',b'if (pointer != s_rx) return false;\n    mbedtls_free(pointer);\n    return true;'),None,'userdata','reserved_pointer_never_sdk_heap_free'),
            ('bypass-reclaim',(b'return mbedtls_calloc(count, bytes);',b'return __real_esp_mbedtls_mem_calloc(count, bytes);'),None,'fallback','busy_slot_reclaim_retry_preserved')]
        scenarios=['userdata','lifetime','registry_full','attach_failure','rollback','fallback','concurrent','stale_storage']
        for name,edit,sdk_edit,case,expected in [('canonical',None,None,None,None)]+controls:
            d=out/name;d.mkdir();config(d);source=module;body=sdk_body
            if edit:source=replace(source,*edit)
            if sdk_edit:
                anchor=b'void mbedtls_ssl_config_'+sdk_edit.encode()+b'('
                function=extract.function(body,anchor);changed=replace(function,b'    yoradio_tls_static_rx_forget_configuration(conf);',b'    /* negative: omitted lifecycle forget */')
                body=replace(body,function,changed)
            (d/'module.c').write_bytes(source);(d/'sdk.c').write_bytes(body);binary=d/'test'
            code,log=execute(name+'-build',flags(d)+[host(d/'module.c'),host(d/'sdk.c'),host(out/'inputs/reclaim/native_input_reclaim.c'),host(out/'inputs/harness/test.c'),host(cpp),'-o',host(binary)]);assert code==0,(name,log[-7000:])
            for scenario in [case] if case else scenarios:
                code,log=execute(name+'-'+scenario,[host(binary),scenario])
                assert not any(marker in log for marker in ['AddressSanitizer','LeakSanitizer','runtime error:','Assertion ']),(name,code,log)
                if expected:
                    assert code==2 and log.splitlines()[-1]=='TLS_RX_HOST_FAILURE '+expected and log.count('TLS_RX_HOST_FAILURE')==1,(name,code,log)
                    report['controls'][name]={'case':scenario,'exit_status':code,'expected_named_failure':expected,'phase_scoped':name=='early-publish-phase'}
                else:
                    assert code==0 and 'TLS_RX_HOST_COMPLETE case='+scenario in log,(name,code,log);report['positive_cases'][scenario]={'exit_status':code,'result':log.strip()}
                save()
        invalids=[(f+'-zero',f,None,'','60002') for f in required]+[(f+'-absent',None,f,'','60002') for f in required]+[('dynamic',None,None,'#define CONFIG_MBEDTLS_DYNAMIC_BUFFER 1\n','60002'),('custom',None,None,'#define CONFIG_MBEDTLS_CUSTOM_MEM_ALLOC 1\n','60002'),('variable',None,None,'#define MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH\n','60002'),('version',None,None,'','60100')]
        for name,zero,absent,extra,version in invalids:
            d=out/('reject-'+name);d.mkdir();config(d,zero,absent,extra,version);(d/'module.c').write_bytes(module)
            code,log=execute('reject-'+name,flags(d)+['-c',host(d/'module.c'),'-o',host(d/'module.o')]);expected='CYD RX reserve requires the audited ESP-IDF6.0.2 declaration/layout profile' if name=='version' else 'CYD RX reserve requires the audited classic ESP32 static/internal profile'
            assert code!=0 and code!='timeout' and expected in log,(name,code,log[-4000:]);report['compile_rejections'][name]={'exit_status':code,'exact_diagnostic':expected};save()
        # Final restored positive re-reads original candidate and actual SDK spans.
        assert (candidate/'native_tls_rx_reserve.c').read_bytes()==module
        assert patcher.validate_sdk_guards(sdk,candidate/'sdk-source-guards.json')==checked
        assert patcher.patch(raw)==overlay
        for scenario in scenarios:
            code,log=execute('restored-'+scenario,[host(out/'canonical/test'),scenario]);assert code==0 and 'TLS_RX_HOST_COMPLETE case='+scenario in log,(scenario,code,log)
        code,log=execute('tools-after',tools);assert code==0;report['tools_after']=json.loads(log.splitlines()[0]);assert report['tools_before']==report['tools_after']
        assert all(sha(Path(path))==entry['sha256'] and sha(out/entry['snapshot'])==entry['sha256'] for path,entry in report['inputs'].items())
        report['host_pthreads_are_not_actual_core_proof']=True;report['passed']=True;print(json.dumps({'passed':True,'positive_cases':len(report['positive_cases']),'controls':len(report['controls']),'compile_rejections':len(report['compile_rejections'])}),flush=True)
    except BaseException as e:report['error']=repr(e);raise
    finally:save()
if __name__=='__main__':main()
