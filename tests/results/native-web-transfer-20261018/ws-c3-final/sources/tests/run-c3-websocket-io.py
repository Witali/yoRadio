"""Exercise C3 WS transport and handlers with unchanged pinned-IDF framing code.

Extracts actual production functions rather than a second transport/parser.
Platform sockets/time/HTTPD session and work dispatch are deterministic seams;
no real TCP scheduling or board stack/latency proof is claimed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32c3-oled-native/main/websocket_service.c'
TEST = ROOT / 'tests/native/c3_ws_io'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run


def select_production(text, old=False):
    return (text[text.index('#define WS_STATUS_POLL_MS'):text.index('static void format_status')]
            + text[text.index('static esp_err_t websocket_handler_awake'):text.index('typedef struct {\n    int64_t started_us;')]
            + ('' if old else text[text.index('esp_err_t websocket_service_register'):]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, default=Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6'))
    parser.add_argument('--baseline-ref', default='d13706c2')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sdk_ws = args.sdk / 'components/esp_http_server/src/httpd_ws.c'
    sdk_rx = args.sdk / 'components/esp_http_server/src/httpd_txrx.c'
    sdk_text, rx_text = sdk_ws.read_text(), sdk_rx.read_text()
    framing = (sdk_text[sdk_text.index('#define HTTPD_WS_CONTINUE'):sdk_text.index('/*\n * The magic GUID')]
               + sdk_text[sdk_text.index('static esp_err_t httpd_ws_check_req'):sdk_text.index('httpd_ws_client_info_t httpd_ws_get_fd_info')]
               + sdk_text[sdk_text.index('static void httpd_ws_send_cb'):sdk_text.index('esp_err_t httpd_ws_send_data(')]
               + sdk_text[sdk_text.index('esp_err_t httpd_ws_send_data_async'):sdk_text.rindex('#endif')])
    receive = rx_text[rx_text.index('static size_t httpd_recv_pending'):rx_text.index('int httpd_recv(httpd_req_t')]
    baseline = subprocess.check_output(['git', 'show', f'{args.baseline_ref}:{MAIN.relative_to(ROOT).as_posix()}'], cwd=ROOT).decode()
    (out / 'baseline.c').write_text(baseline)
    message_header = ROOT/'idf/components/native_stream/include/websocket_message.h'
    files = [MAIN, MAIN.with_suffix('.h'), MAIN.with_name('websocket_message.h'), MAIN.with_name('json_buffer.h'),
             message_header, message_header.with_name('json_buffer.h'),
             ROOT/'idf/components/native_web_transport/include/native_web_transport.h', Path(__file__), TEST/'stubs.h', TEST/'test.c']
    hashes = {}
    for path in files:
        key = path.relative_to(ROOT).as_posix()
        target = out / 'sources' / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        hashes[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    for path in [sdk_ws, sdk_rx, args.sdk/'components/esp_http_server/src/httpd_uri.c']:
        key = path.relative_to(args.sdk).as_posix()
        target = out / 'sdk-sources' / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    (out / 'sdk.inc').write_text(receive + '\n' + framing)
    results = {}
    for name, source, old in [('current', MAIN.read_text(), False), ('baseline', baseline, True)]:
        (out / f'{name}.inc').write_text(select_production(source, old))
        unit = out / f'{name}.c'
        unit.write_text('#include "stubs.h"\n' + ('#define OLD_BASELINE 1\n' if old else '')
                        + f'#include "{name}.inc"\n#include "sdk.inc"\n#include "test.c"\n')
        binary = out / name
        cmd = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-Wno-unused-function', '-Wno-unused-variable', '-Wno-sign-compare',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-I'+host(TEST), '-I'+host(MAIN.parent), '-I'+host(message_header.parent), host(unit), '-o', host(binary)]
        try:
            (out / f'{name}-build.log').write_bytes(run(cmd))
            for mode in (['all'] if not old else ['short-send', 'deadline', 'pong', 'fd-reuse']):
                command = ['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                           'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '45', host(binary), mode]
                try:
                    log = run(command)
                    code = 0
                except subprocess.CalledProcessError as error:
                    code, log = error.returncode, error.output
                (out / f'{name}-{mode}.log').write_bytes(log)
                print(log.decode(errors='replace').strip())
                assert code == (1 if old else 0), (name, mode, code)
                if old:
                    assert b'NEGATIVE_CONTROL_FAIL:' in log and b'Sanitizer' not in log
                else:
                    cases = int(re.search(rb'PASS: (\d+) C3 WebSocket', log)[1])
                    layout = json.loads(re.search(rb'WS_LAYOUT=(.+)',log)[1])
                    assert json.loads(re.search(rb'JSON_SAMPLE=(.+)',log)[1]) == '\ufffd'*66
                results[f'{name}/{mode}'] = {'exit_code': code, 'expected_failure': old}
        except subprocess.CalledProcessError as error:
            (out / 'failure.log').write_bytes(error.output)
            print(error.output.decode(errors='replace'), file=sys.stderr)
            raise
    report = {'passed': True, 'sanitizers': ['ASan', 'UBSan'], 'cases': cases, 'host_layout': layout, 'results': results,
              'source_sha256': hashes, 'baseline_ref': args.baseline_ref,
              'baseline_sha256': hashlib.sha256(baseline.encode()).hexdigest(),
              'sdk_sha256': {p.relative_to(args.sdk).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [sdk_ws, sdk_rx]},
              'application_frame_send_budget_us': 1000000,
              'application_receive_handler_budget_us': 1000000,
              'fragmented_message_budget_us': 5000000,
              'separate_fallback_budgets': 'SDK opcode and SDK control operations before the application handler each have finite per-read/write budgets.',
              'scope': 'Actual production transport/session/broadcast/handler/register functions and unchanged pinned-IDF WS framing/receive functions; deterministic lwIP, clock, context and queue seams. Correct commands, reboot and status-task scheduling are preserved but not executed by this targeted test. No board RAM/stack/latency/TCP timing proof.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
