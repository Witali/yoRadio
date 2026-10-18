"""Actual Wi-Fi handlers/owners and pinned SDK buffered I/O/context lifecycle."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SDK_ROOT = ROOT / '.idf' if (ROOT / '.idf').is_dir() else ROOT.parents[1] / '.idf'
FIXTURE = ROOT / 'tests/native/wifi_http'
COMPONENT = ROOT / 'idf/components/native_wifi_store'


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def module(path):
    spec = importlib.util.spec_from_file_location('wifi_sdk_extract', path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def execute(command, path):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    path.write_bytes(result.stdout)
    if result.returncode:
        raise RuntimeError(result.stdout.decode(errors='replace'))
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sdk-cyd', type=Path, default=SDK_ROOT / 'v6.0.2')
    parser.add_argument('--sdk-c3', type=Path, default=SDK_ROOT / 'v6.1-9a97f6c54ec6')
    args = parser.parse_args()
    if sys.platform == 'win32':
        raise SystemExit(subprocess.call(['wsl.exe', '--exec', 'python3', host(__file__),
            '--output', host(args.output), '--sdk-cyd', host(args.sdk_cyd), '--sdk-c3', host(args.sdk_c3)]))
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cyd = ROOT / 'idf/esp32-cyd2usb-native/main'
    c3 = ROOT / 'idf/esp32c3-oled-native/main'
    files = [Path(__file__), ROOT / 'tests/run-native-ota-http.py', *FIXTURE.glob('*.*'),
             *COMPONENT.glob('*.c'), *COMPONENT.glob('include/*.h'), COMPONENT / 'CMakeLists.txt',
             ROOT / 'idf/components/native_storage/file_transaction.c',
             ROOT / 'idf/components/native_storage/include/file_transaction.h',
             cyd / 'web_wifi.c', cyd / 'web_wifi.h', cyd / 'web_reboot.c', cyd / 'web_reboot.h',
             cyd / 'network_service.c', cyd / 'network_service.h',
             c3 / 'web_wifi.c', c3 / 'web_wifi.h', c3 / 'network_service.c', c3 / 'network_service.h',
             c3 / 'websocket_service.c', c3 / 'websocket_service.h', c3 / 'web_service.c']
    hashes = {}
    for path in files:
        relative = path.relative_to(ROOT)
        raw = path.read_bytes()
        dest = out / 'sources' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        hashes[relative.as_posix()] = hashlib.sha256(raw).hexdigest()
    frozen = out / 'sources'
    extract = module(frozen / 'tests/run-native-ota-http.py')
    report = {'source_sha256': hashes, 'variants': {}, 'sanitizers': ['ASan', 'UBSan']}
    for target, sdk, mainpath in [('cyd', args.sdk_cyd, cyd), ('c3', args.sdk_c3, c3)]:
        directory = out / target
        directory.mkdir()
        sdk_hashes = {}
        texts = {}
        for name in ['httpd_txrx.c', 'httpd_sess.c', 'httpd_parse.c']:
            relative = Path('components/esp_http_server/src') / name
            raw = (sdk / relative).read_bytes()
            dest = directory / 'sdk-sources' / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
            sdk_hashes[relative.as_posix()] = hashlib.sha256(raw).hexdigest()
            texts[name] = raw.decode()
        names = ['httpd_sess_set_send_override', 'httpd_sess_set_recv_override',
                 'httpd_send_all', 'httpd_recv_pending', 'httpd_recv_with_opt',
                 'httpd_recv', 'httpd_unrecv', 'httpd_resp_set_hdr', 'httpd_resp_set_status',
                 'httpd_resp_set_type', 'httpd_resp_send', 'httpd_req_recv']
        (directory / 'sdk-io.inc').write_text(extract.selected(texts['httpd_txrx.c'], names))
        (directory / 'sdk-context.inc').write_text(extract.selected(texts['httpd_sess.c'],
            ['httpd_sess_free_ctx', 'httpd_sess_get_ctx', 'httpd_sess_set_ctx']))
        (directory / 'sdk-cleanup.inc').write_text(extract.selected(texts['httpd_parse.c'], ['httpd_req_cleanup']))
        for name in ['esp_err.h', 'esp_http_server.h', 'esp_timer.h', 'native_web_transport.h',
                     'deep_sleep_clock.h', 'display_settings.h', 'freertos/FreeRTOS.h',
                     'freertos/task.h', 'lwip/sockets.h']:
            dest = directory / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text('#pragma once\n#include "host.h"\n')
        (directory / 'native_state.h').write_text('#pragma once\ntypedef struct {int unused;} native_state_t;\n')
        targetdir = frozen / mainpath.relative_to(ROOT)
        (directory / 'web_wifi.h').write_bytes((targetdir / 'web_wifi.h').read_bytes())
        reboot_header = 'websocket_service.h' if target == 'c3' else 'web_reboot.h'
        (directory / reboot_header).write_bytes((targetdir / reboot_header).read_bytes())
        reboot = (targetdir / ('websocket_service.c' if target == 'c3' else 'web_reboot.c')).read_text()
        if target == 'c3':
            reboot = reboot[reboot.index('// The status task exists'):reboot.index('static void log_setting_error')]
        else:
            reboot = extract.strip_includes(reboot)
        (directory / 'reboot.inc').write_text(reboot)
        network = (targetdir / 'network_service.c').read_text()
        start = network.index('static SemaphoreHandle_t s_wifi_save_lock;')
        end = (network.index('// End desired next-boot credential owner.', start) if target == 'c3'
               else network.index('static bool read_credentials(', start))
        (directory / 'network.inc').write_text(network[start:end])
        (directory / 'target.inc').write_text(extract.strip_includes((targetdir / 'web_wifi.c').read_text()))
        if target == 'c3':
            (directory / 'static.inc').write_text('static void *s_static_request_queue=(void *)1;\n' +
                extract.selected((targetdir / 'web_service.c').read_text(), ['static_handler']))
        unit = directory / 'unit.c'
        unit.write_text(('#define TARGET_C3 1\n' if target == 'c3' else '') + '''#include "host.h"
#include "web_wifi.h"
#include "''' + reboot_header + '''"
#include "native_wifi_file.h"
#include "native_wifi_json.h"
#include "native_wifi_http.h"
#include "reboot.inc"
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
#define malloc response_malloc
#include "sdk-io.inc"
#undef malloc
#include "sdk-context.inc"
#include "sdk-cleanup.inc"
#define calloc workspace_calloc
#define free workspace_free
#include "native_wifi_http.c"
#undef free
#undef calloc
#include "target.inc"
#ifdef TARGET_C3
#include "native_wifi_public.h"
#include "static.inc"
#endif
#include "platform.c"
#include "test.c"
''')
        includes = [directory, frozen / FIXTURE.relative_to(ROOT),
                    frozen / COMPONENT.relative_to(ROOT), frozen / COMPONENT.relative_to(ROOT) / 'include',
                    frozen / 'idf/components/native_storage', frozen / 'idf/components/native_storage/include']
        command = ['gcc', '-std=c11', '-D_GNU_SOURCE', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-Wno-unused-function', '-Wno-unused-parameter', '-Wno-format', '-Wno-sign-compare',
                   '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-pthread',
                   *['-I' + str(path) for path in includes], str(unit), '-o', str(directory / 'test')]
        execute(command, directory / 'build.log')
        log = execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                       'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '60', str(directory / 'test')], directory / 'test.log')
        print(target + ': ' + log.decode().strip())
        report['variants'][target] = {'passed': True, 'result': log.decode().strip(),
            'groups': int(re.search(rb'(\d+) groups', log)[1]), 'sdk_sha256': sdk_hashes,
            'actual_sdk_functions': names + ['httpd_sess_free_ctx', 'httpd_sess_get_ctx', 'httpd_sess_set_ctx', 'httpd_req_cleanup']}
        mutations = {
            'cancel-durable-on-response-error': ('native_wifi_http.c',
                'config->finish(config->context, committed);',
                'config->finish(config->context, committed && response == ESP_OK);', 'success_cases'),
            'cancel-durable-after-deadline': ('native_wifi_http.c',
                'if (result == NATIVE_WIFI_OK) { committed = true; goto done; }',
                'if (result == NATIVE_WIFI_OK) { committed = now_us() < deadline(io); goto done; }', 'success_cases'),
            'skip-http-workspace-erase': ('native_wifi_http.c',
                'native_wifi_erase(opaque, sizeof(wifi_http_io_t));',
                '/* mutant: no erase */', 'workspace_free'),
            'bypass-sdk-pending-body': ('native_wifi_http.c',
                'httpd_req_recv(request, (char *)io->body + offset, request->content_len - offset)',
                'wifi_receive(request->handle, socket, (char *)io->body + offset, request->content_len - offset, 0)', 'success_cases'),
            'expose-all-private-data-paths': ('include/native_wifi_public.h',
                'return !data || (path == sizeof(playlist)',
                'return data || !data || (path == sizeof(playlist)', 'uri_cases'),
        }
        controls = {}
        for name, (file, before, after, expected) in mutations.items():
            original = (frozen / COMPONENT.relative_to(ROOT) / file).read_text()
            if original.count(before) != 1:
                raise RuntimeError('Nonunique mutation anchor: ' + name)
            control = directory / name
            control.mkdir()
            (control / Path(file).name).write_text(original.replace(before, after))
            control_unit = control / 'unit.c'
            control_unit.write_bytes(unit.read_bytes())
            control_command = [part for part in command]
            control_command.insert(control_command.index('-I' + str(directory)), '-I' + str(control))
            control_command = [str(control_unit) if part == str(unit) else
                               str(control / 'test') if part == str(directory / 'test') else part
                               for part in control_command]
            execute(control_command, control / 'build.log')
            result = subprocess.run(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                'UBSAN_OPTIONS=halt_on_error=1', 'timeout', '60', str(control / 'test')],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=80)
            (control / 'test.log').write_bytes(result.stdout)
            output = result.stdout.decode(errors='replace')
            if (not result.returncode or expected not in output or 'Assertion' not in output or
                    'ERROR: AddressSanitizer' in output or 'runtime error:' in output):
                raise RuntimeError('Control was not rejected at semantic assertion ' + name + ': ' + output)
            controls[name] = {'rejected': True, 'semantic_assertion': expected}
        report['variants'][target]['semantic_controls'] = controls
        print(target + ': ' + str(len(controls)) + ' semantic controls rejected')
    report['passed'] = True
    report['scope'] = ('Actual target metadata/edit owner callbacks, common CSV/file/JSON/HTTP and target handlers/reboot reservation; '
                       'actual pinned SDK pending receive/context/response/cleanup functions. Real synthetic Linux files with SPIFFS '
                       'no-overwrite rename; SDK field layouts, RTOS/clock/readiness and native transport are explicit host seams. '
                       'Abnormal session cleanup verifies whole HTTP secret workspace erasure. Does not prove actual wire/TLS or target flash durability.')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
