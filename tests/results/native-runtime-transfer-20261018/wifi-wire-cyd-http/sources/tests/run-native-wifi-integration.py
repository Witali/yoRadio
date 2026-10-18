"""Compose frozen real HTTPD parser/session and Wi-Fi owners over TCP/verified TLS.

SDK structures are a host field model. RTOS queue dispatch executes inline and
the publication-late test advances only the clock boundary. Idle/overall tests
use real monotonic time; credentials are synthetic and TLS keys remain temporary.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/native/wifi_integration'
SDK_ROOT=ROOT/'.idf' if (ROOT/'.idf').is_dir() else ROOT.parents[1]/'.idf'


def host(path):
    p=Path(path).resolve().as_posix()
    return '/mnt/'+p[0].lower()+p[2:] if sys.platform=='win32' else p


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(command,log):
    r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    log.write_bytes(r.stdout)
    if r.returncode:raise RuntimeError(r.stdout.decode(errors='replace'))
    return r.stdout


def module(path):
    s=importlib.util.spec_from_file_location('wifi_wire_extract',path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def model(header):
    replacements={
        'struct resp_hdr resp_hdrs[2]':'struct resp_hdr resp_hdrs[8]',
        'httpd_uri_t *hd_calls[2]':'httpd_uri_t *hd_calls[8]',
        'unsigned,void *,unsigned,void *);':'unsigned,void *,unsigned,TaskHandle_t *);',
        '#define ESP_ERR_INVALID_ARG 1':'#define ESP_ERR_INVALID_ARG 0x102',
        '#define ESP_ERR_INVALID_STATE 2':'#define ESP_ERR_INVALID_STATE 0x103',
        '#define ESP_ERR_INVALID_SIZE 3':'#define ESP_ERR_INVALID_SIZE 0x104',
        '#define ESP_ERR_NO_MEM 7':'#define ESP_ERR_NO_MEM 0x101',
        'typedef struct { int unused; } native_state_t;':'typedef struct { int network_mode; } native_state_t;',
    }
    for old,new in replacements.items():assert header.count(old)==1,old;header=header.replace(old,new)
    return '''#pragma once
#include <pthread.h>
#include <fcntl.h>
#include <sys/stat.h>
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
typedef pthread_mutex_t *SemaphoreHandle_t;
typedef struct {struct {uint8_t ssid[32],password[64];}sta;} wifi_config_t;
static wifi_config_t s_station_config;
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
#define CONFIG_SPIFFS_OBJ_NAME_LEN 32
#define CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES 1024
#define NATIVE_NETWORK_CLIENT 1
'''+header+'''
#define httpd_resp_sendstr(r,s) httpd_resp_send(r,s,HTTPD_RESP_USE_STRLEN)
static native_state_t *s_state=&state;
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
static SemaphoreHandle_t xSemaphoreCreateMutex(void);
static int xSemaphoreTake(SemaphoreHandle_t,unsigned);
static void xSemaphoreGive(SemaphoreHandle_t);
static uint32_t esp_random(void);
static void esp_fill_random(void *,size_t);
static FILE *mapped_open(const char *,const char *);
static int mapped_fd_open(const char *,int,int);
static int mapped_stat(const char *,struct stat *);
static int mapped_remove(const char *);
static int mapped_rename(const char *,const char *);
static esp_err_t radio_control_publish_playlist(const char *,bool (*)(const char *,const char *));
static void websocket_service_notify_playlist_changed(void);
static void observed_upload_erase(void *,size_t);
static esp_err_t httpd_req_async_handler_begin(httpd_req_t *,httpd_req_t **);
static esp_err_t httpd_req_async_handler_complete(httpd_req_t *);
static int xQueueSend(void *,const void *,unsigned);
static esp_err_t serve_static_boundary(httpd_req_t *);
static const char *web_native_page(void);
static bool web_ui_available(void);
static const char *yoradio_index_html(void);
static esp_err_t send_recovery_page(httpd_req_t *);
static const char *esp_get_idf_version(void);
static void native_state_snapshot(native_state_t *,native_state_t *);
esp_err_t httpd_resp_send(httpd_req_t *,const char *,ssize_t);
esp_err_t httpd_resp_set_status(httpd_req_t *,const char *);
esp_err_t httpd_resp_set_type(httpd_req_t *,const char *);
esp_err_t httpd_resp_send_chunk(httpd_req_t *,const char *,ssize_t);
#ifdef INTEGRATION_TLS
void native_web_transport_prepare_close(httpd_handle_t,int,bool);
#else
static void native_web_transport_prepare_close(httpd_handle_t,int,bool);
#endif
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--wifi-evidence',type=Path,required=True)
    p.add_argument('--ws-evidence',type=Path,default=ROOT/'.build/ws-integration-qualified-final')
    p.add_argument('--tls-cyd',type=Path,default=ROOT/'.build/native-tls-ota-602')
    p.add_argument('--tls-c3',type=Path,default=ROOT/'.build/native-tls-ota-611')
    p.add_argument('--crypto-cyd',type=Path,default=ROOT/'.build/native-tls-crypto-v602')
    p.add_argument('--crypto-c3',type=Path,default=ROOT/'.build/native-tls-crypto-v611')
    p.add_argument('--target',choices=['cyd','c3','both'],default='both')
    p.add_argument('--transport',choices=['plain','tls','both'],default='both')
    a=p.parse_args()
    if sys.platform=='win32':
        command=['wsl.exe','--exec','python3',host(__file__)]
        for key,value in vars(a).items():command+=['--'+key.replace('_','-'),host(value) if isinstance(value,Path) else value]
        raise SystemExit(subprocess.call(command))
    import resource
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    wifi=a.wifi_evidence.resolve();ws=a.ws_evidence.resolve()
    wr=json.loads((wifi/'report.json').read_text());sr=json.loads((ws/'report.json').read_text());assert wr['passed'] and sr['passed']
    report={'sanitizers':['ASan','UBSan'],'source_sha256':{},'variants':{},'input_report_sha256':{'wifi':digest(wifi/'report.json'),'ws':digest(ws/'report.json')}}
    files=[Path(__file__),*FIXTURE.glob('*.*'),ROOT/'tests/run-native-ota-http.py',ROOT/'idf/esp32-cyd2usb-native/main/web_static.c',ROOT/'idf/esp32c3-oled-native/main/web_service.c']
    for path in files:
        key=path.relative_to(ROOT);dest=out/'sources'/key;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes());report['source_sha256'][key.as_posix()]=digest(dest)
    shutil.copytree(wifi/'sources',out/'wifi-sources');shutil.copytree(ws/'sources',out/'ws-sources')
    extract=module(out/'sources/tests/run-native-ota-http.py')
    # The network source can acquire unrelated time hooks in parallel. Require
    # exact equality of the owner slices used, and exact full adapter sources.
    for key,value in wr['source_sha256'].items():
        if key.startswith('idf/') and key.endswith(('web_upload.c','web_wifi.c')):assert digest(ROOT/key)==value,'Stale HTTP evidence: '+key
    with tempfile.TemporaryDirectory(prefix='wifi-wire-') as ephemeral:
      tmp=Path(ephemeral);certificate=tmp/'certificate.pem';private=tmp/'private.pem';traditional=tmp/'traditional.pem'
      if a.transport!='plain':
        execute(['openssl','req','-x509','-newkey','rsa:2048','-sha256','-nodes','-keyout',str(private),'-out',str(certificate),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost','-addext','basicConstraints=critical,CA:TRUE'],tmp/'credential.log')
        private.chmod(0o600);execute(['openssl','pkey','-in',str(private),'-traditional','-out',str(traditional)],tmp/'container.log');traditional.chmod(0o600)
      for target,tls,cache in [('cyd',a.tls_cyd,a.crypto_cyd),('c3',a.tls_c3,a.crypto_c3)]:
        if a.target not in ['both',target]:continue
        for transport in ['plain','tls']:
          if a.transport not in ['both',transport]:continue
          d=out/(target+'-'+transport);d.mkdir();shutil.copytree(ws/target/'sdk-sources',d/'sdk-sources')
          for path in (ws/target).glob('*.inc'):
            if '-original' not in path.name and path.name!='application.inc':shutil.copyfile(path,d/path.name)
          if transport=='plain':shutil.copytree(ws/target/'mbedtls',d/'mbedtls')
          for name in ['reboot.inc','network.inc','target.inc','upload.inc','web_wifi.h','websocket_service.h' if target=='c3' else 'web_reboot.h']:
            shutil.copyfile(wifi/target/name,d/name)
          shutil.copyfile(out/'wifi-sources/idf'/('esp32c3-oled-native' if target=='c3' else 'esp32-cyd2usb-native')/'main/web_upload.h',d/'web_upload.h')
          shutil.copyfile(out/'wifi-sources/idf'/('esp32c3-oled-native' if target=='c3' else 'esp32-cyd2usb-native')/'main/network_service.h',d/'network_service.h')
          component=out/'wifi-sources/idf/components/native_wifi_store'
          (d/'model.h').write_text(model((out/'ws-sources/tests/native/ws_integration/platform.h').read_text()))
          for name in ['esp_err.h','esp_http_server.h','esp_timer.h','esp_system.h','deep_sleep_clock.h','display_settings.h','native_web_transport.h','freertos/FreeRTOS.h','freertos/task.h','freertos/semphr.h','lwip/sockets.h']:
            path=d/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('#pragma once\n#include "model.h"\n')
          (d/'native_state.h').write_text('#pragma once\n#include "model.h"\n')
          txrx=(wifi/target/'sdk-sources/components/esp_http_server/src/httpd_txrx.c').read_text()
          (d/'sdk-response.inc').write_text(extract.selected(txrx,['httpd_send_all','httpd_resp_set_hdr','httpd_resp_set_status','httpd_resp_set_type','httpd_resp_send','httpd_resp_send_chunk']))
          static=(out/'sources/idf/esp32c3-oled-native/main/web_service.c' if target=='c3' else out/'sources/idf/esp32-cyd2usb-native/main/web_static.c').read_text()
          names=['content_type','finish_static_response','embedded_script_size','send_static_file','serve_static_request','static_handler','with_awake_request','sleep_guarded_upload_handler','sleep_guarded_webboard_upload_handler','sleep_guarded_recovery_wifi_handler'] if target=='c3' else ['content_type','open_nonempty','serve_static','web_static_handler']
          prefix='static void *s_static_request_queue=(void *)1;\n' if target=='c3' else 'static void *s_requests=(void *)1;static atomic_bool s_static_active;\n'
          raw=extract.selected(static,names)
          if target=='cyd':raw=raw.replace('s_active','s_static_active');prefix+='static void complete_static(httpd_req_t *r) {(void)r;}\n'
          else:prefix+='static FILE *open_nonempty_file(const char *path) {return web_upload_open_file(path);}\nconst uint8_t embedded_script_stub_start[1] asm("_binary_native_script_js_gz_start")={0};\nconst uint8_t embedded_script_stub_end[1] asm("_binary_native_script_js_gz_end")={0};\n'
          suffix='\nstatic esp_err_t serve_static_boundary(httpd_req_t *r) {return '+('serve_static_request' if target=='c3' else 'serve_static')+'(r);}\nstatic esp_err_t static_admission_boundary(httpd_req_t *r) {return '+('static_handler' if target=='c3' else 'web_static_handler')+'(r);}\nstatic void static_activate_boundary(void) {'+('' if target=='c3' else 'atomic_store(&s_static_active,true);')+'}\n'
          (d/'static.inc').write_text(prefix+raw+suffix)
          unit=d/'integration.c';unit.write_text(('#define TARGET_C3 1\n' if target=='c3' else '')+('#define INTEGRATION_TLS 1\n' if transport=='tls' else '')+'''#include "model.h"
'''+('''#include "psa/crypto.h"
#include "mbedtls/base64.h"
''' if transport=='tls' else '#include "crypto.inc"\n')+'''#include "native_httpd_headers.h"
#include "web_wifi.h"
#include "'''+('websocket_service.h' if target=='c3' else 'web_reboot.h')+'''"
#include "native_wifi_file.h"
#include "native_wifi_json.h"
#include "native_wifi_http.h"
#include "native_wifi_request_io.h"
#include "web_file_form.h"
#include "web_upload.h"
#include "network_service.h"
#include "platform-declarations.h"
#include "platform.c"
#include "reboot.inc"
#include "sdk-ws.inc"
#define httpd_req_recv sdk_req_recv
#include "sdk-txrx.inc"
#undef httpd_req_recv
int httpd_req_recv(httpd_req_t *r,char *data,size_t size) {if(request_deletes&&!workspace)++purge_receives;return sdk_req_recv(r,data,size);}
#define malloc response_malloc
#include "sdk-response.inc"
#undef malloc
#define httpd_req_delete sdk_req_delete
#include "sdk-parse.inc"
#undef httpd_req_delete
esp_err_t httpd_req_delete(struct httpd_data *hd) {++request_deletes;return sdk_req_delete(hd);}
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#define stat(...) mapped_stat(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define rename(...) mapped_rename(__VA_ARGS__)
#include "file_transaction.c"
#define fopen(...) mapped_open(__VA_ARGS__)
#include "native_wifi_store.c"
#include "native_wifi_file.c"
#include "network.inc"
#undef fopen
#undef rename
#undef remove
#undef stat
#include "native_wifi_json.c"
#define calloc workspace_calloc
#define free workspace_free
#define native_web_transport_prepare_close observed_prepare_close
#include "native_wifi_request_io.c"
#include "native_wifi_http.c"
#undef native_web_transport_prepare_close
#undef free
#undef calloc
#include "target.inc"
#define fopen(...) mapped_open(__VA_ARGS__)
#define open(...) mapped_fd_open(__VA_ARGS__)
#define remove(...) mapped_remove(__VA_ARGS__)
#define native_wifi_erase observed_upload_erase
#include "upload.inc"
#undef native_wifi_erase
#undef remove
#undef open
#undef fopen
#include "native_wifi_public.h"
#include "static.inc"
#include "test.c"
''')
          (d/'platform-declarations.h').write_text('')
          includes=[d,out/'sources/tests/native/wifi_integration',out/'ws-sources/idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455',out/'ws-sources/idf/components/native_stream/include',out/'wifi-sources/idf/components/native_storage',out/'wifi-sources/idf/components/native_storage/include',component,component/'include',d/'sdk-sources/components/http_parser']
          flags=['-std=gnu11','-D_GNU_SOURCE','-include','stdint.h','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-Wno-misleading-indentation','-Wno-sign-compare','-Wno-format','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-ffunction-sections','-fdata-sections'];extra=[];tr=None
          if transport=='tls':
            tls=tls.resolve();cache=cache.resolve();tr=json.loads((tls/'report.json').read_text());assert tr['passed'] and tr['crypto_fingerprint']==json.loads((cache/'identity.json').read_text())['fingerprint']
            shutil.copytree(tls/'sources',d/'tls-sources')
            for name in ['sdk-functions.inc','transport-production.inc','esp_err.h','sdk-tls-errors.h']:shutil.copyfile(tls/name,d/name)
            if (tls/'sdk-key-config.h').is_file():shutil.copyfile(tls/'sdk-key-config.h',d/'sdk-key-config.h');flags.append('-DHOST_ESP_TLS_UNIFIED_KEYS=1')
            prefix=(d/'tls-sources/tests/native/native_web_transport/esp_tls_host.c').read_text();prefix=prefix[:prefix.index('static uint8_t *read_ephemeral')];first=prefix.index('static struct {int socket;');last=prefix.index('static uint8_t *nvs_blob;')
            externs='''void *httpd_sess_get_transport_ctx(httpd_handle_t,int);
void httpd_sess_set_transport_ctx(httpd_handle_t,int,void *,void (*)(void *));
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_sess_set_pending_override(httpd_handle_t,int,httpd_pending_func_t);
'''
            (d/'backend.c').write_text(prefix[:first]+externs+prefix[last:]+'\n'+(out/'ws-sources/tests/native/ws_integration/tls_backend.c').read_text())
            sdk=SDK_ROOT/tr['sdk'];mbed=sdk/'components/mbedtls/mbedtls';crypto=mbed/'tf-psa-crypto'
            includes += [cache/'host-config',sdk/'components/mbedtls/port/include',mbed/'include',mbed/'library',*[crypto/name for name in ['include','core','dispatch','utilities','extras','platform','drivers/builtin/include','drivers/builtin/src','drivers/everest/include','drivers/everest/include/tf-psa-crypto/private/everest','drivers/everest/include/tf-psa-crypto/private/everest/kremlib','drivers/p256-m/p256-m/include','drivers/p256-m/p256-m/include/p256-m','drivers/p256-m/p256-m_driver_interface','drivers/pqcp/include','drivers/pqcp/src','drivers/pqcp/mldsa-native/mldsa']]]
            extra=[str(d/'backend.c'),str(cache/'libpinned-mbedtls.a')]
          execute(['gcc',*flags,*['-I'+str(x) for x in includes],str(unit),str(d/'sdk-sources/components/http_parser/http_parser.c'),*extra,'-Wl,--gc-sections','-no-pie','-pthread','-o',str(d/'integration')],d/'build.log')
          packed=tmp/(target+'.ntls')
          if transport=='tls':execute(['python3',str(d/'tls-sources/idf/components/native_web_transport/tools/pack_tls_bundle.py'),'--certificate',str(certificate),'--key',str(traditional),'--output',str(packed)],d/'packer.log')
          log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','120',str(d/'integration'),str(packed),str(out/'sources/tests/native/wifi_integration/client.py'),str(certificate)],d/'test.log')
          print(target+'-'+transport+': '+log.decode().strip(),flush=True)
          report['variants'][target+'-'+transport]={'passed':True,'result':log.decode().strip(),'wifi_source_sha256':wr['source_sha256'],'sdk_overlay':sr['variants'][target]['overlay'],'sdk_sha256':sr['variants'][target]['sdk_sha256'],'composed_sha256':{x.name:digest(x) for x in d.glob('*.inc')},'generated_model_sha256':digest(d/'model.h')}
          if tr:report['variants'][target+'-'+transport].update(tls_report_sha256=digest(tls/'report.json'),crypto_archive_sha256=digest(cache/'libpinned-mbedtls.a'),tls_source_sha256=tr['source_sha256'])
          if target=='cyd' and transport=='plain':
            raw=(component/'native_wifi_http.c').read_text();old='config->finish(config->context, committed);\n    return ESP_FAIL;'
            assert raw.count(old)==1
            (d/'terminal-return-ok.inc').write_text(raw.replace(old,'config->finish(config->context, committed);\n    return ESP_OK;'))
            mutant=d/'terminal-return-ok.c';mutant.write_text('#define NEGATIVE_WIFI_RETURN_OK 1\n'+unit.read_text().replace('#include "native_wifi_http.c"','#include "terminal-return-ok.inc"'))
            execute(['gcc',*flags,*['-I'+str(x) for x in includes],str(mutant),str(d/'sdk-sources/components/http_parser/http_parser.c'),'-Wl,--gc-sections','-no-pie','-pthread','-o',str(d/'terminal-return-ok')],d/'negative-build.log')
            r=subprocess.run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','15',str(d/'terminal-return-ok'),str(packed),str(out/'sources/tests/native/wifi_integration/client.py'),str(certificate)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=25)
            (d/'negative.log').write_bytes(r.stdout)
            assert r.returncode==1 and b'NEGATIVE_CONTROL_FAIL:' in r.stdout and b'req_delete=1 body-purge-receives=' in r.stdout and b'Sanitizer' not in r.stdout and b'Assertion' not in r.stdout,r.stdout.decode(errors='replace')
            report['variants'][target+'-'+transport]['negative_control']={'terminal_return_ESP_OK':'DETECTED_BY_ACTUAL_SDK_BODY_PURGE','result':r.stdout.decode().strip(),'exit_code':r.returncode}
    report['passed']=True
    report['scope']='Real localhost TCP and CA/hostname-verified OpenSSL TLS1.2 client, frozen pinned HTTPD parser/URI/pending-body/response/session, actual Wi-Fi owner/JSON/HTTP/request I/O/target adapters/reboot reservations and full legacy import handlers; exact static admission and worker bodies (CYD private activation variable renamed to avoid single-TU collision). Native TLS uses actual transport, selected pinned ESP-TLS and pinned software MbedTLS. Host field layouts, foreground sess_process, inline async/static queue, NVS transport provision and synthetic host filesystem with SPIFFS rename rule are explicit seams. Publication-late advances clock only after durable host rename; idle/overall tests use real time. No target RAM/ABI/RTOS scheduling, actual SPIFFS/power-loss, radio reconnect, or hardware TLS claim.'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
