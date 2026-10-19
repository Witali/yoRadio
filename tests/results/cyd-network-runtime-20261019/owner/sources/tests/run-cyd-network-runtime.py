"""Execute the complete CYD network owner task with pthread RTOS boundaries.

The production network_runtime.c, native_state.c and shared erase implementation
are compiled as complete translation units. Actual registered event callbacks,
owner loop and public APIs execute concurrently. Tests advance a monotonic clock
only while the real owner is parked in its vTaskDelay seam; they never write owner
phase, acknowledgments or private state. Wi-Fi/netif observations and SDK failures
are deterministic seams. No target ABI, RF, scheduler timing or heap/HWM claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = Path('idf/esp32-cyd2usb-native/main')
TEST = Path('tests/native/cyd_network_runtime')
CASES = [
    'no-profiles', 'one-immutable', 'five-attempts', 'late-wrap',
    'startup-deadline', 'cycle-deadline', 'manual-admission', 'manual-before-start', 'manual-exhaustion',
    'config-failure', 'connect-failure', 'config-busy', 'disconnect-error', 'disconnect-stuck',
    'ap-enable-errors', 'queue-overflow', 'start-overflow', 'stale-events',
    'same-ssid', 'snapshot-lock', 'rssi', 'rssi-late', 'projection-lock',
    'pending-publisher-stop', 'unregister-running', 'concurrent-stop', 'cleanup-poison', 'concurrent',
    'clock-limit', 'invalid-input',
    *['rollback-' + name for name in ['queue', 'mutex', 'event', 'ap-netif', 'mac',
      'mode-ap', 'mode-sta', 'ap-config', 'ap-attach', 'ap-handlers',
      'wifi-handler', 'ip-handler', 'task', 'unregister']],
]


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command, timeout=60):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    return result.returncode, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', '--output', dest='out', type=Path, required=True)
    parser.add_argument('--case', action='append', choices=CASES)
    parser.add_argument('--tsan', action='store_true')
    parser.add_argument('--skip-mutants', action='store_true')
    args = parser.parse_args(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__).resolve().relative_to(ROOT),
             *[TEST / name for name in ['platform.h', 'platform.c', 'test.c', 'tsan_control.c', 'README.md']],
             *[MAIN / name for name in ['network_runtime.c', 'network_runtime.h',
               'network_status.h', 'network_netif.c', 'network_netif.h',
               'network_profiles.h', 'board_config.h', 'native_state.c', 'native_state.h',
               'time_service.h', 'time_settings.h']],
             Path('idf/components/native_wifi_store/native_wifi_store.c'),
             Path('idf/components/native_wifi_store/include/native_wifi_store.h'),
             Path('idf/components/native_time/include/native_time_sntp.h')]
    report = dict(passed=False, scope=__doc__, complete_matrix=not args.case,
                  source_sha256={}, cases={}, negative_controls={}, physical_hardware=False,
                  target_abi=False, actual_rtos_scheduler=False)
    for relative in files:
        data = (ROOT / relative).read_bytes(); destination = out / 'sources' / relative
        destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(data)
        report['source_sha256'][relative.as_posix()] = hashlib.sha256(data).hexdigest()
    frozen = out / 'sources'; stubs = out / 'stubs'; stubs.mkdir(); (stubs / 'freertos').mkdir(); (stubs / 'driver').mkdir()
    wrappers = ['esp_err.h', 'esp_netif.h', 'esp_event.h', 'esp_mac.h', 'esp_timer.h',
                'esp_wifi.h', 'esp_wifi_default.h', 'freertos/FreeRTOS.h',
                'freertos/event_groups.h', 'freertos/queue.h', 'freertos/semphr.h', 'freertos/task.h']
    for name in wrappers:
        (stubs / name).write_text('#pragma once\n#include "platform.h"\n')
    (stubs / 'driver/gpio.h').write_text('#pragma once\n/* GPIO macros unused by this owner. */\n')
    (out / 'sdk-stub-manifest.json').write_text(json.dumps({
        p.relative_to(stubs).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in stubs.rglob('*') if p.is_file()}, indent=2) + '\n')

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    def build(sanitizer, binary, runtime=None):
        command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-pthread', '-fno-omit-frame-pointer',
                   '-fno-pie', '-no-pie', '-fsanitize=' + sanitizer,
                   '-include', host(frozen / TEST / 'platform.h'),
                   '-I' + host(stubs), '-I' + host(frozen / TEST), '-I' + host(frozen / MAIN),
                   '-I' + host(frozen / 'idf/components/native_wifi_store/include'),
                   '-I' + host(frozen / 'idf/components/native_time/include'),
                   host(runtime or frozen / MAIN / 'network_runtime.c'),
                   host(frozen / MAIN / 'network_netif.c'),
                   host(frozen / MAIN / 'native_state.c'),
                   host(frozen / 'idf/components/native_wifi_store/native_wifi_store.c'),
                   host(frozen / TEST / 'platform.c'), host(frozen / TEST / 'test.c'),
                   '-o', host(binary)]
        report.setdefault('commands', []).append(command)
        code, log = execute(command); (out / (binary.name + '-build.log')).write_bytes(log)
        if code: save(); raise RuntimeError(log.decode(errors='replace'))

    code, log = execute(['gcc', '--version']); (out / 'compiler.log').write_bytes(log)
    assert code == 0, log.decode(errors='replace')
    report['compiler'] = log.decode().splitlines()[0]
    binary = out / 'runtime'; build('address,undefined', binary)
    for case in args.case or CASES:
        code, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                             'UBSAN_OPTIONS=halt_on_error=1', host(binary), case])
        (out / (case + '.log')).write_bytes(log)
        report['cases'][case] = dict(status=code, passed=code == 0, output=log.decode(errors='replace').strip()); save()
        if code or log != ('PASS:' + case + '\n').encode():
            raise RuntimeError(case + ': ' + log.decode(errors='replace'))
        print('PASS:' + case, flush=True)
    if args.tsan:
        control = out / 'tsan-control'
        command = ['gcc', '-std=c11', '-O1', '-g', '-pthread', '-fno-pie', '-no-pie',
                   '-fsanitize=thread', host(frozen / TEST / 'tsan_control.c'), '-o', host(control)]
        code, log = execute(command); (out / 'tsan-control-build.log').write_bytes(log)
        assert code == 0, log.decode(errors='replace')
        report['tsan'] = dict(control_command=command, controls=[], supported=False,
                              passed=False, scope='Host pthread race check only')
        for attempt in range(3):
            code, log = execute(['env', 'TSAN_OPTIONS=halt_on_error=1', host(control)])
            (out / ('tsan-control-' + str(attempt) + '.log')).write_bytes(log)
            report['tsan']['controls'].append(dict(status=code, output=log.decode(errors='replace').strip()))
            if code == 0 and log == b'TSAN_CONTROL_OK\n':
                report['tsan']['supported'] = True; break
        if report['tsan']['supported']:
            tsan = out / 'runtime-tsan'; build('thread', tsan)
            code, log = execute(['env', 'TSAN_OPTIONS=halt_on_error=1', host(tsan), 'concurrent'])
            (out / 'tsan-concurrent.log').write_bytes(log)
            unavailable = b'unexpected memory mapping' in log or b'ThreadSanitizer: unsupported' in log
            report['tsan'].update(status=code, supported=not unavailable, passed=code == 0,
                                  output=log.decode(errors='replace').strip()); save()
            if code and not unavailable: raise RuntimeError('TSAN: ' + log.decode(errors='replace'))
        else:
            report['tsan']['unavailable_reason'] = 'Race-free standalone pthread control could not complete under this TSAN runtime'
        save()
    if not args.skip_mutants:
        source = (frozen / MAIN / 'network_runtime.c').read_text()
        mutations = [
            ('publish_failed_config', 'result = esp_wifi_set_config(WIFI_IF_STA, &config);',
             'owner->view.profile_index = owner->view.target_profile; result = esp_wifi_set_config(WIFI_IF_STA, &config);',
             'config-failure', 'failed_set_config_not_published'),
            ('stale_pending_snapshot', 'snapshot.online = snapshot.rssi_valid = false;\n        snapshot.ipv4 = 0; snapshot.rssi = 0; snapshot.reconciling = true;',
             'snapshot.reconciling = true;', 'late-wrap', 'pending_loss_masks_old_status'),
            ('manual_tears_down_portal', 'static void begin_cycle(network_owner_t *owner, uint8_t first, int64_t now) {\n    ++owner->view.epoch;',
             'static void begin_cycle(network_owner_t *owner, uint8_t first, int64_t now) {\n    if (owner->view.ap_enabled) (void)esp_wifi_set_mode(WIFI_MODE_STA);\n    ++owner->view.epoch;',
             'manual-admission', 'manual_retry_retains_preconfigured_apsta'),
            ('rssi_query_keeps_old_sample', 'owner->view.rssi = 0; owner->view.rssi_valid = false;',
             '/* missing RSSI invalidation */', 'rssi', 'failed_or_late_rssi_invalidated'),
        ]
        for name, old, new, case, marker in mutations:
            assert source.count(old) == 1, (name, source.count(old))
            directory = out / 'mutants' / name; directory.mkdir(parents=True)
            unit = directory / 'network_runtime.c'; unit.write_text(source.replace(old, new, 1))
            binary = directory / name; build('address,undefined', binary, unit)
            code, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=0:halt_on_error=1',
                                 'UBSAN_OPTIONS=halt_on_error=1', host(binary), case])
            (directory / 'test.log').write_bytes(log)
            assert code == 80 and log.startswith(('SEMANTIC_FAILURE:' + marker + ':').encode()), (name, code, log)
            assert not any(error in log for error in [b'AddressSanitizer', b'runtime error:', b'LeakSanitizer']), log
            report['negative_controls'][name] = dict(detected=True, status=code,
                case=case, expected_marker=marker, sha256=hashlib.sha256(unit.read_bytes()).hexdigest())
            save(); print('DETECTED:' + name, flush=True)
    report['mutants_enabled'] = not args.skip_mutants
    report['passed'] = True; save()


if __name__ == '__main__':
    main()
