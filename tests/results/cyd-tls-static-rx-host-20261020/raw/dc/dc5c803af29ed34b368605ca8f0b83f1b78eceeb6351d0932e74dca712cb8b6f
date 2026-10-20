"""Canonical sources: whole actual CYD owners + exact SDK lifetime spans.

Reuse the existing maintenance harness/RTOS/codec/output seams. Only its HTTP
seam gains typed configured callback + SDK setup/free bodies. Host crypto/types,
HTTP/TCP, clocks, RTOS and DMA remain explicit seams. No SDK target build/QEMU,
hardware benefit or transport/protocol-conformance claim.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"tests/native/cyd_tls_static_rx/service"
COMMON=HERE.parent
MAIN=Path('idf/esp32-cyd2usb-native/main')
SHARED=Path('idf/components/native_stream')

def digest(data):return hashlib.sha256(data).hexdigest()
def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def stripped(path,keep=()):
    return re.sub(r'^#include[^\n]*\n',lambda m:m[0] if any('"'+n+'"' in m[0] for n in keep) else '',path.read_text(),flags=re.M)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def once(data,old,new):
    assert data.count(old)==1,(old,data.count(old));return data.replace(old,new,1)

def board_stack_profile(board,platform):
    # Preserve actual frozen source spellings; no numeric task-size copy.
    import re
    names=('BOARD_TASK_STACK_RADIO_STREAM','BOARD_TASK_STACK_AUDIO_DECODER','BOARD_TASK_STACK_AUDIO_OUTPUT')
    lines=[re.search(r'^#define '+name+r'\s+\d+',board,re.M)[0] for name in names]
    for name in names:
        platform,n=re.subn(r'^#define '+name+r'\s+\d+\n','',platform,flags=re.M);assert n==1
    platform=once(platform,'#pragma once\n','#pragma once\n#include "board_task_profile.h"\n')
    platform=once(platform,'assert(stack);','assert(stack==(next==0?BOARD_TASK_STACK_RADIO_STREAM:next==1?BOARD_TASK_STACK_AUDIO_DECODER:BOARD_TASK_STACK_AUDIO_OUTPUT));')
    return '#pragma once\n'+'\n'.join(lines)+'\n',platform,lines

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--sdk',type=Path,required=True)
    p.add_argument("--preflight-only",action="store_true")
    p.add_argument("--prepare-only",action="store_true",help="Freeze/extract complete source inputs, no compiler/tool invocation")
    p.add_argument('--backend',choices=['PDM','DAC','LEGACY_DAC'],action='append')
    p.add_argument('--quick',action='store_true',help='Only one option pair, callback/reopen cases; not complete qualification')
    a=p.parse_args();out=a.output.resolve();sdk=a.sdk.resolve()
    assert out.is_relative_to(ROOT/".build") and not out.exists()
    contract=load(COMMON/"source_contract.py","service_contract")
    if a.preflight_only:
        print(json.dumps(contract.preflight(ROOT,sdk)));return
    out.mkdir(parents=True)
    report=dict(passed=False,scope=__doc__,target_build=False,qemu=False,hardware=False,quick=a.quick,
                inputs={},commands=[],variants={},controls={},generated={},limitations=[
                    'Host context/config/crypto/RTOS/HTTP/DMA are explicit seams; no target ABI or TLS handshake claim',
                    'Whole production service, adaptive FIFO, state and output execute with only platform includes replaced',
                    'Host capacity inputs retain explicit 16/32/256/0 IV/MAC/padding/CID seams, not actual target capacity proof',
                    'SDK public getter/setter, setup/error/reset/free spans are exact source, not complete SDK compilation',
                    'Canonical reclaim runs against actual shared adaptive queue; no physical exhaustion or memory benefit inferred',
                    'Existing synthetic codec fixture is unchanged; no deferred codec extension tests added'])
    env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0',ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    def freeze(path,relative):
        data=path.read_bytes();dest=out/'inputs'/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        report['inputs'][str(path)]={'sha256':digest(data),'bytes':len(data),'snapshot':dest.relative_to(out).as_posix()};return dest
    def execute(label,command,timeout=60):
        cmd=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,command))
        try:
            result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=timeout)
            code,data=result.returncode,result.stdout
        except subprocess.TimeoutExpired as e:
            code,data='timeout',e.output or b''
        log=out/(label+'.log');log.write_bytes(data)
        report['commands'].append(dict(label=label,argv=cmd,exit_status=code,log_sha256=digest(data)));save()
        return code,data.decode(errors='replace')
    try:
        paths=[Path(__file__),HERE/'tls_bridge.c',HERE/'tls_bridge.h',HERE/'http-seam.c.inc',HERE/'service-scenarios.c.inc',
               ROOT/'tests/run-cyd-maintenance.py',ROOT/'tests/native/cyd_maintenance_test.c',ROOT/'tests/native/cyd_maintenance_platform.h',
               ROOT/'tests/native/cyd_output_pause_test.c',ROOT/'tests/native/cyd_output_metrics_noop.h',ROOT/'tests/native/audio_power_seam.h',
               COMMON/"sdk_spans.py",COMMON/"tls_types.h",COMMON/"source_contract.py"]
        paths += [ROOT/MAIN/n for n in ('audio_service.c','audio_service.h','native_audio_output.c','native_audio_output.h','native_state.c','native_state.h','native_health.h','native_output_metrics.h','input_prefill.h','native_input_reclaim.c','native_input_reclaim.h','board_config.h')]
        paths += [ROOT/SHARED/'adaptive_input.c',ROOT/SHARED/'icy_title.c',*sorted((ROOT/SHARED/'include').glob('*.h'))]
        paths += [ROOT/MAIN/n for n in ("native_tls_rx_reserve.c","native_tls_rx_reserve.h","Kconfig.projbuild","compat/tls_static_rx/enable.cmake","compat/tls_static_rx/sdk-source-guards.json")]
        paths += [ROOT/"tools/patch_cyd_tls_static_rx.py"]
        for path in paths:
            if path.is_file():freeze(path,path.relative_to(ROOT))
        frozen=out/'inputs'
        main=frozen/MAIN;shared=frozen/SHARED;tests=frozen/'tests/native';candidate=main
        own=frozen/HERE.relative_to(ROOT)
        contract=load(frozen/'tests/native/cyd_tls_static_rx/source_contract.py','frozen_service_source_contract')
        actual=(main/'audio_service.c').read_text()
        assert actual.count('.crt_bundle_attach = native_tls_rx_reserve_crt_bundle_attach,')==1
        module_bytes=(candidate/'native_tls_rx_reserve.c').read_bytes()
        report['module_contract']=contract.validate_module(candidate/'native_tls_rx_reserve.c')
        extract=load(frozen/'tests/native/cyd_tls_static_rx/sdk_spans.py','canonical_sdk_spans')
        sdk_paths={}
        for rel in ['components/mbedtls/mbedtls/library/ssl_tls.c','components/mbedtls/mbedtls/library/ssl_misc.h','components/mbedtls/mbedtls/include/mbedtls/ssl.h','components/mbedtls/mbedtls/tf-psa-crypto/platform/platform_util.c']:
            sdk_paths[Path(rel).name]=freeze(sdk/rel,Path('sdk')/rel)
        patcher=load(frozen/'tools/patch_cyd_tls_static_rx.py','canonical_patcher')
        guards=candidate/'compat/tls_static_rx/sdk-source-guards.json'
        report['sdk_supporting_guards']=patcher.validate_sdk_guards(sdk,guards)
        for relative in report['sdk_supporting_guards']:freeze(sdk/relative,Path('sdk')/relative)
        raw=sdk_paths['ssl_tls.c'].read_bytes();patched=patcher.patch(raw)
        anchors=[b'static int ssl_handshake_init(',b'void mbedtls_ssl_init(',b'int mbedtls_ssl_setup(',b'void mbedtls_ssl_session_reset_msg_layer(',b'void mbedtls_ssl_free(',b'void mbedtls_ssl_config_init(',b'void mbedtls_ssl_config_free(']
        sdk_end=b'\n\n'+extract.function(sdk_paths['platform_util.c'].read_bytes(),b'void mbedtls_zeroize_and_free(')+b'\n'
        bodies={name:b'\n\n'.join(extract.function(source,anchor) for anchor in anchors)+sdk_end for name,source in [('on',patched),('off',raw)]}
        for name,body in bodies.items():(out/('sdk-'+name+'.c')).write_bytes(b'#include "platform.h"\n#include "native_tls_rx_reserve.h"\n'+body)
        report['sdk_span_hashes']={name:{anchor.decode():digest(extract.function(source,anchor)) for anchor in anchors} for name,source in [('on',patched),('off',raw)]}
        stubs=out/'stubs';stubs.mkdir();(stubs/'mbedtls').mkdir();(stubs/'freertos').mkdir()
        macro_names=['MBEDTLS_SSL_PAYLOAD_OVERHEAD','MBEDTLS_SSL_IN_PAYLOAD_LEN','MBEDTLS_SSL_OUT_PAYLOAD_LEN','MBEDTLS_SSL_HEADER_LEN','MBEDTLS_SSL_IN_BUFFER_LEN','MBEDTLS_SSL_OUT_BUFFER_LEN']
        (stubs/'capacity.h').write_bytes(b'\n'.join(extract.macro(sdk_paths['ssl_misc.h'].read_bytes(),name) for name in macro_names)+b'\n')
        public=sdk_paths['ssl.h'].read_bytes()
        (stubs/'public_user_data.h').write_bytes(extract.function(public,b'static inline void mbedtls_ssl_conf_set_user_data_p(')+b'\n'+extract.function(public,b'static inline void *mbedtls_ssl_conf_get_user_data_p(')+b'\n'+extract.function(public,b'static inline void mbedtls_ssl_conf_set_user_data_n(')+b'\n'+extract.function(public,b'static inline uintptr_t mbedtls_ssl_conf_get_user_data_n(')+b'\n')
        (stubs/'tls_types.h').write_bytes((frozen/'tests/native/cyd_tls_static_rx/tls_types.h').read_bytes())
        (stubs/'platform.h').write_text('#pragma once\n#include <assert.h>\n#include <pthread.h>\n#include "tls_types.h"\nenum {ESP_OK=0};\ntypedef int BaseType_t;\ntypedef uint32_t TickType_t;\ntypedef pthread_mutex_t portMUX_TYPE;\n#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER\nvoid host_enter(portMUX_TYPE *lock);\nvoid host_exit(portMUX_TYPE *lock);\n#define portENTER_CRITICAL(lock) host_enter(lock)\n#define portEXIT_CRITICAL(lock) host_exit(lock)\n/* Task-only service seam: xPortInIsrContext is always false. */\n#define portENTER_CRITICAL_SAFE(lock) host_enter(lock)\n#define portEXIT_CRITICAL_SAFE(lock) host_exit(lock)\nbool xPortInIsrContext(void);\n')
        for name in ('platform.h','platform_util.h'):(stubs/'mbedtls'/name).write_text('#pragma once\n#include "platform.h"\n')
        (stubs/'mbedtls/ssl.h').write_text('#pragma once\n#include "tls_types.h"\n')
        (stubs/'esp_crt_bundle.h').write_text('#pragma once\n#include "tls_types.h"\n')
        (stubs/'esp_err.h').write_text('#pragma once\n')
        for name in ('ssl_misc.h','tf_psa_crypto_common.h'):(stubs/name).write_text('#pragma once\n#include "platform.h"\n')
        # Service's existing pthread RTOS seam stays in its own TU. Candidate and
        # canonical reclaim receive ABI-equivalent narrow lock/type declarations.
        for name in ('FreeRTOS.h','task.h','semphr.h'):(stubs/'freertos'/name).write_text('#pragma once\n#ifdef SERVICE_HOST_TU\n#include "cyd_maintenance_platform.h"\n#else\n#include "platform.h"\n#endif\n')
        platform=(tests/'cyd_maintenance_platform.h').read_text()
        board=(main/'board_config.h').read_text()
        profile,platform,macro_lines=board_stack_profile(board,platform)
        (out/'board_task_profile.h').write_text(profile)
        report['board_stack_extraction']={'source_snapshot':(main/'board_config.h').relative_to(out).as_posix(),'source_sha256':digest((main/'board_config.h').read_bytes()),'exact_macro_lines':macro_lines,'header_sha256':digest(profile.encode()),'assertion_uses_macro_names':True}
        (out/'cyd_maintenance_platform.h').write_text(platform)
        for name in ('cyd_output_pause_test.c','cyd_output_metrics_noop.h','audio_power_seam.h'):(out/name).write_bytes((tests/name).read_bytes())
        harness=(tests/'cyd_maintenance_test.c').read_text()
        start=harness.index('enum {HTTP_EVENT_ON_HEADER=1};');end=harness.index('\n#include "adaptive.inc"',start)
        harness=harness[:start]+(own/'http-seam.c.inc').read_text()+harness[end:]
        harness=once(harness,'    if(!strcmp(scenario,"idle"))', (own/'service-scenarios.c.inc').read_text()+'    if(!strcmp(scenario,"idle"))')
        harness=once(harness,'    TaskHandle_t none[3]={0};','    tls_assert_drained();\n#if CONFIG_YORADIO_TLS_INPUT_RECLAIM\n    tls_check(native_input_reclaim_detach(s_encoded)==NATIVE_INPUT_RECLAIM_DETACHED,"host_final_quiescent_detach");\n#endif\n    TaskHandle_t none[3]={0};')
        (out/'service.c').write_text('#define SERVICE_HOST_TU 1\n'+harness)
        (out/'audio.inc').write_text(stripped(candidate/'audio_service.c',('stream_encoded_router.h','stream_start.h','input_prefill.h','native_tls_rx_reserve.h','native_input_reclaim.h')))
        (out/'production.inc').write_text(stripped(main/'native_audio_output.c'))
        (out/'adaptive.inc').write_text(stripped(shared/'adaptive_input.c'))
        (out/'state.inc').write_text(stripped(main/'native_state.c'))
        new_cases=['tls_binding','tls_plain','tls_occupied','tls_numeric','tls_attach_error','tls_nested','tls_init_error','tls_open_before_error','tls_open_after_error','tls_setup_error','tls_headers_error','tls_redirect_error','tls_redirect_https','tls_redirect_plain','tls_redirect_to_https','tls_reopen','tls_cancel_open']
        old_cases=['idle','pause_publish','resume','stop_cancels','end_no_resume','end_busy','state_lock','control_lock','queue_failure','wide_epoch','timeout_read','timeout_open','timeout_headers','timeout_close','timeout_cleanup','late_encoded','late_pcm','output_write','output_disable','control_reading','staging','back_to_back','pause_failure','resume_queue_failure','empty_receive_epoch','stopped_no_resume','pending_resume']
        pairs=[(1,1)] if a.quick else [(1,1),(1,0),(0,1),(0,0)]
        backends=a.backend or ['PDM','DAC','LEGACY_DAC']
        tool_probe=['/usr/bin/python3','-c','import hashlib,json,pathlib,subprocess; names=["/usr/bin/gcc","/usr/bin/as","/usr/bin/ld"]; names += [subprocess.check_output(["/usr/bin/gcc",v],text=True).strip() for v in ["-print-prog-name=cc1","-print-prog-name=collect2","-print-file-name=libasan.so","-print-file-name=libubsan.so"]]; print(json.dumps({str(pathlib.Path(p).resolve()):hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in names})); print(subprocess.check_output(["/usr/bin/gcc","--version"],text=True))']
        if a.prepare_only:
            report['status']='inputs_prepared_uncompiled_unrun';report['prepared_inputs_only']=True
            assert all(digest(Path(path).read_bytes())==entry['sha256'] for path,entry in report['inputs'].items())
            save();print(json.dumps({'prepared':True,'passed':False,'compiled':False}));return
        code,log=execute('tools-before',tool_probe);assert code==0,log;report['tools_before']=json.loads(log.splitlines()[0]);report['native_python']={sys.executable:digest(Path(sys.executable).read_bytes())}
        canonical_command=None
        for reserve,reclaim in pairs:
            config=out/f'config-r{reserve}-q{reclaim}';config.mkdir()
            flags=['YORADIO_TLS_STATIC_RX_RESERVE','IDF_TARGET_ESP32','ESP_TLS_USING_MBEDTLS','MBEDTLS_INTERNAL_MEM_ALLOC','MBEDTLS_CERTIFICATE_BUNDLE']
            (config/'sdkconfig.h').write_text(''.join('#define CONFIG_'+v+' '+str(reserve if v=='YORADIO_TLS_STATIC_RX_RESERVE' else 1)+'\n' for v in flags)+('#define CONFIG_YORADIO_TLS_INPUT_RECLAIM 1\n' if reclaim else ''))
            (config/'esp_idf_version.h').write_text('#define ESP_IDF_VERSION_VAL(a,b,c) ((a)*10000+(b)*100+(c))\n#define ESP_IDF_VERSION 60002\n')
            for backend in backends:
                tag=f'r{reserve}-q{reclaim}-{backend.lower()}';binary=out/tag
                defines=['-DCONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_'+backend+'=1','-DCONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=1','-DCONFIG_YORADIO_FRAME_ROUTER=1','-DCONFIG_YORADIO_STREAM_CONFIRM=1','-DCONFIG_YORADIO_INPUT_TAIL_COALESCE=1','-DCONFIG_YORADIO_INPUT_PREFILL_MS=250']
                if reclaim:defines+=['-DCONFIG_YORADIO_TLS_INPUT_RECLAIM=1']
                command=['/usr/bin/gcc','-std=c11','-D_POSIX_C_SOURCE=200809L','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-variable','-Wno-unused-function','-pthread','-fno-omit-frame-pointer','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all',*defines,'-include',host(config/'sdkconfig.h')]
                command+=['-I'+host(path) for path in (out,config,stubs,own,candidate,main,shared/'include')]
                command += [host(out/'service.c'),host(own/'tls_bridge.c'),host(out/('sdk-'+('on' if reserve else 'off')+'.c')),host(shared/'icy_title.c')]
                if reserve:command+=[host(candidate/'native_tls_rx_reserve.c')]
                if reclaim:command+=[host(main/'native_input_reclaim.c')]
                command+=['-o',host(binary)]
                code,log=execute('build-'+tag,command);assert code==0,log[-10000:]
                if reserve==1 and reclaim==1 and canonical_command is None:canonical_command=list(command)
                results={}
                for case in (['tls_binding','tls_reopen'] if a.quick else new_cases+old_cases+(['delete_failure'] if backend!='LEGACY_DAC' else [])):
                    code,log=execute(tag+'-'+case,[host(binary),case],20)
                    assert code==0 and 'PASS '+case+';' in log,(tag,case,code,log[-6000:])
                    results[case]={'exit_status':code,'result':log.strip()}
                report['variants'][tag]=results;save();print(tag+': '+str(len(results))+' PASS',flush=True)
        if not a.quick:
            assert canonical_command
            source_path=out/'audio.inc';original_source=source_path.read_text()
            controls=[('wrong-radio-callback',source_path,'.crt_bundle_attach = native_tls_rx_reserve_crt_bundle_attach,','.crt_bundle_attach = esp_crt_bundle_attach,','actual_radio_callback_selection'),
                      ('omitted-radio-registration',candidate/'native_tls_rx_reserve.c','if (result == ESP_OK)\n            register_configuration(configuration);','if (false && result == ESP_OK)\n            register_configuration(configuration);','live_radio_loan_matches_transport')]
            for name,path,old,new,expected in controls:
                original=path.read_bytes();mutated=once(original.decode(),old,new);path.write_bytes(mutated.encode())
                command=list(canonical_command);command[-1]=host(out/('control-'+name))
                code,log=execute('build-control-'+name,command);assert code==0,log[-6000:]
                code,log=execute('control-'+name,[command[-1],'tls_binding'],20)
                assert code==2 and log.count('TLS_SERVICE_FAILURE '+expected+'\n')==1 and 'AddressSanitizer' not in log and 'runtime error:' not in log,(name,code,log)
                report['controls'][name]={'exit_status':code,'expected_named_failure':expected,'mutation':{'path':path.relative_to(out).as_posix(),'original_sha256':digest(original),'mutated_sha256':digest(mutated.encode()),'old':old,'new':new}}
                path.write_bytes(original);save()
            assert source_path.read_text()==original_source
            assert (candidate/'native_tls_rx_reserve.c').read_bytes()==module_bytes
        code,log=execute('tools-after',tool_probe);assert code==0;report['tools_after']=json.loads(log.splitlines()[0]);assert report['tools_before']==report['tools_after']
        assert patcher.validate_sdk_guards(sdk,guards)==report['sdk_supporting_guards']
        for path,data in report['inputs'].items():assert digest(Path(path).read_bytes())==data['sha256'],path
        report['generated']={f.relative_to(out).as_posix():digest(f.read_bytes()) for f in out.rglob('*') if f.is_file() and f.name!='report.json' and 'inputs' not in f.relative_to(out).parts}
        report['positive_case_count']=sum(len(v) for v in report['variants'].values());report['variant_count']=len(report['variants']);report['named_control_count']=len(report['controls'])
        report['passed']=True
    except BaseException as e:
        report['error']=repr(e);save();raise
    finally:save()

if __name__=='__main__':main()
