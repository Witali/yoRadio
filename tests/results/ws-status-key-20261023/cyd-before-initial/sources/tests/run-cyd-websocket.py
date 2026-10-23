"""Run the real CYD WebSocket core with deferred HTTPD work and SDK seams.

The HTTPD seam executes queued work later and captures synchronous frame sends;
real IDF framing, TCP timing and board RAM/stack measurements remain separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32-cyd2usb-native/main'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-ref', help='Qualify a historical production implementation with the current regression harness')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    stubs = {
        'sdkconfig.h': '#define CONFIG_HTTPD_WS_SUPPORT 1\n#define CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT 1\n#define CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT 1\n#define CONFIG_HTTPD_QUEUE_WORK_BLOCKING 0\n#define CONFIG_LWIP_MAX_SOCKETS 10\n',
        'esp_err.h': '''#pragma once
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL (-1)
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_TIMEOUT 0x107
''',
        'freertos/FreeRTOS.h': '''#pragma once
#include <stddef.h>
#include <stdint.h>
#define pdPASS 1
#define pdMS_TO_TICKS(value) (value)
''',
        'freertos/semphr.h': '#pragma once\ntypedef void *SemaphoreHandle_t;\n',
        'freertos/task.h': '''#pragma once
#include "FreeRTOS.h"
int xTaskCreate(void (*)(void *),const char *,unsigned,void *,unsigned,void *);
void vTaskDelay(unsigned);
void vTaskDelete(void *);
''',
        'esp_timer.h': '#pragma once\n#include <stdint.h>\nint64_t esp_timer_get_time(void);\n',
        'native_web_transport.h': '''#pragma once
#include "esp_http_server.h"
#include <sys/types.h>
ssize_t native_web_transport_send(httpd_handle_t,int,const void *,size_t,int,bool *);
ssize_t native_web_transport_recv(httpd_handle_t,int,void *,size_t,int,bool *);
void native_web_transport_shutdown(httpd_handle_t,int,bool);
''',
        'lwip/sockets.h': '''#pragma once
#include <sys/types.h>
#include <sys/select.h>
#define SHUT_RDWR 2
#define MSG_DONTWAIT 8
#define MSG_PEEK 2
int shutdown(int,int);
ssize_t lwip_send(int,const void *,size_t,int);
ssize_t lwip_recv(int,void *,size_t,int);
int lwip_select(int,fd_set *,fd_set *,fd_set *,struct timeval *);
''',
        'esp_http_server.h': '''#pragma once
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
typedef void *httpd_handle_t;
#define HTTPD_400_BAD_REQUEST 400
typedef void (*httpd_free_ctx_fn_t)(void *);
typedef void (*httpd_work_fn_t)(void *);
typedef enum { HTTP_DELETE=0, HTTP_GET=1, HTTP_POST=3 } httpd_method_t;
typedef enum { HTTPD_WS_TYPE_CONTINUE=0,HTTPD_WS_TYPE_TEXT=1,HTTPD_WS_TYPE_BINARY=2,HTTPD_WS_TYPE_CLOSE=8,HTTPD_WS_TYPE_PING=9,HTTPD_WS_TYPE_PONG=10 } httpd_ws_type_t;
typedef enum { HTTPD_WS_CLIENT_INVALID,HTTPD_WS_CLIENT_HTTP,HTTPD_WS_CLIENT_WEBSOCKET } httpd_ws_client_info_t;
typedef struct { bool final,fragmented;httpd_ws_type_t type;uint8_t *payload;size_t len; } httpd_ws_frame_t;
typedef struct { int socket;httpd_method_t method;const char *payload;size_t length;httpd_ws_type_t type;bool final,fragmented,receive_error,transport_reads; } httpd_req_t;
typedef struct { const char *uri;httpd_method_t method;esp_err_t (*handler)(httpd_req_t *);bool is_websocket,handle_ws_control_frames;esp_err_t (*ws_post_handshake_cb)(httpd_req_t *);esp_err_t (*ws_pre_handshake_cb)(httpd_req_t *); } httpd_uri_t;
typedef int (*httpd_send_func_t)(httpd_handle_t,int,const char *,size_t,int);
typedef int (*httpd_recv_func_t)(httpd_handle_t,int,char *,size_t,int);
#define HTTPD_SOCK_ERR_FAIL (-1)
#define HTTPD_SOCK_ERR_TIMEOUT (-3)
esp_err_t httpd_register_uri_handler(httpd_handle_t,const httpd_uri_t *);
esp_err_t httpd_get_client_list(httpd_handle_t,size_t *,int *);
httpd_ws_client_info_t httpd_ws_get_fd_info(httpd_handle_t,int);
void *httpd_sess_get_ctx(httpd_handle_t,int);
void httpd_sess_set_ctx(httpd_handle_t,int,void *,httpd_free_ctx_fn_t);
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_queue_work(httpd_handle_t,httpd_work_fn_t,void *);
esp_err_t httpd_ws_send_frame_async(httpd_handle_t,int,httpd_ws_frame_t *);
int httpd_req_to_sockfd(httpd_req_t *);
esp_err_t httpd_ws_recv_frame(httpd_req_t *,httpd_ws_frame_t *,size_t);
esp_err_t httpd_resp_send_err(httpd_req_t *,int,const char *);
''',
        'compat.h': '#include <stddef.h>\nsize_t strlcpy(char *,const char *,size_t);\n',
    }
    for relative, contents in stubs.items():
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    sources = [Path(__file__), ROOT / 'tests/native/cyd_websocket_test.c',
               MAIN / 'websocket_service.c', *MAIN.glob('*.h'),
               ROOT / 'idf/components/native_audio_settings/native_audio_settings.h',
               ROOT / 'idf/components/native_storage/include/radio_control.h',
               ROOT / 'idf/components/native_stream/include/json_buffer.h',
               ROOT / 'idf/components/native_stream/include/websocket_message.h',
               ROOT / 'idf/components/native_web_transport/include/native_web_transport.h',
               ROOT / 'idf/components/native_network_power/include/native_network_power.h',
               ROOT / 'tools/codec_benchmark/run_output_dma_host.py']
    hashes = {}
    for path in sources:
        data = path.read_bytes(); relative = path.relative_to(ROOT)
        snapshot = out / 'sources' / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True); snapshot.write_bytes(data)
        hashes[relative.as_posix()] = hashlib.sha256(data).hexdigest()
    frozen = out / 'sources'
    frozen_main = frozen / MAIN.relative_to(ROOT)
    binary = out / 'cyd-websocket'
    production = MAIN / 'websocket_service.c'
    source = subprocess.check_output(['git', 'show', args.source_ref + ':' + production.relative_to(ROOT).as_posix()], cwd=ROOT) if args.source_ref else (frozen_main / 'websocket_service.c').read_bytes()
    (out / 'websocket-under-test.c').write_bytes(source)
    fixture = (frozen / 'tests/native/cyd_websocket_test.c').read_text().replace(
        '#include "../../idf/esp32-cyd2usb-native/main/websocket_service.c"',
        '#include "websocket-under-test.c"')
    (out / 'cyd_websocket_test.c').write_text('#define TEST_NETWORK_STATUS '+str(int(b'network_service_snapshot' in source))+'\n'+fixture)
    try:
        build = run(['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                     '-Wno-misleading-indentation', '-pthread', '-fsanitize=address,undefined',
                     '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-include', host(out / 'compat.h'),
                     '-I' + host(out), '-I' + host(frozen_main),
                     '-I' + host(frozen / 'idf/components/native_stream/include'),
                     '-I' + host(frozen / 'idf/components/native_audio_settings'),
                     '-I' + host(frozen / 'idf/components/native_storage/include'),
                     '-I' + host(frozen / 'idf/components/native_network_power/include'),
                     host(out / 'cyd_websocket_test.c'), '-o', host(binary)])
        (out / 'build.log').write_bytes(build)
        log = run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '30', host(binary)])
    except subprocess.CalledProcessError as error:
        (out / 'failure.log').write_bytes(error.output)
        print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    (out / 'test.log').write_bytes(log)
    maximum = None
    for line in log.decode().splitlines():
        if line.startswith('WS_MAX='):
            maximum = json.loads(line.removeprefix('WS_MAX='))
            assert maximum['status']['bitrate'] == 2**32 - 1
            assert maximum['status']['generation'] == 2**32 - 1
            assert maximum['status']['connecting'] is True
            assert maximum['status']['current'] == 65535 and maximum['status']['count'] == 65535
            assert maximum['status']['smartstart'] is True and maximum['status']['normalization'] is True
            assert maximum['status']['normgain'] == 255 and maximum['status']['normtarget'] == -128 and maximum['status']['normtime'] == 65535
            payload = {item['id']: item['value'] for item in maximum['payload']}
            assert payload['bitrate'] == 2**32 - 1 and payload['heap'] == 99
            assert maximum['status']['station'] == '\1' * 95
        elif line.startswith('WS_MAX_BYTES='):
            maximum_bytes = int(line.split('=', 1)[1])
        else:
            print(line)
    assert maximum is not None
    assert b'18 scalar and 4 string changes detected' in log
    report = {'passed': True, 'sanitizers': ['ASan', 'UBSan'], 'maximum_json_bytes': maximum_bytes,
              'status_key_comparison': {'padding_ignored': True, 'scalar_fields': 18, 'string_fields': 4},
              'source_ref': args.source_ref, 'qualified_implementation_sha256': hashlib.sha256(source).hexdigest(),
              'status_capacity': 5120, 'websocket_client_limit': 2, 'queued_status_work_limit': 1,
              'application_send_frame_budget_us': 1000000, 'application_receive_handler_budget_us': 1000000,
              'separate_budgets': 'HTTPD opcode read before handler and SDK control reads use separate finite per-read fallback budgets; TCP/RTOS timing remains unverified.',
              'source_sha256': hashes,
              'scope': 'Actual production WS core with deferred HTTPD callbacks, synchronous send completion seams and real concurrent polling producers; no IDF framing/TCP/hardware/stack timing proof.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
