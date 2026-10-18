"""ASan/UBSan checks of actual generated SDK functions with explicit host seams."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
spec=importlib.util.spec_from_file_location('overlay_apply',HERE/'apply.py')
overlay=importlib.util.module_from_spec(spec);spec.loader.exec_module(overlay)


def functions(source,parse):
    names=['httpd_ws_get_response_subprotocol','httpd_ws_respond_server_handshake',
           'httpd_ws_check_req','httpd_ws_is_control_opcode','httpd_ws_fail_connection',
           'httpd_ws_unmask_payload','httpd_ws_recv_frame','httpd_ws_send_frame',
           'httpd_ws_send_frame_async','httpd_ws_get_frame_type','httpd_ws_send_handshake_error',
           'httpd_ws_mark_closing','httpd_ws_recv_frame_internal']
    selected=[]
    for name in names:
        try:selected.append(overlay.function_span(source,name))
        except AssertionError:pass
    defines='\n'.join(re.findall(r'^#define (?:HTTPD_WS_|SEC_WEBSOCKET_)[^\n]+',source,re.M))+'\n'
    magic=re.search(r'^static const char ws_magic_uuid\[\][^\n]+',source,re.M).group(0)+'\n'
    contents=defines+magic+'\n'.join(source[a:b] for a,b in sorted(selected))
    contents+='\n'+'\n'.join(parse[a:b] for a,b in
                             [overlay.function_span(parse,name) for name in ['httpd_req_cleanup','httpd_req_delete']])
    return contents


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    report=overlay.generate(args.sdk,out)
    source=(out/'httpd_ws.c').read_text(encoding='utf-8');parse=(out/'httpd_parse.c').read_text(encoding='utf-8')
    (out/'generated-functions.inc').write_text(functions(source,parse),encoding='utf-8')
    (out/'mbedtls').mkdir();(out/'mbedtls/base64.h').write_text('#pragma once\n')
    base64=args.sdk/'components/mbedtls/mbedtls/tf-psa-crypto/utilities/base64.c'
    encoded=re.sub(r'^#include[^\n]+\n','',base64.read_text(encoding='utf-8'),flags=re.M)
    (out/'sdk-base64.inc').write_text('''#define MBEDTLS_BASE64_C 1
#define MBEDTLS_STATIC_TESTABLE static
#define MBEDTLS_ERR_BASE64_BUFFER_TOO_SMALL (-42)
#define MBEDTLS_ERR_BASE64_INVALID_CHARACTER (-44)
#define MBEDTLS_ERR_ERROR_CORRUPTION_DETECTED (-46)
#define MBEDTLS_BYTE_0(x) ((unsigned char)((x)&255))
#define MBEDTLS_BYTE_1(x) ((unsigned char)(((x)>>8)&255))
#define MBEDTLS_BYTE_2(x) ((unsigned char)(((x)>>16)&255))
static unsigned char mbedtls_ct_uchar_in_range_if(unsigned a,unsigned b,unsigned x,unsigned result) {return x>=a && x<=b?(unsigned char)result:0;}
'''+encoded,encoding='utf-8')
    report['function_variants']={}
    for variant in ['host','target-size-cap']:
      binary=out/('test-httpd-'+variant)
      try:
        log=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function',
                 '-Wno-misleading-indentation','-Wno-sign-compare','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                 *(['-DNATIVE_TEST_TARGET_SIZE32=1'] if variant=='target-size-cap' else []),
                 '-I'+host(out),'-I'+host(HERE),'-I'+host(args.sdk/'components/http_parser'),
                 host(HERE/'test_host.c'),host(args.sdk/'components/http_parser/http_parser.c'),'-o',host(binary)])
        (out/(variant+'-build.log')).write_bytes(log)
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)])
      except subprocess.CalledProcessError as error:
        (out/'failure.log').write_bytes(error.output);print(error.output.decode(errors='replace'));raise
      (out/(variant+'-test.log')).write_bytes(log);print(log.decode(),end='')
      report['function_variants'][variant]=log.decode().strip()
    # Real wire bytes enter the SDK parser and its own HTTPD pause/read/unrecv
    # pipeline. URI dispatch alone is a seam selecting the one /ws GET route.
    txrx_path=args.sdk/'components/esp_http_server/src/httpd_txrx.c'
    txrx=txrx_path.read_text(encoding='utf-8')
    txrx_functions='\n'.join(txrx[a:b] for a,b in
        [overlay.function_span(txrx,name) for name in ['httpd_recv_pending','httpd_recv_with_opt','httpd_unrecv']])
    report['whole_http_parser']={}
    for variant in ['baseline','current']:
        directory=out/('wire-'+variant);directory.mkdir()
        ws_source=(args.sdk/'components/esp_http_server/src/httpd_ws.c').read_text(encoding='utf-8') if variant=='baseline' else source
        parser_source=(args.sdk/'components/esp_http_server/src/httpd_parse.c').read_text(encoding='utf-8') if variant=='baseline' else parse
        (directory/'generated-functions.inc').write_text(functions(ws_source,parser_source),encoding='utf-8')
        start=parser_source.index('typedef struct {')
        _,end=overlay.function_span(parser_source,'httpd_parse_req')
        (directory/'parser-functions.inc').write_text(parser_source[start:end],encoding='utf-8')
        (directory/'txrx-functions.inc').write_text(txrx_functions,encoding='utf-8')
        wire_binary=directory/'wire-test'
        try:
            log=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function',
                     '-Wno-misleading-indentation','-Wno-sign-compare','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer',
                     '-fno-pie','-no-pie','-I'+host(directory),'-I'+host(out),'-I'+host(HERE),
                     '-I'+host(args.sdk/'components/http_parser'),host(HERE/'test_wire.c'),
                     host(args.sdk/'components/http_parser/http_parser.c'),'-o',host(wire_binary)])
            (directory/'build.log').write_bytes(log)
        except subprocess.CalledProcessError as error:
            (directory/'failure.log').write_bytes(error.output);print(error.output.decode(errors='replace'));raise
        for case in (['extensions','protocol','fold','empty-length'] if variant=='baseline' else ['all']):
            try:
                log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',
                         'timeout','60',host(wire_binary),*([case] if variant=='baseline' else [])]);success=True
            except subprocess.CalledProcessError as error:
                log=error.output;success=False
            (directory/(case+'.log')).write_bytes(log)
            if variant=='baseline':
                expected=b'SDK parser truncated folded field' if case=='fold' else b'wire mismatch'
                assert not success and expected in log,log.decode(errors='replace')
                report['whole_http_parser'][variant+'-'+case]=('DETECTED original SDK folded value truncation' if case=='fold' else
                    'DETECTED original SDK accepted empty Content-Length' if case=='empty-length' else
                    'DETECTED original SDK accepted malformed offer')
            else:
                assert success,log.decode(errors='replace');print(log.decode(),end='')
                report['whole_http_parser'][variant]=log.decode().strip()
    # Historical control executes the actual SDK queued-close callback, not a
    # substitute model of the callback. Only queue delivery and slot reuse are seams.
    session_source=(args.sdk/'components/esp_http_server/src/httpd_sess.c').read_text(encoding='utf-8')
    close_functions='\n'.join(session_source[a:b] for a,b in
                             [overlay.function_span(session_source,name) for name in
                              ['httpd_sess_close','httpd_sess_trigger_close_','httpd_sess_trigger_close']])
    report['close_ordering']={}
    for variant,parser_source in [('baseline',(args.sdk/'components/esp_http_server/src/httpd_parse.c').read_text(encoding='utf-8')),('current',parse)]:
        a,b=overlay.function_span(parser_source,'httpd_req_cleanup')
        (out/'close-functions.inc').write_text(close_functions+'\n'+parser_source[a:b],encoding='utf-8')
        close_binary=out/('close-'+variant)
        log=run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function',
                 '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                 '-I'+host(out),host(HERE/'test_close.c'),'-o',host(close_binary)])
        (out/('close-'+variant+'-build.log')).write_bytes(log)
        try:
            log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(close_binary)])
            success=True
        except subprocess.CalledProcessError as error:
            log=error.output;success=False
        (out/('close-'+variant+'.log')).write_bytes(log)
        if variant=='baseline':
            assert not success and b'queued close deleted the recycled session' in log
            report['close_ordering'][variant]='DETECTED actual callback deleted reused session'
        else:
            assert success,log.decode(errors='replace');print(log.decode(),end='')
            report['close_ordering'][variant]='PASS'
    report['source_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [HERE/'apply.py',HERE/'native_httpd_headers.h',HERE/'test_host.c',HERE/'test_wire.c',HERE/'test_close.c',HERE/'test_host.py',HERE/'enable.cmake']}
    report['additional_sdk_sha256']={str(path.relative_to(args.sdk)).replace('\\','/'):hashlib.sha256(path.read_bytes()).hexdigest()
                                    for path in [txrx_path,args.sdk/'components/http_parser/http_parser.c',args.sdk/'components/http_parser/http_parser.h']}
    report['base64_sha256']=hashlib.sha256(base64.read_bytes()).hexdigest()
    report['scope']='Actual generated SDK WS and HTTPD parser/read/pause pipeline, actual SDK http_parser and recv/pending/unrecv C. Field-model HTTPD structs, byte-stream, one-route dispatch and SHA sample seams. Actual SDK Base64 C with constant-time primitive host seam. Separate target SIZE_MAX cap model; no target ABI, real TCP/TLS or full RFC pass claimed.'
    report['passed']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
