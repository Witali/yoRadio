"""Qualify checked CYD netif construction over selected pinned SDK bodies.

Runs the unchanged complete production wrapper plus actual v6.0.2 attach,
post-attach, driver create/destroy, default callback registration/rollback and
public clear bodies. Netif/lwIP allocation and destruction, event registry,
shutdown registry, Wi-Fi RX callback detach and field layout are explicit host
seams. Faults wrap the actual setter; the actual attach still publishes its
driver before post_attach, and actual cleanup frees that driver even on error.
This is not target ABI, scheduler, lwIP/DHCP or RF/hardware qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def host(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def execute(command):
    result = subprocess.run((['wsl.exe', '--exec'] if sys.platform == 'win32' else []) + command,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return result.returncode, result.stdout


def function(source, name):
    match = re.search(r'^[^;{}\n]*\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', source, re.M)
    assert match, name
    position = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[position] == '{') - (source[position] == '}')
        position += 1
    return source[match.start():position] + '\n'


def macro(source, name):
    lines = source.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if re.match(r'^#define\s+' + re.escape(name) + r'\b', line):
            result = line
            while lines[index].rstrip().endswith('\\'):
                index += 1
                result += lines[index]
            return result
    raise AssertionError(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sdk-root', type=Path)
    args = parser.parse_args()
    common = Path(subprocess.check_output(['git', 'rev-parse', '--path-format=absolute',
                                          '--git-common-dir'], cwd=ROOT, text=True).strip())
    sdk = (args.sdk_root or common.parent / '.idf/v6.0.2').resolve()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=sdk, text=True).strip()
    assert revision == '7101770dc6db2667b3c477cc31365dd1acd6db4e', revision
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    main_dir = ROOT / 'idf/esp32-cyd2usb-native/main'
    fixture = ROOT / 'tests/native/network_netif'
    sources = [Path(__file__).resolve(), fixture / 'test.c', fixture / 'stubs.h',
               main_dir / 'network_netif.c', main_dir / 'network_netif.h',
               ROOT / 'idf/esp32-cyd2usb-native/build-c3-transfer/config/sdkconfig.h']
    sdk_paths = ['components/esp_wifi/src/wifi_default.c',
                 'components/esp_wifi/src/wifi_netif.c',
                 'components/esp_netif/lwip/esp_netif_lwip.c',
                 'components/esp_netif/include/esp_netif_defaults.h',
                 'components/esp_wifi/include/esp_wifi_default.h',
                 'components/esp_wifi/include/esp_wifi_netif.h']
    report = {'passed': False, 'scope': __doc__, 'physical_hardware': False,
              'sanitizers': ['ASan', 'UBSan'], 'sdk_revision': revision,
              'source_sha256': {}, 'sdk_sha256': {}, 'generated_sha256': {},
              'negative_controls': {}}
    for path in sources:
        data = path.read_bytes()
        relative = path.relative_to(ROOT)
        snapshot = out / 'sources' / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(data)
        report['source_sha256'][relative.as_posix()] = hashlib.sha256(data).hexdigest()
    for relative in sdk_paths:
        data = (sdk / relative).read_bytes()
        snapshot = out / 'sdk-sources' / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(data)
        report['sdk_sha256'][relative] = hashlib.sha256(data).hexdigest()
    frozen = out / 'sources'
    sdk_frozen = out / 'sdk-sources'
    defaults = (sdk_frozen / sdk_paths[0]).read_text()
    driver = (sdk_frozen / sdk_paths[1]).read_text()
    netif = (sdk_frozen / sdk_paths[2]).read_text()
    config = (sdk_frozen / sdk_paths[3]).read_text()
    profile = (frozen / sources[-1].relative_to(ROOT)).read_text()
    assert '#define CONFIG_ESP_WIFI_SOFTAP_SUPPORT 1' in profile
    assert '#define CONFIG_LWIP_IPV4 1' in profile
    for option in ['CONFIG_ESP_WIFI_NAN_SYNC_ENABLE', 'CONFIG_LWIP_IGMP', 'CONFIG_LWIP_IPV6']:
        assert '#define ' + option + ' 1' not in profile, option
    generated = {
        'sdk-netif.inc': ''.join(function(netif, name) for name in
            ['esp_netif_get_io_driver', 'esp_netif_set_driver_config', 'esp_netif_attach']),
        'sdk-driver-struct.inc': re.search(r'struct wifi_netif_driver\s*\{.*?\n\};', driver, re.S).group(0) + '\n',
        'sdk-driver.inc': ''.join(function(driver, name) for name in
            ['wifi_driver_start', 'esp_wifi_destroy_if_driver', 'esp_wifi_create_if_driver']),
        'sdk-default.inc': ''.join(function(defaults, name) for name in
            ['clear_default_wifi_handlers', 'set_default_wifi_handlers',
             'esp_wifi_set_default_wifi_sta_handlers', 'esp_wifi_set_default_wifi_ap_handlers',
             'esp_wifi_clear_default_wifi_driver_and_handlers', 'disconnect_and_destroy',
             'create_and_attach', 'esp_netif_attach_wifi', 'esp_netif_attach_wifi_station',
             'esp_netif_attach_wifi_ap']),
        'sdk-default-macros.inc': ''.join(macro(config, name) for name in
            ['ESP_NETIF_DEFAULT_WIFI_AP', 'ESP_NETIF_DEFAULT_WIFI_STA',
             'ESP_NETIF_BASE_DEFAULT_WIFI_AP', 'ESP_NETIF_BASE_DEFAULT_WIFI_STA',
             'ESP_NETIF_NETSTACK_DEFAULT_WIFI_AP', 'ESP_NETIF_NETSTACK_DEFAULT_WIFI_STA']),
    }
    for name, contents in generated.items():
        (out / name).write_text(contents)
        report['generated_sha256'][name] = hashlib.sha256((out / name).read_bytes()).hexdigest()
    for name in ['esp_err.h', 'esp_netif.h', 'esp_wifi_default.h']:
        (out / name).write_text('#pragma once\n#include "stubs.h"\n')
    loader = (frozen / main_dir.relative_to(ROOT) / 'network_netif.c').read_text()
    command = ['gcc', '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-Wno-cast-function-type', '-fsanitize=address,undefined',
               '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-I' + host(out), '-I' + host(frozen / main_dir.relative_to(ROOT)),
               '-I' + host(frozen / fixture.relative_to(ROOT)),
               host(frozen / fixture.relative_to(ROOT) / 'test.c'), '-o', host(out / 'netif')]

    def run_case(name, source, marker=None):
        (out / 'network_netif-production.c').write_text(source)
        (out / (name + '-source.c')).write_text(source)
        status, log = execute(command)
        (out / (name + '-build.log')).write_bytes(log)
        assert status == 0, log.decode(errors='replace')
        status, log = execute(['env', 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                               'UBSAN_OPTIONS=halt_on_error=1', host(out / 'netif')])
        (out / (name + '.log')).write_bytes(log)
        assert b'ERROR: AddressSanitizer' not in log and b'runtime error:' not in log, log
        if marker is None:
            assert status == 0, log.decode(errors='replace')
            report['positive'] = log.decode().strip()
            print(log.decode(), end='')
        else:
            assert status == 80 and ('SEMANTIC_FAILURE:' + marker + ':').encode() in log, (name, status, log)
            report['negative_controls'][name] = {'detected': True, 'exit_status': status,
                                                'expected_marker': marker}

    run_case('positive', loader)
    mutations = [
        ('ignore-attach-failure', '    if (result == ESP_OK) result = ap ?',
         '    result = ap ?', 'driver_allocation_failure_propagates'),
        ('ignore-handler-failure', 'result = ap ? esp_wifi_set_default_wifi_ap_handlers()\n                                     : esp_wifi_set_default_wifi_sta_handlers();',
         '(void)(ap ? esp_wifi_set_default_wifi_ap_handlers()\n                   : esp_wifi_set_default_wifi_sta_handlers());',
         'registration_failure_propagates_original_error'),
        ('skip-partial-rollback', '    if (result != ESP_OK) (void)network_netif_release(out);',
         '    /* Deliberately retain an unmarked partial object. */',
         'failed_create_has_no_usable_owner'),
        ('destroy-after-clear-error', '    if (result != ESP_OK) {',
         '    if (false) {', 'never_destroy_after_failed_clear'),
        ('retry-failed-sdk-clear', '    if (owner->cleanup_failed) return ESP_ERR_INVALID_STATE;',
         '    if (owner->cleanup_failed && !owner->handle) return ESP_ERR_INVALID_STATE;',
         'failed_cleanup_never_repeated'),
        ('swap-sta-ap-config', 'config = ap ?', 'config = !ap ?', 'checked_create_success'),
    ]
    for name, old, new, marker in mutations:
        assert loader.count(old) == 1, name
        run_case(name, loader.replace(old, new, 1), marker)
    (out / 'network_netif-production.c').write_text(loader)
    report['command'] = command
    report['passed'] = True
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS', len(mutations), 'exact semantic negative controls')


if __name__ == '__main__':
    main()
