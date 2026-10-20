"""Execute current CYD bootstrap facade and app/time ordering with platform seams.

Production app startup and current network facade bodies run unchanged. SDK,
RTOS, profile loading, display and time boundaries are deterministic host seams.
Current CYD GOT/loss/time notifications execute in run-cyd-network-runtime.py;
the old CYD event handler is not represented as current production here.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host


def execute(command):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return result.returncode, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    main_dir = ROOT / 'idf/esp32-cyd2usb-native/main'
    test = ROOT / 'tests/native/cyd_time_events_test.c'
    helper = ROOT / 'tests/run-web-warning-regressions.py'
    files = [Path(__file__).resolve(), test, helper, main_dir / 'app_main.c',
             main_dir / 'network_service.c', main_dir / 'board_config.h',
             main_dir / 'network_profiles.h', main_dir / 'network_netif.h',
             main_dir / 'network_runtime.h',
             main_dir / 'network_settings.h',
             ROOT / 'idf/esp32-cyd2usb-native/sdkconfig.defaults',
             ROOT / 'idf/esp32c3-oled-native/main/network_service.c',
             ROOT / 'tools/codec_benchmark/run_output_dma_host.py']
    report = {'passed': False, 'scope': __doc__, 'physical_hardware': False,
              'source_sha256': {}, 'negative_controls': {}}
    for path in files:
        data = path.read_bytes()
        relative = path.relative_to(ROOT)
        snapshot = out / 'sources' / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(data)
        report['source_sha256'][relative.as_posix()] = hashlib.sha256(data).hexdigest()
    frozen = out / 'sources'
    spec = importlib.util.spec_from_file_location('frozen_helpers', frozen / helper.relative_to(ROOT))
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    network = (frozen / main_dir.relative_to(ROOT) / 'network_service.c').read_text()
    startup = (frozen / main_dir.relative_to(ROOT) / 'app_main.c').read_text()
    globals_start=network.index('static network_netif_t s_station_netif;')
    globals_end=network.index('static SemaphoreHandle_t',globals_start)
    network_unit=network[globals_start:globals_end]+helpers.function(network,'network_service_start')
    startup_unit = ''.join(helpers.function(startup, name) for name in ['mount_spiffs', 'app_main'])
    c3_unit = helpers.function((frozen/'idf/esp32c3-oled-native/main/network_service.c').read_text(), 'event_handler')
    assert 'CONFIG_LWIP_SNTP_MAX_SERVERS=2' in (frozen / 'idf/esp32-cyd2usb-native/sdkconfig.defaults').read_text()
    (out / 'driver').mkdir()
    (out / 'driver/gpio.h').write_text('/* GPIO declarations unused by this startup fixture. */\n')
    (out / 'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n')
    (out / 'esp_netif.h').write_text('#pragma once\ntypedef struct esp_netif esp_netif_t;\n')
    command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-Wno-unused-function', '-Wno-unused-variable',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-I' + host(out), '-I' + host(frozen / main_dir.relative_to(ROOT)),
               host(frozen / test.relative_to(ROOT)), '-o', host(out / 'events')]

    def run_case(name, net, app, assertion=None, c3=c3_unit):
        (out / 'network.inc').write_text(net)
        (out / 'startup.inc').write_text(app)
        (out / 'c3-events.inc').write_text(c3)
        code, log = execute(command)
        (out / (name + '-build.log')).write_bytes(log)
        assert code == 0, log.decode(errors='replace')
        code, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                             'UBSAN_OPTIONS=halt_on_error=1', host(out / 'events')])
        (out / (name + '.log')).write_bytes(log)
        assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log
        if assertion is None:
            assert code == 0, log.decode(errors='replace')
            report['positive'] = log.decode().strip()
            print(log.decode(), end='')
        else:
            assert code != 0 and b'Assertion' in log and assertion.encode() in log, (name, log)
            report['negative_controls'][name] = {'detected': True, 'expected_assertion': assertion,
                                                  'status': code}

    run_case('positive', network_unit, startup_unit)
    mutations = [
        ('missing_time_start', 'startup', 'result = time_service_start();',
         'result = ESP_OK;', 'time_step>display_step'),
        ('missing_network_settings_start', 'startup', 'result = network_settings_init();',
         'result = ESP_OK;', 'network_settings_step>nvs_step'),
        ('changed_network_affinity', 'startup', 'NULL, 3, NULL, 0);',
         'NULL, 3, NULL, 1);', 'priority == 3U && core == 0'),
        ('driver_flash_persistence', 'network', 'esp_wifi_set_storage(WIFI_STORAGE_RAM)',
         'ESP_OK', 'driver_ram'),
        ('missing_profile_load','network','esp_err_t loaded = network_profiles_load(&profiles);',
         'esp_err_t loaded = ESP_OK;','profiles->count==(empty_profiles?0:2)'),
        ('partial_profile_failure_handoff','network','        native_wifi_erase(&profiles, sizeof(profiles));',
         '        /* negative: publish partial table */','!memcmp(profiles,&zero,sizeof(zero))'),
        ('destroy_after_stop_failure','network','stopped != ESP_OK && stopped != ESP_ERR_WIFI_NOT_STARTED',
         'false','atomic_load(&s_network_start)==NETWORK_RETAINED'),
        ('missing_runtime_rollback','network','network_runtime_stop(2000)',
         'ESP_OK','runtime_stops==1&&releases==1&&!s_station_netif.handle'),
    ]
    for name, unit, old, new, assertion in mutations:
        contents = network_unit if unit == 'network' else startup_unit
        assert contents.count(old) == 1, name
        changed = contents.replace(old, new, 1)
        run_case(name, changed if unit == 'network' else network_unit,
                 changed if unit == 'startup' else startup_unit, assertion)
    old='if (s_have_credentials) esp_wifi_connect();'
    assert c3_unit.count(old)==1
    run_case('donor_empty_file_uses_retained_driver_profile', network_unit, startup_unit,
             'connect_calls==0U', c3_unit.replace(old,'esp_wifi_connect();',1))
    (out / 'network.inc').write_text(network_unit)
    (out / 'startup.inc').write_text(startup_unit)
    (out / 'c3-events.inc').write_text(c3_unit)
    report['command'] = command
    report['passed'] = True
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS', len(mutations)+1, 'targeted semantic controls')


if __name__ == '__main__':
    main()
