"""Actual generated HTTPD/parser/lifecycle and application WS handlers over TCP.

Only NEW integration fixtures are maintained here. Source bodies are extracted
unchanged from a frozen snapshot; the JSON report states all excluded seams.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/native/ws_integration'
COMPAT = ROOT / 'idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455'
SDK_ROOT=ROOT/'.idf' if (ROOT/'.idf').is_dir() else ROOT.parents[1]/'.idf'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--sdk-cyd', type=Path, default=SDK_ROOT / 'v6.0.2')
    parser.add_argument('--sdk-c3', type=Path, default=SDK_ROOT / 'v6.1-9a97f6c54ec6')
    parser.add_argument('--target',choices=['cyd','c3','both'],default='both')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = [Path(__file__), *FIXTURE.glob('*.*'), COMPAT/'apply.py', COMPAT/'native_httpd_headers.h',
               COMPAT/'test_host.c', COMPAT/'test_host.py',
               ROOT/'idf/esp32-cyd2usb-native/main/websocket_service.c',
               ROOT/'idf/esp32c3-oled-native/main/websocket_service.c',
               ROOT/'idf/components/native_stream/include/websocket_message.h',
               ROOT/'idf/components/native_stream/include/json_buffer.h',
               ROOT/'idf/components/native_web_transport/include/native_web_transport.h']
    hashes = {}
    for path in sources:
        raw = path.read_bytes()
        key = path.relative_to(ROOT).as_posix()
        dest = out/'sources'/key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        hashes[key] = hashlib.sha256(raw).hexdigest()
    overlay = module(out/'sources'/COMPAT.relative_to(ROOT)/'apply.py', 'overlay_snapshot')
    helper = module(out/'sources'/COMPAT.relative_to(ROOT)/'test_host.py', 'host_snapshot')
    # test_host.py's discovery path is unsuitable inside our snapshot; its
    # functions() still uses its own identical pinned overlay implementation.
    report = {'source_sha256': hashes, 'variants': {}, 'sanitizers': ['ASan', 'UBSan']}

    def selected(text, names):
        spans=[]
        for name in names:
            match=re.search(r'^(?:(?:static|inline|const|volatile)[ \t]+)*[A-Za-z_]\w*[ \t*]+'
                            +name+r'\([^;{}]*?\)\s*\{',text,re.M)
            assert match,name
            brace=text.index('{',match.start());end=brace+1;depth=1
            while depth:
                depth+=(text[end]=='{')-(text[end]=='}');end+=1
            spans.append((match.start(),end))
        return '\n'.join(text[a:b] for a,b in sorted(spans))+'\n'

    def ws_functions(ws,parse):
        contents=helper.functions(ws,parse)
        cleanup=selected(parse,['httpd_req_cleanup']).strip()
        return contents[:contents.index(cleanup)]+selected(ws,['httpd_ws_get_fd_info'])

    def parse_functions(parse):
        begin=parse.index('typedef struct {')
        _,end=overlay.function_span(parse,'httpd_req_delete')
        names=['httpd_req_get_hdr_value_len','httpd_req_get_hdr_value_str']
        if 'static const char *httpd_find_hdr_value' in parse:
            names[0:0]=['httpd_next_hdr','httpd_find_hdr_value']
        return parse[begin:end]+'\n'+selected(parse,names)

    for target, sdk in [('cyd', args.sdk_cyd), ('c3', args.sdk_c3)]:
        if args.target!='both' and args.target!=target:continue
        directory = out/target
        directory.mkdir()
        sdkfiles = ['components/esp_http_server/src/'+name for name in
                    ['httpd_ws.c','httpd_parse.c','httpd_sess.c','httpd_txrx.c','httpd_uri.c','esp_httpd_priv.h']]
        sdkfiles += ['components/esp_http_server/include/esp_http_server.h',
                     'components/http_parser/http_parser.c', 'components/http_parser/http_parser.h',
                     'components/mbedtls/mbedtls/tf-psa-crypto/utilities/base64.c']
        sdkhashes = {}
        for key in sdkfiles:
            raw=(sdk/key).read_bytes()
            destination=directory/'sdk-sources'/key
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(raw)
            sdkhashes[key]=hashlib.sha256(raw).hexdigest()
        generated=directory/'generated'
        generated.mkdir()
        generation=overlay.generate(sdk,generated)
        ws=(generated/'httpd_ws.c').read_text(encoding='utf-8')
        parse=(generated/'httpd_parse.c').read_text(encoding='utf-8')
        sdkroot=directory/'sdk-sources/components/esp_http_server/src'
        sess=(sdkroot/'httpd_sess.c').read_text(encoding='utf-8')
        txrx=(sdkroot/'httpd_txrx.c').read_text(encoding='utf-8')
        uri=(sdkroot/'httpd_uri.c').read_text(encoding='utf-8')
        (directory/'sdk-ws.inc').write_text(ws_functions(ws,parse),encoding='utf-8')
        (directory/'sdk-parse.inc').write_text(parse_functions(parse),encoding='utf-8')
        (directory/'sdk-txrx.inc').write_text(selected(txrx,[
            'httpd_sess_set_send_override','httpd_sess_set_recv_override','httpd_sess_set_pending_override','httpd_send',
            'httpd_recv_pending','httpd_recv_with_opt','httpd_recv','httpd_unrecv','httpd_req_recv','httpd_req_to_sockfd']),encoding='utf-8')
        (directory/'sdk-sess.inc').write_text(selected(sess,[
            'httpd_sess_free_ctx','httpd_sess_clear_ctx','httpd_sess_get_ctx','httpd_sess_set_ctx',
            'httpd_sess_get_transport_ctx','httpd_sess_set_transport_ctx',
            'httpd_sess_delete','httpd_sess_process']),encoding='utf-8')
        (directory/'sdk-uri.inc').write_text(selected(uri,[
            'httpd_uri_match_simple','httpd_find_uri_handler','httpd_register_uri_handler',
            'httpd_unregister_all_uri_handlers','httpd_uri']),encoding='utf-8')
        apppath=Path('idf')/('esp32c3-oled-native' if target=='c3' else 'esp32-cyd2usb-native')/'main/websocket_service.c'
        app=(out/'sources'/apppath).read_text(encoding='utf-8')
        if target=='c3':
            prefix=app[app.index('#define WS_STATUS_POLL_MS'):app.index('static void ws_update_active')]
            names=['ws_update_active','ws_session_free','ws_session','ws_wait','ws_send_complete',
                   'ws_receive_complete','ws_finish_client','ws_fail_client','websocket_pre_handshake',
                   'websocket_post_handshake','ws_send_control','ws_close_client','ws_send_request',
                   'websocket_handler_awake','websocket_handler','websocket_service_register']
        else:
            prefix=app[app.index('#define WS_CLIENT_LIMIT'):app.index('static void session_free')]
            # The command dispatcher seam records exact complete text, while
            # production SDK/session/receive/control/message code stays intact.
            prefix+='\nstatic esp_err_t handle_command(ws_client_t *,char *);\nstatic esp_err_t send_status(ws_client_t *,bool);\n'
            names=['session_free','current_client','send_complete_frame_bytes','receive_complete_frame_bytes',
                   'fail_client','find_client','send_text','send_control','close_with_code','receive_and_handle',
                   'websocket_handler','websocket_handshake_transport','websocket_service_register']
        (directory/'application.inc').write_text(prefix+selected(app,names),encoding='utf-8')
        # Reuse the documented SHA sample seam, not an independently copied
        # handshake algorithm. Base64 is the actual snapshotted SDK C.
        fixture=(out/'sources'/COMPAT.relative_to(ROOT)/'test_host.c').read_text(encoding='utf-8')
        crypto=fixture[fixture.index('/* SDK SHA implementation'):fixture.index('#include "native_httpd_headers.h"')]
        (directory/'crypto.inc').write_text(crypto,encoding='utf-8')
        base64=(directory/'sdk-sources'/sdkfiles[-1]).read_text(encoding='utf-8')
        base64=re.sub(r'^#include[^\n]+\n','',base64,flags=re.M)
        base64_prefix='''#define MBEDTLS_BASE64_C 1
#define MBEDTLS_STATIC_TESTABLE static
#define MBEDTLS_ERR_BASE64_BUFFER_TOO_SMALL (-42)
#define MBEDTLS_ERR_BASE64_INVALID_CHARACTER (-44)
#define MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED (-46)
#define MBEDTLS_BYTE_0(x) ((unsigned char)((x)&255))
#define MBEDTLS_BYTE_1(x) ((unsigned char)(((x)>>8)&255))
#define MBEDTLS_BYTE_2(x) ((unsigned char)(((x)>>16)&255))
static unsigned char mbedtls_ct_uchar_in_range_if(unsigned a,unsigned b,unsigned x,unsigned result) {return x>=a && x<=b?(unsigned char)result:0;}
'''
        (directory/'sdk-base64.inc').write_text(base64_prefix+base64,encoding='utf-8')
        (directory/'mbedtls').mkdir()
        (directory/'mbedtls/base64.h').write_text('#pragma once\n',encoding='utf-8')
        unit=directory/'integration.c'
        unit.write_text(('#define TARGET_C3 1\n' if target=='c3' else '')+'''
#include "platform.h"
#include "crypto.inc"
#include "native_httpd_headers.h"
#include "sdk-ws.inc"
#include "sdk-txrx.inc"
#include "sdk-parse.inc"
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#include "application.inc"
#include "platform.c"
#include "test.c"
''',encoding='utf-8')
        binary=directory/'integration'
        includes=[directory, out/'sources'/FIXTURE.relative_to(ROOT), out/'sources'/COMPAT.relative_to(ROOT),
                  out/'sources/idf/components/native_stream/include',directory/'sdk-sources/components/http_parser']
        command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function',
                 '-Wno-unused-variable','-Wno-unused-parameter','-Wno-misleading-indentation','-Wno-sign-compare',
                 '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                 *['-I'+host(p) for p in includes],host(unit),
                 host(directory/'sdk-sources/components/http_parser/http_parser.c'),'-o',host(binary)]
        try:
            (directory/'build.log').write_bytes(run(command))
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',
                     'timeout','60',host(binary)])
            (directory/'test.log').write_bytes(log)
            print(target+': '+log.decode().strip())
        except subprocess.CalledProcessError as error:
            (directory/'failure.log').write_bytes(error.output)
            print(error.output.decode(errors='replace'),file=sys.stderr)
            raise
        report['variants'][target]={'passed':True,'result':log.decode().strip(),'sdk_sha256':sdkhashes,
                                    'overlay':generation,'extracted_functions':names}
        # Actual pinned original SDKs are the historical negative controls;
        # current application handlers/routes/platform adapters stay identical.
        original_ws=(sdkroot/'httpd_ws.c').read_text(encoding='utf-8')
        original_parse=(sdkroot/'httpd_parse.c').read_text(encoding='utf-8')
        (directory/'sdk-ws-original.inc').write_text(ws_functions(original_ws,original_parse),encoding='utf-8')
        (directory/'sdk-parse-original.inc').write_text(parse_functions(original_parse),encoding='utf-8')
        original_unit=directory/'original.c'
        original_unit.write_text(unit.read_text(encoding='utf-8').replace('"sdk-ws.inc"','"sdk-ws-original.inc"')
                                 .replace('"sdk-parse.inc"','"sdk-parse-original.inc"'),encoding='utf-8')
        original_binary=directory/'original'
        original_cmd=[host(original_unit) if item==host(unit) else host(original_binary) if item==host(binary) else item for item in command]
        try:
            (directory/'original-build.log').write_bytes(run(original_cmd))
        except subprocess.CalledProcessError as error:
            (directory/'original-failure.log').write_bytes(error.output)
            print(error.output.decode(errors='replace'),file=sys.stderr);raise
        negatives={}
        for mode in ['extensions','protocol','empty-length']:
            try:
                log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',
                         'timeout','15',host(original_binary),mode]);code=0
            except subprocess.CalledProcessError as error:
                log=error.output;code=error.returncode
            (directory/('negative-'+mode+'.log')).write_bytes(log)
            assert code==1 and b'NEGATIVE_CONTROL_FAIL:' in log and b'Sanitizer' not in log,(code,log)
            negatives[mode]={'exit_code':code,'expected_failure':True,'result':log.decode().strip()}
        report['variants'][target]['negative_controls']=negatives
    report['scope']='Actual generated SDK HTTPD HTTP/parser/request lifecycle/URI/frame code, actual application receive/control/transport/session/register functions, real localhost TCP. Field-model structs; native transport delegates to POSIX; HTTP error formatting, radio command dispatcher/status/FreeRTOS scheduling and SHA sample digest are explicit seams. No TLS, target ABI, hardware timing, whole FreeRTOS HTTPD main loop or full RFC compliance claim.'
    report['passed']=True
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
