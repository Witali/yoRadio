"""Actual CYD time HTTP/parser/session/settings over TCP and verified TLS.

Uses the qualified pinned HTTPD extraction/overlay and native ESP-TLS host
backend. Server scheduling is foreground sess_process; SDK struct layout,
FreeRTOS locks, NVS and time_service snapshots are explicit host seams.
The pinned parser requires one body byte before dispatch; huge/slow cases
leave 1 MiB-1 bytes unsent after that byte. Handler deadlines do not include
the SDK's pre-dispatch receive wait. Raw TCP may reset after a full rejection
response when closing with unread input; TLS requires proper close_notify.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SDK_ROOT=ROOT/'.idf' if (ROOT/'.idf').is_dir() else ROOT.parents[1]/'.idf'
FIXTURE=ROOT/'tests/native/cyd_time_integration'

def host(path):
    path=Path(path).resolve().as_posix()
    return '/mnt/'+path[0].lower()+path[2:] if sys.platform=='win32' else path
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def module(path):
    spec=importlib.util.spec_from_file_location('time_wire_extract',path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
def run(command,log):
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120);log.write_bytes(result.stdout)
    if result.returncode:raise RuntimeError(result.stdout.decode(errors='replace'))
    return result.stdout
def model(source):
    replacements={
        'struct resp_hdr resp_hdrs[2]':'struct resp_hdr resp_hdrs[8]',
        '#define ESP_ERR_INVALID_ARG 1':'#define ESP_ERR_INVALID_ARG 0x102',
        '#define ESP_ERR_INVALID_STATE 2':'#define ESP_ERR_INVALID_STATE 0x103',
        '#define ESP_ERR_INVALID_SIZE 3':'#define ESP_ERR_INVALID_SIZE 0x104',
        '#define ESP_ERR_NO_MEM 7':'#define ESP_ERR_NO_MEM 0x101',
        'httpd_uri_t *hd_calls[2]; int http_server_state; unsigned hd_sd_active_count; uint64_t lru_counter; };':
            'httpd_uri_t *hd_calls[2]; int http_server_state; unsigned hd_sd_active_count; uint64_t lru_counter; esp_err_t (*err_handler_fns[506])(httpd_req_t *,httpd_err_code_t); };',
    }
    for old,new in replacements.items():assert source.count(old)==1,old;source=source.replace(old,new)
    return '#pragma once\n'+source+'''
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_HTTPD_RESP_HDR 0x602
#define ESP_ERR_HTTPD_RESP_SEND 0x604
#define HTTPD_RESP_USE_STRLEN (-1)
#define HTTP_SERVER_EVENT_HEADERS_SENT 4
#define HTTP_SERVER_EVENT_SENT_DATA 5
#define HTTP_SERVER_EVENT_ERROR 6
#define HTTPD_401_UNAUTHORIZED 401
#define HTTPD_403_FORBIDDEN 403
#define HTTPD_411_LENGTH_REQUIRED 411
#define httpd_resp_sendstr(r,s) httpd_resp_send(r,s,HTTPD_RESP_USE_STRLEN)
void native_web_transport_prepare_close(httpd_handle_t,int,bool);
'''

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--ws-evidence',type=Path,default=ROOT/'.build/ws-integration-qualified-final')
    parser.add_argument('--tls-evidence',type=Path,default=ROOT/'.build/native-tls-ota-602')
    parser.add_argument('--crypto',type=Path,default=ROOT/'.build/native-tls-crypto-v602')
    parser.add_argument('--sdk',type=Path,default=SDK_ROOT/'v6.0.2')
    args=parser.parse_args()
    if sys.platform=='win32':
        command=['wsl.exe','--exec','python3',host(__file__)]
        for key,value in vars(args).items():command+=['--'+key.replace('_','-'),host(value)]
        raise SystemExit(subprocess.call(command))
    import resource
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);ws=args.ws_evidence.resolve();tls=args.tls_evidence.resolve();cache=args.crypto.resolve();sdk=args.sdk.resolve()
    ws_report=json.loads((ws/'report.json').read_text());tls_report=json.loads((tls/'report.json').read_text())
    assert ws_report['passed'] and tls_report['passed'] and tls_report['sdk']=='v6.0.2'
    assert tls_report['crypto_fingerprint']==json.loads((cache/'identity.json').read_text())['fingerprint']
    mainpath=ROOT/'idf/esp32-cyd2usb-native/main'
    files=[Path(__file__),*FIXTURE.glob('*.*'),ROOT/'tests/run-native-ota-http.py',
        ROOT/'tests/native/ws_integration/platform.h',ROOT/'tests/native/native_web_transport/esp_tls_host.c',
        *[mainpath/name for name in ['web_time.c','web_time.h','time_settings.c','time_settings.h','time_service.h']],
        ROOT/'idf/components/native_time/include/native_time_sntp.h',ROOT/'idf/components/native_stream/include/json_buffer.h',
        ROOT/'idf/components/native_stream/include/websocket_message.h',
        *[mainpath/'compat/httpd_rfc6455'/name for name in ['native_httpd_headers.h']],
        *[ROOT/'idf/components/native_web_transport'/name for name in ['native_web_transport.c','include/native_web_transport.h','tools/pack_tls_bundle.py']]]
    hashes={}
    for path in files:
        relative=path.relative_to(ROOT);target=out/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes());hashes[relative.as_posix()]=digest(target)
    frozen=out/'sources';extract=module(frozen/'tests/run-native-ota-http.py')
    # Only qualified foundation units are reused, with exact pinned inputs and
    # the current tracked private-header helper. No old application body enters.
    for relative,expected in ws_report['variants']['cyd']['sdk_sha256'].items():
        assert digest(sdk/relative)==expected,relative
    assert digest(frozen/'tests/native/ws_integration/platform.h')==ws_report['source_sha256']['tests/native/ws_integration/platform.h']
    assert digest(frozen/'idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455/native_httpd_headers.h')==ws_report['source_sha256']['idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455/native_httpd_headers.h']
    for relative,expected in tls_report['source_sha256'].items():
        if relative.startswith('idf/components/native_web_transport/') or relative=='tests/native/native_web_transport/esp_tls_host.c':assert digest(ROOT/relative)==expected,relative
        elif relative.startswith('sdk/'):assert digest(sdk/relative[4:])==expected,relative
    shutil.copyfile(ws/'report.json',out/'httpd-foundation-report.json');shutil.copyfile(tls/'report.json',out/'tls-foundation-report.json');shutil.copyfile(cache/'identity.json',out/'crypto-identity.json')
    report={'passed':False,'scope':__doc__,'physical_hardware':False,'sanitizers':['ASan','UBSan'],'source_sha256':hashes,
        'httpd_foundation_report_sha256':digest(ws/'report.json'),'tls_foundation_report_sha256':digest(tls/'report.json'),
        'sdk_sha256':ws_report['variants']['cyd']['sdk_sha256'],'sdk_overlay':ws_report['variants']['cyd']['overlay'],
        'tls_source_sha256':tls_report['source_sha256'],'crypto_archive_sha256':digest(cache/'libpinned-mbedtls.a'),'variants':{}}
    directory=out/'composed';directory.mkdir();shutil.copytree(ws/'cyd/sdk-sources',directory/'sdk-sources')
    shutil.copytree(cache/'host-config',directory/'crypto-config')
    report['crypto_config_sha256']={p.relative_to(directory/'crypto-config').as_posix():digest(p) for p in (directory/'crypto-config').rglob('*') if p.is_file()}
    for name in ['sdk-ws.inc','sdk-txrx.inc','sdk-parse.inc','sdk-sess.inc','sdk-uri.inc']:
        shutil.copyfile(ws/'cyd'/name,directory/name)
    for name in ['httpd_ws.c','httpd_parse.c']:
        assert digest(ws/'cyd/generated'/name)==ws_report['variants']['cyd']['overlay']['generated_sha256'][name],name
    txrx=(sdk/'components/esp_http_server/src/httpd_txrx.c').read_text();parse=(sdk/'components/esp_http_server/src/httpd_parse.c').read_text()
    (directory/'sdk-response.inc').write_text(extract.selected(txrx,['httpd_send_all','httpd_resp_set_hdr','httpd_resp_set_status','httpd_resp_set_type','httpd_resp_send','httpd_resp_send_err','httpd_resp_send_custom_err','httpd_req_handle_err']))
    (directory/'sdk-default-io.inc').write_text(extract.selected(txrx,['httpd_sock_err','httpd_default_send','httpd_default_recv']))
    (directory/'sdk-query.inc').write_text(extract.selected(parse,['httpd_req_get_url_query_len','httpd_req_get_url_query_str']))
    (directory/'model.h').write_text(model((frozen/'tests/native/ws_integration/platform.h').read_text()))
    for name in ['esp_err.h','esp_http_server.h','freertos/FreeRTOS.h','freertos/semphr.h','nvs.h','native_web_transport.h']:
        path=directory/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('#pragma once\n#include "model.h"\n')
    for name in ['sdk-functions.inc','transport-production.inc','sdk-tls-errors.h']:
        shutil.copyfile(tls/name,directory/name)
    # TLS code owns its own public-config field model; do not let its esp_err.h
    # include the HTTPD model from this translation unit.
    backend_dir=directory/'tls';backend_dir.mkdir()
    for name in ['sdk-functions.inc','transport-production.inc','sdk-tls-errors.h','esp_err.h']:
        shutil.copyfile(tls/name,backend_dir/name)
    prefix=(frozen/'tests/native/native_web_transport/esp_tls_host.c').read_text();prefix=prefix[:prefix.index('static uint8_t *read_ephemeral')]
    first=prefix.index('static struct {int socket;');last=prefix.index('static uint8_t *nvs_blob;')
    externs='''void *httpd_sess_get_transport_ctx(httpd_handle_t,int);
void httpd_sess_set_transport_ctx(httpd_handle_t,int,void *,void (*)(void *));
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_sess_set_pending_override(httpd_handle_t,int,httpd_pending_func_t);
'''
    (backend_dir/'backend.c').write_text(prefix[:first]+externs+prefix[last:]+'\n'+(frozen/'tests/native/cyd_time_integration/backend.c').read_text())
    unit=directory/'integration.c';unit.write_text('''#define INTEGRATION_TLS 1
#include "model.h"
#include "psa/crypto.h"
#include "mbedtls/base64.h"
#include "native_httpd_headers.h"
#include "time_service.h"
#include "web_time.h"
#include "platform.c"
#include "sdk-ws.inc"
#define httpd_req_recv sdk_req_recv
#include "sdk-txrx.inc"
#undef httpd_req_recv
int httpd_req_recv(httpd_req_t *r,char *data,size_t n) {int count=sdk_req_recv(r,data,n);if(in_purge){++purge_calls;if(count>0)purge_positive_bytes+=(unsigned)count;}return count;}
#include "sdk-response.inc"
#include "sdk-default-io.inc"
#define httpd_req_delete sdk_req_delete
#include "sdk-parse.inc"
#undef httpd_req_delete
esp_err_t httpd_req_delete(struct httpd_data *hd) {++request_deletes;in_purge=true;esp_err_t result=sdk_req_delete(hd);in_purge=false;return result;}
#include "sdk-query.inc"
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#include "time_settings.c"
#define native_web_transport_prepare_close observed_prepare_close
#include "web_time.c"
#undef native_web_transport_prepare_close
#include "test.c"
''')
    mbed=sdk/'components/mbedtls/mbedtls';crypto=mbed/'tf-psa-crypto'
    includes=[directory,frozen/'tests/native/cyd_time_integration',frozen/'idf/esp32-cyd2usb-native/main',
        frozen/'idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455',frozen/'idf/components/native_stream/include',frozen/'idf/components/native_time/include',
        directory/'sdk-sources/components/http_parser',directory/'crypto-config',sdk/'components/mbedtls/port/include',mbed/'include',mbed/'library',
        *[crypto/name for name in ['include','core','dispatch','utilities','extras','platform','drivers/builtin/include','drivers/builtin/src','drivers/everest/include','drivers/everest/include/tf-psa-crypto/private/everest','drivers/everest/include/tf-psa-crypto/private/everest/kremlib','drivers/p256-m/p256-m/include','drivers/p256-m/p256-m/include/p256-m','drivers/p256-m/p256-m_driver_interface','drivers/pqcp/include','drivers/pqcp/src','drivers/pqcp/mldsa-native/mldsa']]]
    flags=['-std=c11','-D_GNU_SOURCE','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-Wno-misleading-indentation','-Wno-sign-compare','-Wno-format','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-ffunction-sections','-fdata-sections']
    def build(unit,binary,log):
        command=['gcc',*flags,*['-I'+str(p) for p in includes],str(unit),str(directory/'sdk-sources/components/http_parser/http_parser.c'),str(backend_dir/'backend.c'),str(cache/'libpinned-mbedtls.a'),'-Wl,--gc-sections','-no-pie','-pthread','-o',str(binary)]
        run(command,log);return command
    binary=directory/'integration';report['build_command']=build(unit,binary,directory/'build.log')
    with tempfile.TemporaryDirectory(prefix='cyd-time-wire-') as ephemeral:
        temporary=Path(ephemeral);certificate=temporary/'certificate.pem';private=temporary/'private.pem';traditional=temporary/'traditional.pem';packed=temporary/'identity.ntls'
        run(['openssl','req','-x509','-newkey','rsa:2048','-sha256','-nodes','-keyout',str(private),'-out',str(certificate),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost','-addext','basicConstraints=critical,CA:TRUE'],temporary/'credential.log');os.chmod(private,0o600)
        run(['openssl','pkey','-in',str(private),'-traditional','-out',str(traditional)],temporary/'container.log');os.chmod(traditional,0o600)
        run(['python3',str(frozen/'idf/components/native_web_transport/tools/pack_tls_bundle.py'),'--certificate',str(certificate),'--key',str(traditional),'--output',str(packed)],out/'packer.log')
        for mode in ['plain','tls']:
            command=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',str(binary),str(packed),str(frozen/'tests/native/cyd_time_integration/client.py'),str(certificate),mode]
            log=run(command,out/(mode+'.log'));assert b'23 actual TCP' in log
            report['variants'][mode]={'passed':True,'positive_groups':23,'result':log.decode().strip()}
        source=(frozen/'idf/esp32-cyd2usb-native/main/web_time.c').read_text();old='    return ESP_FAIL;\n}\n\nstatic int hex_value';assert source.count(old)==1
        mutant=directory/'web-time-return-ok.inc';mutant.write_text(source.replace(old,'    return ESP_OK;\n}\n\nstatic int hex_value'))
        mutant_unit=directory/'negative.c';mutant_unit.write_text('#define NEGATIVE_TIME_RETURN_OK 1\n'+unit.read_text().replace('#include "web_time.c"','#include "web-time-return-ok.inc"'))
        bad=directory/'negative';report['negative_build_command']=build(mutant_unit,bad,directory/'negative-build.log')
        for mode in ['plain','tls']:
            command=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',str(bad),str(packed),str(frozen/'tests/native/cyd_time_integration/client.py'),str(certificate),mode]
            result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30);(out/(mode+'-negative.log')).write_bytes(result.stdout)
            assert result.returncode==1 and b'NEGATIVE_CONTROL_FAIL:' in result.stdout and b'req_delete=1 purge_calls=1 purge_bytes=1' in result.stdout,(mode,result.stdout)
            assert b'Sanitizer' not in result.stdout and b'Assertion' not in result.stdout and b'Traceback' not in result.stdout,result.stdout
            report['variants'][mode]['negative_control']={'terminal_return_ESP_OK':'DETECTED_BY_ACTUAL_SDK_ONE_BYTE_PURGE','status':result.returncode,'result':result.stdout.decode().strip()}
    report['generated_sha256']={p.relative_to(directory).as_posix():digest(p) for p in directory.rglob('*') if p.is_file() and p.suffix in ('.c','.h','.inc')}
    report['source_files_still_match_snapshot']=all(digest(ROOT/key)==value for key,value in hashes.items());assert report['source_files_still_match_snapshot']
    report['passed']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS CYD time wire: 46 TCP/TLS groups + 2 exact actual-SDK purge controls; ASan/UBSan')
if __name__=='__main__':main()
