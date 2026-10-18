"""Actual HTTPD wire/parser/OTA handlers over TCP and verified native ESP-TLS.

Composes frozen successful HTTP/WS/TLS reports. Only field-model platform seams
are adapted; generated SDK and production algorithm bodies stay unchanged.
Credentials are created only under a Linux temporary directory.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/native/ota_integration'
SDK_ROOT=ROOT/'.idf' if (ROOT/'.idf').is_dir() else ROOT.parents[1]/'.idf'

def host(path):
    path=Path(path).resolve().as_posix()
    return '/mnt/'+path[0].lower()+path[2:] if sys.platform=='win32' else path
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def execute(command,log):
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    log.write_bytes(result.stdout)
    if result.returncode:raise RuntimeError(result.stdout.decode(errors='replace'))
    return result.stdout
def module(path):
    spec=importlib.util.spec_from_file_location('ota_http_snapshot',path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

def model(header,image_header):
    # Adapt only the previously-qualified host field model, never SDK C.
    replacements={
        'struct resp_hdr resp_hdrs[2]':'struct resp_hdr resp_hdrs[8]',
        'unsigned,void *,unsigned,void *);':'unsigned,void *,unsigned,TaskHandle_t *);',
        '#define ESP_ERR_INVALID_ARG 1':'#define ESP_ERR_INVALID_ARG 0x102',
        '#define ESP_ERR_INVALID_STATE 2':'#define ESP_ERR_INVALID_STATE 0x103',
        '#define ESP_ERR_INVALID_SIZE 3':'#define ESP_ERR_INVALID_SIZE 0x104',
        '#define ESP_ERR_NO_MEM 7':'#define ESP_ERR_NO_MEM 0x101',
    }
    for old,new in replacements.items():assert header.count(old)==1,old;header=header.replace(old,new)
    public=image_header[image_header.index('typedef unsigned esp_ota_handle_t;'):image_header.index('typedef void *httpd_handle_t;')]
    return '''#pragma once
#include <stdint.h>
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
typedef unsigned portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(p) assert(!(*(p))++)
#define portEXIT_CRITICAL(p) assert((*(p))--==1)
#define pdTRUE 1
#define pdMS_TO_TICKS(v) (v)
#define portMAX_DELAY UINT32_MAX
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_NOT_SUPPORTED 0x106
#define ESP_ERR_HTTPD_RESP_HDR 0x602
#define ESP_ERR_HTTPD_RESP_SEND 0x604
#define HTTPD_RESP_USE_STRLEN (-1)
#define HTTP_SERVER_EVENT_HEADERS_SENT 4
#define HTTP_SERVER_EVENT_SENT_DATA 5
#define ESP_IMAGE_HASH_LEN 32
#define OTA_WITH_SEQUENTIAL_WRITES 0xfffffffeU
#define ESP_STATIC_ASSERT _Static_assert
#define FORCE_INLINE_ATTR static inline
'''+header+'\n'+public+'''
typedef struct {uint64_t epoch;} audio_maintenance_token_t;
static esp_err_t audio_service_maintenance_begin(uint32_t,audio_maintenance_token_t *);
static esp_err_t audio_service_maintenance_end(audio_maintenance_token_t *,bool);
static TickType_t xTaskGetTickCount(void);
static void xTaskNotifyGive(TaskHandle_t);
static unsigned ulTaskNotifyTake(int,TickType_t);
static void vTaskDelete(TaskHandle_t);
static void esp_restart(void);
static void display_settings_note_activity(void);
static void *response_malloc(size_t);
static void *workspace_calloc(size_t,size_t);
static void workspace_free(void *);
static void observed_prepare_close(httpd_handle_t,int,bool);
#ifdef INTEGRATION_TLS
void native_web_transport_prepare_close(httpd_handle_t,int,bool);
#else
static void native_web_transport_prepare_close(httpd_handle_t,int,bool);
#endif
#define httpd_resp_sendstr(r,s) httpd_resp_send(r,s,HTTPD_RESP_USE_STRLEN)
'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--http-evidence',type=Path,required=True)
    parser.add_argument('--ws-evidence',type=Path,default=ROOT/'.build/ws-integration-qualified-final')
    parser.add_argument('--tls-cyd',type=Path,default=ROOT/'.build/native-tls-ota-602')
    parser.add_argument('--tls-c3',type=Path,default=ROOT/'.build/native-tls-ota-611')
    parser.add_argument('--crypto-cyd',type=Path,default=ROOT/'.build/native-tls-crypto-v602')
    parser.add_argument('--crypto-c3',type=Path,default=ROOT/'.build/native-tls-crypto-v611')
    parser.add_argument('--target',choices=['cyd','c3','both'],default='both')
    parser.add_argument('--transport',choices=['plain','tls','both'],default='both')
    args=parser.parse_args()
    if sys.platform=='win32':
        command=['wsl.exe','--exec','python3',host(__file__)]
        for key,value in vars(args).items():command+=['--'+key.replace('_','-'),host(value) if isinstance(value,Path) else value]
        raise SystemExit(subprocess.call(command))
    import resource
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    http=args.http_evidence.resolve();ws=args.ws_evidence.resolve()
    http_report=json.loads((http/'report.json').read_text());ws_report=json.loads((ws/'report.json').read_text())
    assert http_report['passed'] and ws_report['passed']
    report={'sanitizers':['ASan','UBSan'],'source_sha256':{},'variants':{},'input_report_sha256':{'http':digest(http/'report.json'),'ws':digest(ws/'report.json')}}
    for path in [Path(__file__),*FIXTURE.glob('*.*')]:
        key=path.relative_to(ROOT);target=out/'sources'/key;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes());report['source_sha256'][key.as_posix()]=digest(target)
    shutil.copytree(http/'sources',out/'http-sources');shutil.copytree(ws/'sources',out/'ws-sources')
    helper=module(out/'http-sources/tests/run-native-ota-http.py')
    # Reject stale production body snapshots. Audio implementation is a stated
    # ACK seam, while the actual handler/reboot/form/image/HTTP bodies are exact.
    for key,value in http_report['source_sha256'].items():
        if key.startswith('idf/') and not key.endswith('audio_service.h'):assert digest(ROOT/key)==value,'Regenerate current HTTP evidence: '+key
    with tempfile.TemporaryDirectory(prefix='ota-wire-') as ephemeral:
      temporary=Path(ephemeral);certificate=temporary/'certificate.pem';private=temporary/'private.pem';traditional=temporary/'traditional.pem'
      if args.transport!='plain':
        execute(['openssl','req','-x509','-newkey','rsa:2048','-sha256','-nodes','-keyout',str(private),'-out',str(certificate),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost','-addext','basicConstraints=critical,CA:TRUE'],temporary/'credential.log')
        os.chmod(private,0o600)
        execute(['openssl','pkey','-in',str(private),'-traditional','-out',str(traditional)],temporary/'container.log');os.chmod(traditional,0o600)
      for target,tls_evidence,cache in [('cyd',args.tls_cyd,args.crypto_cyd),('c3',args.tls_c3,args.crypto_c3)]:
        if args.target!='both' and args.target!=target:continue
        for transport in ['plain','tls']:
          if args.transport!='both' and args.transport!=transport:continue
          directory=out/(target+'-'+transport);directory.mkdir()
          shutil.copytree(ws/target/'sdk-sources',directory/'sdk-sources')
          for path in (ws/target).glob('*.inc'):
            if '-original' not in path.name and path.name!='application.inc':shutil.copyfile(path,directory/path.name)
          if transport=='plain':shutil.copytree(ws/target/'mbedtls',directory/'mbedtls')
          for name in ['sdk-app-format.h','sdk-app-desc.h','sdk-image-types.inc','reboot.inc','target.inc','web_ota.h','web_reboot.h' if target=='cyd' else 'websocket_service.h']:
            shutil.copyfile(http/target/name,directory/name)
          for key,value in http_report['variants'][target]['sdk_sha256'].items():
            if key in ws_report['variants'][target]['sdk_sha256']:assert value==ws_report['variants'][target]['sdk_sha256'][key],key
          component=out/'http-sources/idf/components/native_ota'
          for path in (component/'include').glob('*.h'):shutil.copyfile(path,directory/path.name)
          (directory/'model.h').write_text(model((out/'ws-sources/tests/native/ws_integration/platform.h').read_text(),(out/'http-sources/tests/native/ota_http/host.h').read_text()))
          for name in ['esp_err.h','esp_http_server.h','esp_ota_ops.h','esp_app_format.h','esp_app_desc.h','esp_image_format.h','esp_timer.h','esp_system.h','audio_service.h','deep_sleep_clock.h','display_settings.h','native_web_transport.h','freertos/FreeRTOS.h','freertos/task.h','lwip/sockets.h']:
            path=directory/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('#pragma once\n#include "model.h"\n')
          (directory/'native_state.h').write_text('#pragma once\n#include "model.h"\n')
          sdk_txrx=(http/target/'sdk-sources/components/esp_http_server/src/httpd_txrx.c').read_text()
          (directory/'sdk-response.inc').write_text(helper.selected(sdk_txrx,['httpd_send_all','httpd_resp_set_hdr','httpd_resp_set_status','httpd_resp_set_type','httpd_resp_send']))
          unit=directory/'integration.c'
          unit.write_text(('#define TARGET_C3 1\n' if target=='c3' else '')+('#define INTEGRATION_TLS 1\n' if transport=='tls' else '')+'''#include "model.h"
'''+('''#include "psa/crypto.h"
#include "mbedtls/base64.h"
''' if transport=='tls' else '#include "crypto.inc"\n')+'''#include "native_httpd_headers.h"
#include "web_ota.h"
#include "'''+('web_reboot.h' if target=='cyd' else 'websocket_service.h')+'''"
#include "reboot.inc"
#include "sdk-ws.inc"
#include "platform-declarations.h"
#define httpd_req_recv sdk_req_recv
#include "sdk-txrx.inc"
#undef httpd_req_recv
int httpd_req_recv(httpd_req_t *request,char *data,size_t size) {if(request_deletes&&!workspace)++purge_receives;return sdk_req_recv(request,data,size);}
#define malloc response_malloc
#include "sdk-response.inc"
#undef malloc
#define httpd_req_delete sdk_req_delete
#include "sdk-parse.inc"
#undef httpd_req_delete
esp_err_t httpd_req_delete(struct httpd_data *hd) {++request_deletes;return sdk_req_delete(hd);}
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#include "native_ota_sink.c"
#include "native_ota_form.c"
#define calloc workspace_calloc
#define free workspace_free
#define native_web_transport_prepare_close observed_prepare_close
#include "native_ota_http.c"
#undef native_web_transport_prepare_close
#undef free
#undef calloc
#include "target.inc"
#include "platform.c"
#include "test.c"
''')
          (directory/'platform-declarations.h').write_text('static unsigned request_deletes,purge_receives;\nstatic void *workspace;\n')
          includes=[directory,out/'sources/tests/native/ota_integration',out/'ws-sources/idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455',out/'http-sources/idf/components/native_stream/include',out/'ws-sources/idf/components/native_stream/include',out/'http-sources/idf/components/native_storage/include',component,directory/'sdk-sources/components/http_parser']
          flags=['-std=c11','-D_GNU_SOURCE','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-Wno-misleading-indentation','-Wno-sign-compare','-Wno-format','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-ffunction-sections','-fdata-sections']
          extra=[];tls_report=None
          if transport=='tls':
            tls_evidence=tls_evidence.resolve();cache=cache.resolve();tls_report=json.loads((tls_evidence/'report.json').read_text())
            assert tls_report['passed'] and tls_report['crypto_fingerprint']==json.loads((cache/'identity.json').read_text())['fingerprint']
            for key,value in tls_report['source_sha256'].items():
              if key.startswith('idf/components/native_web_transport/') and (ROOT/key).is_file():assert digest(ROOT/key)==value,'Regenerate current TLS evidence: '+key
            shutil.copytree(tls_evidence/'sources',directory/'tls-sources')
            for name in ['sdk-functions.inc','transport-production.inc','esp_err.h','sdk-tls-errors.h']:
              shutil.copyfile(tls_evidence/name,directory/name)
            if (tls_evidence/'sdk-key-config.h').is_file():shutil.copyfile(tls_evidence/'sdk-key-config.h',directory/'sdk-key-config.h');flags.append('-DHOST_ESP_TLS_UNIFIED_KEYS=1')
            prefix=(directory/'tls-sources/tests/native/native_web_transport/esp_tls_host.c').read_text();prefix=prefix[:prefix.index('static uint8_t *read_ephemeral')]
            first=prefix.index('static struct {int socket;');last=prefix.index('static uint8_t *nvs_blob;')
            externs='''void *httpd_sess_get_transport_ctx(httpd_handle_t,int);
void httpd_sess_set_transport_ctx(httpd_handle_t,int,void *,void (*)(void *));
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_sess_set_pending_override(httpd_handle_t,int,httpd_pending_func_t);
'''
            (directory/'backend.c').write_text(prefix[:first]+externs+prefix[last:]+'\n'+(out/'ws-sources/tests/native/ws_integration/tls_backend.c').read_text())
            sdk=SDK_ROOT/tls_report['sdk'];mbed=sdk/'components/mbedtls/mbedtls';crypto=mbed/'tf-psa-crypto'
            includes += [cache/'host-config',sdk/'components/mbedtls/port/include',mbed/'include',mbed/'library',*[crypto/name for name in ['include','core','dispatch','utilities','extras','platform','drivers/builtin/include','drivers/builtin/src','drivers/everest/include','drivers/everest/include/tf-psa-crypto/private/everest','drivers/everest/include/tf-psa-crypto/private/everest/kremlib','drivers/p256-m/p256-m/include','drivers/p256-m/p256-m/include/p256-m','drivers/p256-m/p256-m_driver_interface','drivers/pqcp/include','drivers/pqcp/src','drivers/pqcp/mldsa-native/mldsa']]]
            extra=[str(directory/'backend.c'),str(cache/'libpinned-mbedtls.a')]
          binary=directory/'integration'
          execute(['gcc',*flags,*['-I'+str(p) for p in includes],str(unit),str(directory/'sdk-sources/components/http_parser/http_parser.c'),*extra,'-Wl,--gc-sections','-no-pie','-pthread','-o',str(binary)],directory/'build.log')
          packed=temporary/(target+'.ntls')
          if transport=='tls':execute(['python3',str(directory/'tls-sources/idf/components/native_web_transport/tools/pack_tls_bundle.py'),'--certificate',str(certificate),'--key',str(traditional),'--output',str(packed)],directory/'packer.log')
          log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','90',str(binary),str(packed),str(out/'sources/tests/native/ota_integration/client.py'),str(certificate),str(temporary/(target+'-'+transport+'.img'))],directory/'test.log')
          print(target+'-'+transport+': '+log.decode().strip())
          report['variants'][target+'-'+transport]={'passed':True,'result':log.decode().strip(),'http_source_sha256':http_report['source_sha256'],'sdk_overlay':ws_report['variants'][target]['overlay'],'sdk_sha256':ws_report['variants'][target]['sdk_sha256'],'composed_sha256':{p.name:digest(p) for p in directory.glob('*.inc')},'generated_model_sha256':digest(directory/'model.h')}
          if tls_report:report['variants'][target+'-'+transport].update(tls_report_sha256=digest(tls_evidence/'report.json'),crypto_archive_sha256=digest(cache/'libpinned-mbedtls.a'),tls_source_sha256=tls_report['source_sha256'])
          if target=='cyd' and transport=='plain':
            raw=(component/'native_ota_http.c').read_text()
            old='config->finish(config->context, activated);\n    return ESP_FAIL;'
            assert raw.count(old)==1
            mutant=directory/'terminal-return-ok.inc';mutant.write_text(raw.replace(old,'config->finish(config->context, activated);\n    return ESP_OK;'))
            mutant_unit=directory/'terminal-return-ok.c';mutant_unit.write_text('#define NEGATIVE_OTA_RETURN_OK 1\n'+unit.read_text().replace('#include "native_ota_http.c"','#include "terminal-return-ok.inc"'))
            mutant_binary=directory/'terminal-return-ok'
            execute(['gcc',*flags,*['-I'+str(p) for p in includes],str(mutant_unit),str(directory/'sdk-sources/components/http_parser/http_parser.c'),'-Wl,--gc-sections','-no-pie','-pthread','-o',str(mutant_binary)],directory/'negative-build.log')
            result=subprocess.run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','15',str(mutant_binary),str(packed),str(out/'sources/tests/native/ota_integration/client.py'),str(certificate),str(temporary/'negative.img')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=25)
            (directory/'negative.log').write_bytes(result.stdout)
            assert result.returncode==1 and b'NEGATIVE_CONTROL_FAIL:' in result.stdout and b'req_delete=1 body-purge-receives=' in result.stdout and b'Sanitizer' not in result.stdout and b'Assertion' not in result.stdout,result.stdout.decode(errors='replace')
            report['variants'][target+'-'+transport]['negative_control']={'terminal_return_ESP_OK':'DETECTED_BY_ACTUAL_SDK_BODY_PURGE','result':result.stdout.decode().strip(),'exit_code':result.returncode}
    report['passed']=True
    report['scope']='Real localhost TCP HTTP and independent CA/hostname-verified OpenSSL TLS1.2 client; actual pinned/generated HTTPD parser, URI, buffered request body, response and session lifecycle; actual shared OTA sink/form/HTTP and target handler/reboot code; actual native transport, selected pinned ESP-TLS server code and pinned software MbedTLS for TLS profiles. Field-model SDK structs, foreground sess_process scheduling, acknowledged audio, flash/image-verifier and NVS are explicit seams. Audio-owner implementation is qualified separately; this gate validates its handler ACK/lease contract. No physical flash, target ABI/RAM/timing, whole FreeRTOS HTTPD main loop or power-loss durability claim.'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
