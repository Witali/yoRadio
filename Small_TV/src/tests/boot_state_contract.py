"""Require linked-ELF guest readiness instead of optional UART INFO messages."""
import copy
import math
import re

SIZES = {'connected': 1, 'ap_active': 1, 'last_station_address': 4, 'time_synced': 1,
         's_microseconds_offset': 8, 's_correction_us': 8}
CHECKS = ('application_runtime_ready', 'rom_and_bootloader', 'wifi_associated',
          'station_dhcp', 'sntp_notification_received', 'runtime_ready_after_reset',
          'reset_reboots', 'no_panic_or_watchdog', 'no_panic_after_reset',
          'lcd_has_content', 'animation_updates', 'ntp_reply_sent', 'guest_clock_set_by_sntp',
          'clock_recovered_after_reset', 'source_flash_unchanged', 'source_artifacts_unchanged')
CHECKS += ('display_ready_after_reset', 'network_recovered_after_reset')
REJECTIONS = ('missing_units', 'failed_units', 'omitted_units', 'wrong_unit_source',
              'wrong_converter', 'wrong_vm_helper', 'wrong_elf', 'missing_observation',
              'disconnected', 'reset_not_synced', 'reset_wrong_dhcp', 'station_is_ap',
              'outside_ram', 'wrong_bool_size', 'missing_symbols', 'wrong_qemu',
              'reset_not_ready', 'uart_only_readiness', 'wrong_layout_helper',
              'coarse_ntp_only', 'missing_ntp', 'wrong_ntp_base', 'wrong_ntp_expectation',
              'reset_missing_ntp', 'reset_wrong_ntp_base', 'reset_old_ntp_reply',
              'wrong_sdk_clock_layout', 'wrong_clock_object_size', 'wrong_sdk_offset')
REJECTIONS += ('missing_display_unit', 'wrong_display_helper', 'missing_display_observation',
               'blank_reset_display', 'late_reset_display', 'wrong_final_frame',
               'missing_display_check', 'mixed_subsystem_decision', 'no_new_rom_boot')


def require(value, message):
    """Keep rejection active with Python optimization enabled."""
    if not value:
        raise ValueError(message)


def validate_reset_display(boot):
    """Require bounded panel evidence, independently of DHCP/SNTP and ROM banners."""
    observation = boot.get('reset_display_observation', {})
    require(observation.get('passed') is True and
            observation.get('method') == 'bounded_post_reset_framebuffer', 'Missing reset panel observation')
    require(type(observation.get('nonzero_bytes')) is int and
            1000 < observation['nonzero_bytes'] <= 240 * 240 * 3, 'Reset panel is blank/incomplete')
    samples = observation.get('samples', [])
    require(type(observation.get('polls')) is int and observation['polls'] == len(samples) > 0,
            'Missing reset panel samples')
    for key, maximum in (('host', 30), ('guest', 5)):
        elapsed, deadline = observation.get(key + '_seconds'), observation.get(key + '_timeout')
        require(type(elapsed) in (int, float) and type(deadline) in (int, float) and
                math.isfinite(elapsed) and math.isfinite(deadline) and
                0 <= elapsed < deadline <= maximum, 'Late reset display: ' + key)
    require(re.fullmatch('[0-9a-f]{64}', observation.get('frame_sha256', '')) is not None,
            'Missing reset frame identity')
    for key in ('host_seconds', 'guest_seconds', 'nonzero_bytes', 'frame_sha256'):
        require(samples[-1].get(key) == observation[key], 'Final reset frame mismatch')
    groups = boot.get('checks_by_subsystem', {})
    display = groups.get('display', {})
    require(display.get('passed') is True and
            display.get('checks', {}).get('display_ready_after_reset') is True,
            'Missing independent display decision')
    require(not any(key in display['checks'] for key in
                    ('station_dhcp', 'wifi_associated', 'sntp_notification_received', 'network_recovered_after_reset')),
            'Network flags entered display acceptance')
    return True


def validate_reset_network(boot):
    """Consume network readiness without accepting display pixels as network proof."""
    network = boot.get('checks_by_subsystem', {}).get('network', {})
    require(network.get('passed') is True and
            network.get('checks', {}).get('network_recovered_after_reset') is True,
            'Missing independent network decision')
    require(not any(key in network['checks'] for key in
                    ('lcd_240x240', 'lcd_has_content', 'animation_updates', 'display_ready_after_reset')),
            'Display pixels entered network acceptance')
    return True


def validate_reset_boot(boot):
    """Consume the new ROM boot count independently of network and panel state."""
    rom = boot.get('boot_observation', {})
    require(type(rom.get('rom_boots_before_reset')) is int and
            type(rom.get('rom_boots_after_reset')) is int and
            rom['rom_boots_after_reset'] > rom['rom_boots_before_reset'] >= 1,
            'Reset did not produce a new ROM boot')
    return True


def validate_ntp_observation(boot, name):
    """Recompute SDK UTC in guest time, including reset-relative timer corrections."""
    sample = boot.get(name, {})
    require(sample.get('method') in ('model_response_timestamp', 'diagnostic_wire_timestamp'),
            'Missing exact NTP response timestamp: ' + name)
    if sample['method'] == 'diagnostic_wire_timestamp':
        require(boot.get('qemu_diagnostics_enabled') is True, 'NTP diagnostic source was disabled')
    for key in ('response_count', 'server_epoch', 'sent_virtual_us', 'boot_time_us', 'virtual_us', 'systimer_ticks'):
        require(type(sample.get(key)) is int and sample[key] >= 0, 'Invalid NTP scalar: ' + key)
    require(sample['response_count'] > 0, 'No NTP response was generated')
    for key in ('rtc_hrt_offset_us', 'system_correction_us', 'since_boot_us'):
        require(type(sample.get(key)) is int, 'Invalid SDK timekeeping scalar: ' + key)
    for key in ('actual_utc_seconds', 'expected_utc_seconds', 'difference_seconds'):
        require(type(sample.get(key)) in (int, float) and math.isfinite(sample[key]), 'Invalid RTC base: ' + key)
    since_boot = sample['systimer_ticks'] * 5 // 52 + sample['rtc_hrt_offset_us'] + sample['system_correction_us']
    actual = (sample['boot_time_us'] + since_boot) / 1e6
    expected = sample['server_epoch'] + (sample['virtual_us'] - sample['sent_virtual_us']) / 1e6
    require(sample['since_boot_us'] == since_boot and
            abs(sample['actual_utc_seconds'] - actual) < 1e-6 and
            abs(sample['expected_utc_seconds'] - expected) < 1e-6 and
            abs(sample['difference_seconds'] - (actual - expected)) < 1e-6 and
            abs(actual - expected) < 1, 'SDK UTC differs from NTP response: ' + name)
    return sample


def validate_boot_state(qemu, expected):
    """Reject stale ELF, missing unit controls and incomplete station/reset state."""
    unit = qemu.get('boot_observer_unit', {})
    helpers = qemu['helper_sha256']
    require(unit.get('passed') is True and unit.get('tests', 0) >= 12 and
            not unit.get('errors') and not unit.get('failures'), 'Missing ELF observation unit controls')
    require(unit.get('source_sha256') == expected['observer_test_sha256'] == qemu.get('boot_observer_test_sha256') and
            unit.get('converter_sha256') == helpers.get('esp_elf.py') and
            unit.get('vm_helper_sha256') == helpers.get('small_tv_vm.py'), 'Boot observer source mismatch')
    boot = qemu['boot_reset']['reconstructed']
    display_unit = qemu.get('display_observer_unit', {})
    require(display_unit.get('passed') is True and display_unit.get('display_tests', 0) >= 9 and
            display_unit.get('isolation_tests', 0) >= 3 and
            display_unit.get('source_sha256') == qemu.get('display_observer_test_sha256') and
            display_unit.get('display_helper_sha256') == helpers.get('small_tv_display.py') and
            display_unit.get('vm_helper_sha256') == helpers.get('small_tv_vm.py'),
            'Missing independent display/isolation unit controls')
    validate_reset_display(boot)
    validate_reset_display(qemu['boot_reset']['original'])
    for row in qemu['boot_reset'].values():
        validate_reset_network(row)
        validate_reset_boot(row)
    require(boot.get('passed') is True and boot['qemu_sha256'] == qemu['qemu_sha256'] and
            boot['firmware'] == 'reconstructed', 'Boot used a different VM or did not pass')
    image = next(row for row in boot['prepared']['sources']['images'] if row['file'] == 'app.bin')
    require(image['sha256'] == expected['app_sha256'], 'Boot used a different application')
    require(all(boot['checks'].get(name) is True for name in CHECKS), 'Missing actual boot/reset acceptance condition')
    observation = boot.get('runtime_observation', {})
    layout = observation.get('layout', {})
    require(layout.get('elf_sha256') == expected['elf_sha256'] and
            layout.get('converter_sha256') == helpers['esp_elf.py'] and
            layout.get('vm_helper_sha256') == helpers['small_tv_vm.py'], 'Boot layout used a different ELF/converter/helper')
    require(boot.get('clock_layout') == layout, 'Clock used a different SDK object layout')
    require(type(boot.get('qemu_diagnostics_enabled')) is bool, 'Missing QEMU diagnostic capability')
    first = validate_ntp_observation(boot, 'ntp_observation')
    reset = validate_ntp_observation(boot, 'reset_ntp_observation')
    require(reset['response_count'] > first['response_count'], 'Reset reused the previous NTP response')
    symbols = layout['symbols']
    require(set(symbols) == set(SIZES), 'Missing observed SDK/application objects')
    ranges = []
    for name, size in SIZES.items():
        row = symbols[name]
        require(row['size'] == size and 0x3fca0000 <= row['address'] < row['address'] + size <= 0x3fce0000,
                'Invalid boot observation RAM/ABI: ' + name)
        require(not any(row['address'] < end and row['address'] + size > begin for begin, end in ranges),
                'Overlapping boot observation objects')
        ranges.append((row['address'], row['address'] + size))
    for name in ('before_reset', 'after_reset'):
        state = observation[name]
        require(state['connected'] is True and state['time_synced'] is True and
                state['ap_active'] is False and state['station_address'] == '10.0.2.15',
                'Station/DHCP/SNTP not observed: ' + name)
    return True


def rejection_checks(qemu, expected):
    """Mutate a captured passing boot report, proving each control can reject."""
    validate_boot_state(qemu, expected)
    base = ('boot_reset', 'reconstructed')
    observation = base + ('runtime_observation',)
    mutations = {
        'missing_units': (('boot_observer_unit',), {}),
        'failed_units': (('boot_observer_unit', 'passed'), False),
        'omitted_units': (('boot_observer_unit', 'tests'), 0),
        'wrong_unit_source': (('boot_observer_unit', 'source_sha256'), 'bad'),
        'wrong_converter': (('boot_observer_unit', 'converter_sha256'), 'bad'),
        'wrong_vm_helper': (('boot_observer_unit', 'vm_helper_sha256'), 'bad'),
        'wrong_elf': (observation + ('layout', 'elf_sha256'), 'bad'),
        'missing_observation': (base + ('runtime_observation',), {}),
        'disconnected': (observation + ('before_reset', 'connected'), False),
        'reset_not_synced': (observation + ('after_reset', 'time_synced'), False),
        'reset_wrong_dhcp': (observation + ('after_reset', 'station_address'), '192.168.43.1'),
        'station_is_ap': (observation + ('before_reset', 'ap_active'), True),
        'outside_ram': (observation + ('layout', 'symbols', 'connected', 'address'), 0x42000000),
        'wrong_bool_size': (observation + ('layout', 'symbols', 'connected', 'size'), 4),
        'missing_symbols': (observation + ('layout', 'symbols'), {}),
        'wrong_qemu': (base + ('qemu_sha256',), 'bad'),
        'reset_not_ready': (base + ('checks', 'runtime_ready_after_reset'), False),
        'uart_only_readiness': (base + ('checks', 'application_runtime_ready'), False),
        'wrong_layout_helper': (observation + ('layout', 'vm_helper_sha256'), 'bad'),
        'coarse_ntp_only': (base + ('ntp_observation', 'method'), 'actual_sync_flag_and_host_epoch'),
        'missing_ntp': (base + ('ntp_observation',), {}),
        'wrong_ntp_base': (base + ('ntp_observation', 'actual_utc_seconds'), 0),
        'wrong_ntp_expectation': (base + ('ntp_observation', 'expected_utc_seconds'), 0),
        'reset_missing_ntp': (base + ('reset_ntp_observation',), {}),
        'reset_wrong_ntp_base': (base + ('reset_ntp_observation', 'actual_utc_seconds'), 0),
        'reset_old_ntp_reply': (base + ('reset_ntp_observation', 'response_count'),
                               qemu['boot_reset']['reconstructed']['ntp_observation']['response_count']),
        'wrong_sdk_clock_layout': (base + ('clock_layout',), {}),
        'wrong_clock_object_size': (observation + ('layout', 'symbols', 's_correction_us', 'size'), 4),
        'wrong_sdk_offset': (base + ('ntp_observation', 'system_correction_us'), 0),
        'missing_display_unit': (('display_observer_unit',), {}),
        'wrong_display_helper': (('display_observer_unit', 'display_helper_sha256'), 'bad'),
        'missing_display_observation': (base + ('reset_display_observation',), {}),
        'blank_reset_display': (base + ('reset_display_observation', 'nonzero_bytes'), 0),
        'late_reset_display': (base + ('reset_display_observation', 'guest_seconds'), 5),
        'wrong_final_frame': (base + ('reset_display_observation', 'frame_sha256'), '0' * 64),
        'missing_display_check': (base + ('checks', 'display_ready_after_reset'), False),
        'mixed_subsystem_decision': (base + ('checks_by_subsystem', 'network', 'checks', 'display_ready_after_reset'), True),
        'no_new_rom_boot': (base + ('boot_observation', 'rom_boots_after_reset'), 1),
    }
    require(set(mutations) == set(REJECTIONS), 'Boot rejection controls changed unexpectedly')
    passed = {}
    for label, (path, value) in mutations.items():
        changed = copy.deepcopy(qemu)
        node = changed
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        try:
            validate_boot_state(changed, expected)
        except (ValueError, KeyError, StopIteration, TypeError):
            passed[label] = True
        else:
            raise ValueError('Boot consumer accepted invalid report: ' + label)
    return {'passed': True, 'checks': len(passed), 'rejections': passed}


def validate_boot_rejections(qemu):
    """Require the actual consumer-negative controls in published full evidence."""
    checks = qemu.get('boot_observer_contract_checks', {})
    require(checks.get('passed') is True and checks.get('checks') == len(REJECTIONS) and
            set(checks.get('rejections', {})) == set(REJECTIONS) and
            all(value is True for value in checks['rejections'].values()), 'Missing boot consumer rejection controls')
