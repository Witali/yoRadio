"""Require real role lists, retained synthetic driver NVS and a working AP scan."""
from copy import deepcopy
from pathlib import Path

from netif_observer import FACTORY_SHA, require, require_role


def validate_netif_roles(report, expected):
    """Reject stale identities or partial role/scan evidence despite a green flag."""
    try:
        require(report['passed'] is True and report['inputs_unchanged'] is True, 'Netif run did not pass')
        for key in ('app_sha256', 'native_elf_sha256', 'qemu_sha256'):
            require(report[key] == expected[key], 'Netif identity differs: ' + key)
        require(report['factory_full_flash_sha256'] == FACTORY_SHA and
                report['native_layout']['elf_sha256'] == expected['native_elf_sha256'], 'Netif layout identity differs')
        for name, sha in expected['test_sha256'].items():
            matches = [value for path, value in report['inputs_sha256'].items() if Path(path).name == name]
            require(matches == [sha], 'Netif observer source differs: ' + name)
        require(set(report['flows']) == {variant + '-' + role for variant in ('original', 'reconstructed')
                                        for role in ('station', 'setup')}, 'Missing netif role flow')
        for variant in ('original', 'reconstructed'):
            station, setup = (report['flows'][variant + '-' + role] for role in ('station', 'setup'))
            for is_station, row in ((True, station), (False, setup)):
                require(all(row[key] is True for key in
                            ('passed', 'executable_media_unchanged', 'uart_clean', 'expected_http_page')),
                        'Missing role/HTTP/immutable-code acceptance')
                require_role(row['netifs'], is_station)
                state = row['ready']
                require(state in row['observations'] and state['rom_boots'] == 1 and
                        state['mode_raw'] == state['mode_ram'] == (1 if is_station else 2) and
                        state['connected'] is is_station and state['ap_active'] is (not is_station),
                        'Selected role was not actually observed')
            require(setup['seeded_mode_only'] is True and station['sources'] == setup['sources'] and
                    setup['seed_provenance']['driver_nvs_source'] == 'original-station' and
                    setup['seed_provenance']['only_nvs_replaced_before_mode_change'] is True,
                    'Setup seed/source did not preserve the station fixture')
            credentials = report['synthetic_driver_nvs']
            require(credentials == setup['retained_driver_nvs'], 'Setup did not retain the exact SDK credentials')
            require(len(credentials['entries']) == 2 and {row['key'] for row in credentials['entries']} ==
                    {'sta.ssid', 'sta.apinfo'}, 'Missing retained driver SSID payloads')
            for entry in credentials['entries']:
                require(entry['namespace'] == 'nvs.net80211' and all(entry[key] is True for key in
                        ('header_crc_matches', 'data_crc_matches', 'contains_expected_synthetic_ssid')),
                        'Driver credential CRC/payload validation failed')
            require(setup['scan'] == {'status': 200, 'expected_public_ssid_present': True}, 'Setup scan failed')
            require_role(setup['netifs_after_scan'], False)
            after = setup['after_scan']
            require(after['ap_active'] is True and after['connected'] is False and after['rom_boots'] == 1 and
                    after['mode_ram'] == after['mode_raw'] == 2, 'Scan changed the selected role')
            if variant == 'original':
                require(all(state['factory_station_state'] == 5 and state['factory_apsta_got_ip_event'] is False
                            for state in (setup['ready'], after)), 'Factory AP init/GOT_IP was not observed')
            else:
                app = next(row for row in station['sources']['images'] if row['file'] == 'app.bin')
                require(app['sha256'] == expected['app_sha256'] and
                        station['sources']['source_sha256'] == expected['source_sha256'], 'Native VM image differs')
    except (KeyError, TypeError, StopIteration) as error:
        raise ValueError('Incomplete netif role evidence') from error


def rejection_checks(report, expected):
    """Prove that missing roles, extra interfaces, bad NVS and scan failures cannot pass."""
    validate_netif_roles(report, expected)
    mutations = [('failed', ('passed',), False), ('changed-inputs', ('inputs_unchanged',), False),
        ('wrong-app', ('app_sha256',), '0' * 64), ('wrong-elf', ('native_elf_sha256',), '0' * 64),
        ('wrong-qemu', ('qemu_sha256',), '0' * 64), ('missing-factory', ('flows', 'original-setup'), None),
        ('empty-netifs', ('flows', 'reconstructed-setup', 'netifs'), []),
        ('extra-station', ('flows', 'reconstructed-setup', 'netifs'),
                         [{'key': 'WIFI_AP_DEF'}, {'key': 'WIFI_STA_DEF'}]),
        ('changed-code', ('flows', 'original-setup', 'executable_media_unchanged'), False),
        ('missing-http', ('flows', 'reconstructed-station', 'expected_http_page'), False),
        ('lost-nvs', ('flows', 'original-setup', 'retained_driver_nvs', 'sha256'), '0' * 64),
        ('bad-nvs-crc', ('flows', 'original-setup', 'retained_driver_nvs', 'entries', 0, 'data_crc_matches'), False),
        ('scan-failed', ('flows', 'reconstructed-setup', 'scan', 'status'), 503),
        ('scan-extra-station', ('flows', 'original-setup', 'netifs_after_scan'),
                              [{'key': 'WIFI_AP_DEF'}, {'key': 'WIFI_STA_DEF'}]),
        ('factory-got-ip', ('flows', 'original-setup', 'after_scan', 'factory_apsta_got_ip_event'), True),
        ('factory-unobserved', ('flows', 'original-setup', 'after_scan', 'factory_apsta_got_ip_event'), None),
        ('scan-reset', ('flows', 'reconstructed-setup', 'after_scan', 'rom_boots'), 2)]
    checks = []
    for name, path, value in mutations:
        changed = deepcopy(report)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate_netif_roles(changed, expected)
        except ValueError:
            checks.append({'name': name, 'passed': True})
        else:
            raise AssertionError('Netif contract accepted invalid evidence: ' + name)
    return checks
