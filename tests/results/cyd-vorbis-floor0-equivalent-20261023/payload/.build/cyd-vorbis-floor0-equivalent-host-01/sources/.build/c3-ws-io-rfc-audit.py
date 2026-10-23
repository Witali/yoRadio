from pathlib import Path
import sys
import json
import subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run
out=ROOT/'.build/c3-ws-io-rfc-audit'
out.mkdir(exist_ok=False)
test=ROOT/'tests/native/c3_ws_io'
prior=ROOT/'.build/c3-ws-io-transport-final'
(out/'stubs.h').write_text((test/'stubs.h').read_text().replace('#define CONFIG_HTTPD_WS_STRICTER_RFC6455 0','#define CONFIG_HTTPD_WS_STRICTER_RFC6455 1'))
for name in ['current.inc','sdk.inc']:(out/name).write_bytes((prior/name).read_bytes())
(out/'audit.c').write_text('''#include "stubs.h"
#include "current.inc"
#include "sdk.inc"
#define main original_main
#include "test.c"
#undef main
static esp_err_t sdk_read(httpd_req_t *req) {
    esp_err_t result=httpd_ws_get_frame_type(req);
    if(result!=ESP_OK || req->aux->ws_type==HTTPD_WS_TYPE_CLOSE || req->aux->ws_type==HTTPD_WS_TYPE_PING) return result;
    uint8_t buffer[256]; httpd_ws_frame_t frame={.payload=buffer};
    return httpd_ws_recv_frame(req,&frame,sizeof(buffer));
}
int main(void) {
    static const uint8_t close_one[]={1};
    static const uint8_t close_999[]={3,0xe7};
    static const uint8_t close_1004[]={3,0xec};
    static const uint8_t close_1005[]={3,0xed};
    static const uint8_t close_1006[]={3,0xee};
    static const uint8_t close_1015[]={3,0xf7};
    static const uint8_t close_5000[]={0x13,0x88};
    static const uint8_t close_utf8[]={3,0xe8,0xc0,0xaf};
    static const uint8_t bad_utf8[]={0xc0,0xaf};
    struct { const char *name;const uint8_t *payload;size_t size;httpd_ws_type_t type;bool final; } tests[]={
        {"close_length_one",close_one,sizeof(close_one),HTTPD_WS_TYPE_CLOSE,true},
        {"close_code_999",close_999,2,HTTPD_WS_TYPE_CLOSE,true},
        {"close_code_1004",close_1004,2,HTTPD_WS_TYPE_CLOSE,true},
        {"close_code_1005",close_1005,2,HTTPD_WS_TYPE_CLOSE,true},
        {"close_code_1006",close_1006,2,HTTPD_WS_TYPE_CLOSE,true},
        {"close_code_1015",close_1015,2,HTTPD_WS_TYPE_CLOSE,true},
        {"close_code_5000",close_5000,2,HTTPD_WS_TYPE_CLOSE,true},
        {"close_reason_invalid_utf8",close_utf8,sizeof(close_utf8),HTTPD_WS_TYPE_CLOSE,true},
        {"text_invalid_utf8",bad_utf8,sizeof(bad_utf8),HTTPD_WS_TYPE_TEXT,true},
        {"orphan_continuation",bad_utf8,sizeof(bad_utf8),HTTPD_WS_TYPE_CONTINUE,true},
        {"fragmented_ping",bad_utf8,sizeof(bad_utf8),HTTPD_WS_TYPE_PING,false},
        {"reserved_opcode",bad_utf8,sizeof(bad_utf8),(httpd_ws_type_t)3,true},
    };
    for(size_t i=0;i<sizeof(tests)/sizeof(*tests);++i) {
        reset();ready_session(3);append_input(tests[i].payload,tests[i].size,tests[i].type,tests[i].final,0);
        struct httpd_req_aux aux;httpd_req_t req=request_for(3,&aux);
        esp_err_t result=sdk_read(&req);
        unsigned code=transmitted_size>=4 && transmitted_wire[1]==2 ? (unsigned)transmitted_wire[2]*256+transmitted_wire[3] : 0;
        printf("%s: return=%d server_close_code=%u consumed=%zu/%zu\\n",tests[i].name,result,code,received_at,received_size);
    }
    reset();ready_session(3);append_input((const uint8_t *)"a",1,HTTPD_WS_TYPE_TEXT,false,0);append_input((const uint8_t *)"b",1,HTTPD_WS_TYPE_TEXT,true,0);
    struct httpd_req_aux aux;httpd_req_t req=request_for(3,&aux);esp_err_t first=sdk_read(&req);req=request_for(3,&aux);esp_err_t second=sdk_read(&req);
    printf("new_text_during_fragmented_message: return=%d,%d\\n",first,second);
    reset();return 0;
}
''')
cmd=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-sign-compare','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+host(out),'-I'+host(test),host(out/'audit.c'),'-o',host(out/'audit')]
try:
    (out/'build.log').write_bytes(run(cmd))
    result=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(out/'audit')])
    (out/'test.log').write_bytes(result)
    print(result.decode())
except subprocess.CalledProcessError as e:
    (out/'failure.log').write_bytes(e.output);print(e.output.decode(errors='replace'));raise
