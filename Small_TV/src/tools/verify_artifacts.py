"""Refresh validation metadata from the tested archive and a full passing suite."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ARCHIVE = REPO / 'firmware/development/small-tv-esp32c2-reconstructed'
BUILD = REPO / '.build/small-tv-esp32c2'
sys.path.insert(0, str(ROOT/'tests'))
from photo_frame_contract import validate_photo_frames
from photo_controls_contract import validate_photo_brightness, validate_photo_controls, validate_photo_reinit
from photo_settings_contract import validate_photo_settings
from advanced_qemu import validate_advanced
from http_body_contract import validate_http_body, validate_http_body_guards
from concurrency_contract import validate_concurrency, validate_concurrency_guards
from boot_state_contract import validate_boot_state, validate_boot_rejections
from wifi_fallback_contract import validate_wifi_fallback, validate_wifi_fallback_guards
from netif_roles_contract import validate_netif_roles, rejection_checks as netif_role_rejections
from ap_services_contract import validate_ap_services, rejection_checks as ap_service_rejections
from jpeg_dht_contract import validate_dht, validate_photo_dht, rejection_checks as dht_rejections
from jpeg_header_contract import validate_headers, rejection_checks as header_rejections
from jpeg_header_http_contract import validate_photo_headers
from jpeg_selector_contract import validate_selector_evidence, validate_photo_selectors


def read(path):
    """Accept PowerShell JSON with or without its UTF-8 BOM."""
    return json.loads(path.read_text(encoding='utf-8-sig'))


def require(condition, message):
    """Reject stale evidence even when Python runs with assertions disabled."""
    if not condition:
        raise ValueError(message)


def main():
    """Derive sizes/counts dynamically; never turn missing checks into successes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, default=ROOT / 'tests/functional-validation.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'validation.json')
    args = parser.parse_args()
    suite, manifest = read(args.suite), read(ARCHIVE / 'manifest.json')
    require(suite['passed'] and suite['automatic_profile'] == 'host_machine_qemu',
            'A full passing suite is required')
    groups = {row['name']: row['result'] for row in suite['groups'] if row['status'] == 'passed'} \
        if 'groups' in suite else suite
    for name in ('report_aggregation', 'native', 'platform', 'frontend', 'integrity', 'timezone_sources', 'machine', 'machine_control', 'machine_classic', 'machine_weather', 'machine_calendar', 'machine_jpeg', 'machine_jpeg_inputs', 'machine_timezones', 'machine_time_state', 'machine_text', 'machine_network', 'qemu_profile', 'qemu'):
        require(name in groups and groups[name]['passed'], 'Missing passing group: ' + name)
    for item in suite['test_inputs']:
        require(hashlib.sha256((REPO / item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Test changed since execution: ' + item['file'])
    for item in groups['frontend']['inputs']:
        require(hashlib.sha256((REPO / item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Frontend changed since execution: ' + item['file'])
    for item in groups['timezone_sources']['inputs']:
        require(hashlib.sha256((REPO / item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Timezone source/updater changed since execution: ' + item['file'])
    for item in groups['qemu_profile']['inputs']:
        require(hashlib.sha256((REPO / item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Profile/firmware wiring changed since execution: ' + item['file'])
    profile_input = next(row for row in groups['qemu_profile']['inputs'] if row['file'].endswith('/small-tv-c2.json'))
    require(profile_input['sha256'] == groups['qemu']['profile_sha256'] and
            all(groups['qemu']['helper_sha256'][key] == value for key, value in groups['qemu_profile']['compiler_sha256'].items()),
            'Profile validation and firmware used different profile/compiler inputs')
    app = (ARCHIVE / 'app.bin').read_bytes()
    app_sha = hashlib.sha256(app).hexdigest()
    validate_boot_state(groups['qemu'], {'app_sha256': app_sha,
        'elf_sha256': hashlib.sha256((BUILD / 'small_tv_reconstructed.elf').read_bytes()).hexdigest(),
        'observer_test_sha256': groups['qemu']['boot_observer_test_sha256']})
    validate_boot_rejections(groups['qemu'])
    wifi_wait = groups['qemu']['wifi_fallback_http']
    validate_wifi_fallback(wifi_wait, {'app_sha256':app_sha,
        'source_sha256':manifest['source_sha256'],'qemu_sha256':groups['qemu']['qemu_sha256'],
        'native_elf_sha256':hashlib.sha256((BUILD/'small_tv_reconstructed.elf').read_bytes()).hexdigest(),
        'test_sha256':hashlib.sha256((ROOT/'tests/wifi_fallback_qemu.py').read_bytes()).hexdigest()})
    validate_wifi_fallback_guards(wifi_wait)
    # New role gates share the suite/publisher's validators; a green outer
    # report must not authorize missing task, cache, scan or complete LCD data.
    role_expected = {'app_sha256': app_sha, 'source_sha256': manifest['source_sha256'],
        'qemu_sha256': groups['qemu']['qemu_sha256'],
        'native_elf_sha256': hashlib.sha256((BUILD / 'small_tv_reconstructed.elf').read_bytes()).hexdigest()}
    netif_roles = groups['qemu']['netif_roles_http']
    netif_expected = {**role_expected, 'test_sha256': {
        name: hashlib.sha256((ROOT / 'tests' / name).read_bytes()).hexdigest()
        for name in ('netif_roles_qemu.py', 'netif_observer.py', 'wifi_fallback_qemu.py')}}
    validate_netif_roles(netif_roles, netif_expected)
    require(netif_roles['contract_checks'] == netif_role_rejections(netif_roles, netif_expected) and
            groups['qemu']['netif_observer_unit'] == {'passed': True, 'tests': 7}, 'Missing netif evidence guards')
    require(groups['qemu']['raw_flash_observer_unit'] == {'passed': True, 'tests': 5},
            'Missing raw erase/program persistence observer controls')
    ap_services = groups['qemu']['ap_services_http']
    ap_expected = {**role_expected, 'test_sha256': hashlib.sha256((ROOT / 'tests/ap_services_qemu.py').read_bytes()).hexdigest()}
    validate_ap_services(ap_services, ap_expected)
    require(ap_services['contract_checks'] == ap_service_rejections(ap_services, ap_expected), 'Missing AP service guards')
    for gate in (netif_roles, ap_services):
        for filename, expected in gate['inputs_sha256'].items():
            require(hashlib.sha256(Path(filename).read_bytes()).hexdigest() == expected,
                    'Role input changed after execution: ' + Path(filename).name)
    body_http = groups['qemu']['body_http']
    validate_http_body(body_http, {'app_sha256': app_sha, 'source_sha256': manifest['source_sha256'],
        'qemu_sha256': groups['qemu']['qemu_sha256'],
        'test_sha256': hashlib.sha256((ROOT / 'tests/http_body_qemu.py').read_bytes()).hexdigest()})
    validate_http_body_guards(body_http)
    concurrency_http = groups['qemu']['concurrency_http']
    validate_concurrency(concurrency_http, {'app_sha256': app_sha, 'source_sha256': manifest['source_sha256'],
        'qemu_sha256': groups['qemu']['qemu_sha256'],
        'native_elf_sha256': hashlib.sha256((BUILD / 'small_tv_reconstructed.elf').read_bytes()).hexdigest(),
        'test_sha256': hashlib.sha256((ROOT / 'tests/concurrency_qemu.py').read_bytes()).hexdigest(),
        'formatter_sha256': hashlib.sha256((ROOT / 'tests/photo_protocol.py').read_bytes()).hexdigest()})
    validate_concurrency_guards(concurrency_http)
    require(suite['app_sha256'] == app_sha and suite['source_sha256'] == manifest['source_sha256'],
            'Suite tested a different application/source archive')
    state, network = groups['machine_time_state'], groups['qemu']['time_http']
    jpeg_inputs = groups['machine_jpeg_inputs']
    require(jpeg_inputs['passed'] and jpeg_inputs['inputs_unchanged'] and
            jpeg_inputs['app_sha256'] == app_sha and
            jpeg_inputs['source_sha256'] == manifest['source_sha256'] and
            jpeg_inputs['native_elf_sha256'] == state['native_elf_sha256'] and
            len(jpeg_inputs['valid']) == 8 and len(jpeg_inputs['invalid']) == 12 and
            all(row['passed'] for row in jpeg_inputs['valid'] + jpeg_inputs['invalid']),
            'Additional JPEG gate omitted cases or used different inputs')
    huffman = jpeg_inputs['huffman']
    require(huffman['passed'] and len(huffman['valid']) == 4 and len(huffman['invalid']) == 17 and
            {row['name'] for row in huffman['valid']} ==
                {'one-bit', 'long-dc', 'long-ac', 'long-dc-and-ac'} and
            {row['name'] for row in huffman['invalid']} ==
                {'dc-depth-1'} | {'ac-depth-' + str(depth) for depth in range(1, 17)} and
            all(row['passed'] for row in huffman['valid'] + huffman['invalid']) and
            not any(row['decoder_started'] for row in huffman['invalid']),
            'Huffman gate omitted depth/boundary cases or accepted an impossible tree')
    validate_dht(jpeg_inputs['dht'], {key: jpeg_inputs[key] for key in
        ('app_sha256', 'source_sha256', 'native_elf_sha256', 'factory_elf_sha256')})
    dht_guards = jpeg_inputs['dht_rejection_checks']
    require(len(dht_guards) == 7 and all(row['passed'] for row in dht_guards) and
            dht_guards == dht_rejections(jpeg_inputs['dht']), 'JPEG DHT evidence rejection controls did not pass')
    validate_headers(jpeg_inputs['headers'], {key: jpeg_inputs[key] for key in
        ('app_sha256', 'source_sha256', 'native_elf_sha256', 'factory_elf_sha256')})
    header_guards = jpeg_inputs['header_rejection_checks']
    require(len(header_guards) == 7 and all(row['passed'] for row in header_guards) and
            header_guards == header_rejections(jpeg_inputs['headers']), 'JPEG header evidence rejection controls did not pass')
    validate_selector_evidence(jpeg_inputs['selectors'], {key: jpeg_inputs[key] for key in
        ('app_sha256', 'source_sha256', 'native_elf_sha256', 'factory_elf_sha256')}, jpeg_inputs['selector_rejection_checks'])
    for item in jpeg_inputs['test_inputs']:
        require(hashlib.sha256((REPO / item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Additional JPEG fixture/adapter changed: ' + item['file'])
    for name in ('startup_wait', 'weather_wait', 'advanced_http', 'photo_http', 'photo_frames', 'photo_brightness', 'photo_controls', 'photo_reinit', 'photo_settings'):
        gate = groups['qemu'][name]
        gate_source = gate['source_sha256'] if name in ('photo_frames', 'photo_brightness', 'photo_controls', 'photo_reinit', 'photo_settings') else gate['sources']['source_sha256']
        require(gate['passed'] and gate['inputs_unchanged'] and gate['app_sha256'] == app_sha and
                gate['native_elf_sha256'] == state['native_elf_sha256'] and
                gate['qemu_sha256'] == groups['qemu']['qemu_sha256'] and
                gate['helper_sha256'] == groups['qemu']['helper_sha256'] and
                gate_source == manifest['source_sha256'],
                'Guest observer tested different inputs: ' + name)
    startup, held_weather = groups['qemu']['startup_wait'], groups['qemu']['weather_wait']
    photo = groups['qemu']['photo_http']
    advanced = groups['qemu']['advanced_http']
    validate_advanced(advanced)
    require(advanced['profile_sha256'] == groups['qemu']['profile_sha256'],
            'Advanced editor used a different hardware profile')
    for item in advanced['test_inputs']:
        require(hashlib.sha256((REPO/item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Advanced editor test changed: '+item['file'])
    for item in advanced['artifact_inputs']:
        require(hashlib.sha256((ARCHIVE/item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Advanced editor artifact changed: '+item['file'])
    frames = groups['qemu']['photo_frames']
    validate_photo_frames(frames)
    require(len(frames['contract_checks']) == 14 and all(row['passed'] for row in frames['contract_checks']),
            'Photo frame contract rejection checks did not pass')
    idle_brightness = groups['qemu']['photo_brightness']
    validate_photo_brightness(idle_brightness)
    controls_http = groups['qemu']['photo_controls']
    validate_photo_controls(controls_http)
    reinit_http = groups['qemu']['photo_reinit']
    validate_photo_reinit(reinit_http)
    photo_settings = groups['qemu']['photo_settings']
    validate_photo_settings(photo_settings)
    require(len(photo_settings['contract_checks']) == 14 and all(row['passed'] for row in photo_settings['contract_checks']) and
            photo_settings['profile_sha256'] == groups['qemu']['profile_sha256'] and
            photo_settings['factory_elf_sha256'] == state['factory_elf_sha256'],
            'Photo in-flight settings omitted rejection checks or used different inputs')
    for item in photo_settings['test_inputs']:
        require(hashlib.sha256((REPO/item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Photo in-flight setting input changed: '+item['file'])
    require(reinit_http['profile_sha256'] == groups['qemu']['profile_sha256'],
            'Photo active commands used a different hardware profile')
    for item in reinit_http['test_inputs']:
        require(hashlib.sha256((REPO/item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Photo active command input changed since execution: '+item['file'])
    require(controls_http['profile_sha256'] == groups['qemu']['profile_sha256'],
            'Photo theme commands used a different hardware profile')
    for item in controls_http['test_inputs']:
        require(hashlib.sha256((REPO/item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Photo theme command input changed since execution: '+item['file'])
    require(idle_brightness['profile_sha256'] == groups['qemu']['profile_sha256'],
            'Photo brightness used a different hardware profile')
    for item in idle_brightness['test_inputs']:
        require(hashlib.sha256((REPO/item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Photo brightness input changed since execution: '+item['file'])
    require(frames['profile_sha256'] == groups['qemu']['profile_sha256'] and
            frames['factory_elf_sha256'] == state['factory_elf_sha256'] and
            frames['normalized']['app_sha256'] == frames['app_sha256'] and
            frames['normalized']['native_elf_sha256'] == frames['native_elf_sha256'] and
            frames['normalized']['factory_elf_sha256'] == frames['factory_elf_sha256'],
            'Photo frames or normalized scenes used different inputs')
    for item in frames['test_inputs']:
        require(hashlib.sha256((REPO/item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Photo frame input changed since execution: '+item['file'])
    photo_checks = {'valid_gray_published', 'malformed_huffman_rejected', 'reserved_dht_rejected', 'busy_and_retry_policy',
                    'valid_published', 'download_exact', 'first_boot_no_panic', 'owned_flash_changed',
                    'cold_boot_new_vm', 'cold_boot_metadata', 'cold_boot_download_exact', 'cold_boot_no_panic',
                    'immediate_finish_cut_bounded', 'immediate_finish_new_vm', 'immediate_finish_persisted',
                    'interrupted_slot_unpublished', 'interrupted_start_cut_bounded', 'immediate_finish_no_panic',
                    'interrupted_boot_new_vm', 'interrupted_photo_hidden', 'new_upload_after_interruption',
                    'interrupted_boot_no_panic', 'header_fields_rejected', 'custom_component_ids_published',
                    'selector_uploads_valid', 'selector_missing_rejected'}
    require(photo['profile_sha256'] == groups['qemu']['profile_sha256'] and
            set(photo['checks']) == photo_checks and all(photo['checks'].values()) and
            photo['invalid']['finish_status'] == 400 and photo['invalid']['metadata'] == {'exists': False, 'size': 0} and
            all(0 <= photo[key] < .5 for key in
                ('finish_response_to_stop_guest_seconds', 'start_response_to_stop_guest_seconds')),
            'Real photo upload/download/cold-boot checks omitted stages or accepted invalid data')
    validate_photo_dht(photo)
    validate_photo_headers(photo)
    validate_photo_selectors(photo)
    require(0 <= startup['ready_wait_guest_seconds'] <= .5 and startup['different_colors'] >= 2,
            'Ready startup clock was delayed or blank')
    require(held_weather['during']['request_state'] & held_weather['compiled_running_mask'] and
            held_weather['during']['wait_guest_seconds'] <= 1.5 and
            held_weather['during']['rgb_sha256'] != held_weather['before']['rgb_sha256'],
            'Clock did not advance during the held weather request')
    require(groups['qemu']['field_http']['flows']['reconstructed']['checks']['responsive_refresh_phase'],
            'Live field scroll was not checked during the held reply')
    require(state['app_sha256'] == app_sha and state['source_sha256'] == manifest['source_sha256'],
            'Time-state gate tested a different archive')
    require(network['passed'] and network['qemu_sha256'] == groups['qemu']['qemu_sha256'] and
            network['layout']['elf_sha256'] == state['native_elf_sha256'],
            'Real SNTP gate tested different machine/emulator inputs')
    text_gate, text_network = groups['machine_text'], groups['qemu']['text_http']
    station = groups['machine_network']
    require(station['app_sha256'] == app_sha and station['source_sha256'] == manifest['source_sha256']
            and station['native_elf_sha256'] == state['native_elf_sha256'],
            'Station event gate tested a different application/source/ELF')
    require(set(station['event_cases']) == {'factory','native'} and
            all(len(cases) == 2 and all(row['passed'] for row in cases)
                for cases in station['event_cases'].values()) and
            len(station['factory_dispatch']) == 16 and all(row['passed'] for row in station['factory_dispatch']),
            'Station event/dispatch gate omitted required cases')
    require(text_gate['app_sha256'] == app_sha and text_gate['source_sha256'] == manifest['source_sha256']
            and text_gate['native_elf_sha256'] == state['native_elf_sha256']
            and text_gate['native_elf_sha256'] == hashlib.sha256((BUILD/'small_tv_reconstructed.elf').read_bytes()).hexdigest(),
            'Text machine gate tested a different application/source/ELF')
    require(groups['qemu']['inputs_unchanged'] and text_network['passed']
            and text_network['qemu_sha256'] == groups['qemu']['qemu_sha256']
            and text_network['cache_layout']['elf_sha256'] == text_gate['native_elf_sha256'],
            'Real UTF-8 gate tested different machine/emulator inputs')
    require(text_gate['font_source_sha256'] == text_network['font_source_sha256'] == hashlib.sha256(
        (ROOT/'third_party/spleen/spleen-6x12.bdf').read_bytes()).hexdigest(), 'Unicode font source changed')
    require(app == (BUILD / 'small_tv_reconstructed.bin').read_bytes(), 'Build and archive differ')
    regional = groups['qemu']['regional_http']
    require(regional['passed'] and regional['qemu_sha256'] == groups['qemu']['qemu_sha256'] and
            regional['settings_layout']['elf_sha256'] == state['native_elf_sha256'],
            'Regional settings gate tested a different executable/emulator')
    completed = groups['qemu']['completed_scenes']
    require(completed['passed'] and completed['app_sha256'] == app_sha and
            completed['native_elf_sha256'] == state['native_elf_sha256'] and
            completed['qemu_sha256'] == groups['qemu']['qemu_sha256'],
            'Completed-frame gate tested a different executable/emulator')
    calendar_network = groups['qemu']['calendar_http']
    require(calendar_network['passed'] and calendar_network['app_sha256'] == app_sha and
            calendar_network['source_sha256'] == manifest['source_sha256'] and
            calendar_network['native_elf_sha256'] == state['native_elf_sha256'] and
            calendar_network['qemu_sha256'] == groups['qemu']['qemu_sha256'] and
            calendar_network['profile_sha256'] == groups['qemu']['profile_sha256'] and
            calendar_network['helper_sha256'] == groups['qemu']['helper_sha256'],
            'Natural calendar gate tested a different application/source/executable/emulator')
    require(len(calendar_network['requirements']) == 14 and
            set(calendar_network['flows']) == {'original','reconstructed'} and
            all(flow['passed'] and all(flow['checks'].values()) and
                flow.get('transitions',len(flow.get('cases',[]))) == 42 and
                flow.get('completed_frames',sum(len(row['samples']) for row in flow.get('cases',[]))) == 84
                for flow in calendar_network['flows'].values()),
            'Natural calendar gate omitted a required theme/transition/frame')
    for item in calendar_network['test_inputs']:
        require(hashlib.sha256((REPO/item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Calendar input changed since execution: '+item['file'])
    generated = BUILD / 'verification-resources'
    subprocess.run([sys.executable, str(ROOT / 'tools/prepare_resources.py'), '--output', str(generated)], check=True)
    source = read(generated / 'source-manifest.json')
    require(source == read(ARCHIVE / 'source-manifest.json') and
            source['aggregate_sha256'] == manifest['source_sha256'], 'Production sources changed after build')
    require((generated / 'assets.bin').read_bytes() == (ARCHIVE / 'assets.bin').read_bytes(),
            'Generated assets differ from the archive')
    subprocess.run([sys.executable, str(ROOT / 'tests/artifact_test.py'),
                    '--output', str(generated / 'integrity.json')], check=True)
    integrity = read(generated / 'integrity.json')
    require(integrity['passed'] and integrity['app_sha256'] == app_sha, 'Artifact integrity failed')
    size = json.loads(subprocess.check_output([sys.executable, '-m', 'esp_idf_size', '--format', 'json2',
                                              str(BUILD / 'small_tv_reconstructed.map')], text=True))
    diram = next(row for row in size['layout'] if row['name'] == 'DIRAM')
    table = (ARCHIVE / 'partition-table.bin').read_bytes()
    partitions = {}
    for position in range(0, len(table), 32):
        entry = table[position:position + 32]
        if struct.unpack_from('<H', entry)[0] != 0x50aa:
            break  # MD5/footer and all bounds were independently checked above.
        _, _, _, _, length, label, _ = struct.unpack('<HBBII16sI', entry)
        partitions[label.split(b'\0')[0].decode()] = length
    symbols = read(ROOT / 'symbol-map.json')
    definitions = re.compile(r'(?m)^[A-Za-z_][\w \t*]*?\b(\w+)\s*\([^;{}]*\)\s*\{')
    function_count, marked_count = 0, 0
    for path in (ROOT / 'app').rglob('*.c'):
        text = path.read_text()
        for match in definitions.finditer(text):
            comment = text[match.end():].lstrip()
            require(comment.startswith('/*'), 'Missing entry comment: ' + match[1])
            function_count += 1
            if re.search(r'FIXED_FACTORY|FIXED_RECONSTRUCTION|REQUESTED_CHANGE', comment.split('*/', 1)[0]):
                marked_count += 1
    classic = groups['machine_classic']
    report = read(args.output) if args.output.exists() else {}
    report['limitations'] = [item for item in report.get('limitations', [])
                             if not item.startswith('The C-port assistant ')] + [
        'The C-port assistant reports decoded control flow; it does not emit or verify an executable C implementation.']
    report.update(target=manifest['target'], date=suite['finished_utc'][:10], sdk_revision=manifest['idf_revision'],
                  source_sha256=manifest['source_sha256'], app_sha256=app_sha, app_bytes=len(app),
                  app_partition_bytes=partitions['factory'], app_partition_free_bytes=partitions['factory'] - len(app),
                  media_bytes=partitions['assets'], original_routes=34, registered_routes=len(groups['native']['routes']),
                  reference_functions=len(symbols['functions']), named_globals=len(symbols['globals']),
                  named_local_parameter_aliases=sum(len(item['names']) for item in symbols['locals']),
                  host_result=f"PASS: {groups['native']['checks']} checks; all registered HTTP contracts",
                  asset_pack_matches_sanitized_exports=True, compiled_source_hashes_match_archive=True,
                  partition_table_md5_valid=True, original_flash_dump_unchanged=True,
                  static_diram_bytes=diram['used'], linker_diram_remaining_bytes=diram['free'],
                  runtime_memory_measured=False, hardware_tested=False, device_flashed=False, ota=False,
                  production_functions_with_entry_comments=function_count, production_functions_with_correction_markers=marked_count,
                  correction_markers_document='CORRECTION_MARKERS.md',
                  host_platform_scenarios=len(groups['platform']['cases']),
                  host_platform_checks=sum(row['checks'] for row in groups['platform']['cases']),
                  machine_classic_report='../qemu/parity/classic-validation.json',
                  machine_classic_cases=classic['renderer_cases'] if isinstance(classic['renderer_cases'], int) else len(classic['renderer_cases']),
                  machine_animation_transitions=classic.get('animation_transitions', len(classic.get('animation', {}).get('cases', []))),
                  machine_backlight_comparisons=groups['machine_control']['backlight']['comparisons'],
                  machine_glyph_geometry_checks=len(classic['glyph_geometry_checks']))
    weather = groups['machine_weather']
    require(weather['app_sha256'] == app_sha and weather['source_sha256'] == manifest['source_sha256'],
            'Weather gate tested different application/source inputs')
    report['machine_weather_report'] = '../qemu/parity/weather-render-validation.json'
    report['machine_weather_cases'] = sum(weather['case_counts'].values()) if 'case_counts' in weather else len(weather['cases'])
    calendar = groups['machine_calendar']
    require(calendar['app_sha256']==app_sha and calendar['source_sha256']==manifest['source_sha256'],
            'Calendar gate tested different application/source inputs')
    require(groups['qemu']['field_http']['passed'],'Real QEMU field update/scroll gate failed')
    report['machine_calendar_report'] = '../qemu/parity/calendar-validation.json'
    report['machine_calendar_cases'] = calendar['renderer_cases'] if 'renderer_cases' in calendar else len(calendar['cases'])
    jpeg = groups['machine_jpeg']
    require(jpeg['complete_asset_set'] and jpeg['app_sha256']==app_sha and
            jpeg['source_sha256']==manifest['source_sha256'], 'JPEG gate did not test the complete current image set')
    report['machine_jpeg_report'] = '../qemu/parity/jpeg-validation.json'
    report['machine_jpeg_images'] = jpeg['decoded_images'] if 'decoded_images' in jpeg else len(jpeg['cases'])
    report['machine_jpeg_error_checks'] = jpeg['error_validation_checks'] if 'error_validation_checks' in jpeg else len(jpeg['errors'])
    timezones = groups['machine_timezones']
    require(timezones['complete_country_set'] and timezones['app_sha256']==app_sha and
            timezones['source_sha256']==manifest['source_sha256'], 'Timezone gate tested different inputs')
    require(timezones['timezone_manifest_sha256']==hashlib.sha256(
        (ROOT/'resources/timezones/manifest.json').read_bytes()).hexdigest(), 'Timezone source data changed')
    report['machine_timezone_report'] = '../qemu/parity/timezone-validation.json'
    report['machine_timezone_countries'] = timezones['countries'] if isinstance(timezones['countries'],int) else len(timezones['countries'])
    report['machine_timezone_comparisons'] = timezones['comparisons']
    report['qemu_field_report'] = '../qemu/field-http-validation.json'
    report['machine_time_state_report'] = '../qemu/parity/time-state-validation.json'
    report['machine_network_event_traces'] = sum(len(cases) for cases in station['event_cases'].values())
    report['machine_network_factory_dispatch_states'] = len(station['factory_dispatch'])
    report['machine_time_state_factory_cases'] = len(state['factory_cases'])
    report['machine_time_state_native_checks'] = len(state['native_cases'])
    report['qemu_time_report'] = '../qemu/time-http-validation.json'
    report['qemu_time_native_stages'] = len(network['flows']['reconstructed']['stages'])
    report['machine_text_report'] = '../qemu/parity/text-validation.json'
    report['machine_text_case_counts'] = text_gate['case_counts'] if 'case_counts' in text_gate else {
        key: len(text_gate[key]) for key in ('glyph_checks','render_cases','decode_checks','prefix_checks','literal_factory')}
    report['unicode_glyphs'] = text_gate['unicode_glyphs']
    report['qemu_text_report'] = '../qemu/text-http-validation.json'
    report['qemu_text_native_cases'] = len(text_network['flows']['reconstructed']['cases'])
    report['qemu_regional_report'] = '../qemu/regional-http-validation.json'
    report['qemu_regional_keys'] = len(regional['flows']['reconstructed']['cases'])
    report['settings_version'] = 2
    report['settings_nvs_bytes'] = regional['settings_layout']['size']
    report['settings_nvs_v1_migration_verified'] = regional['nvs_migration']['passed']
    report['qemu_completed_scene_report'] = '../qemu/completed-scenes-validation.json'
    report['qemu_completed_frames'] = sum(len(flow['samples']) for scene in completed['scenes'].values() for flow in scene.values())
    report['qemu_photo_completed_frames'] = sum(len(flow['samples']) for flows in frames['flows'].values() for flow in flows.values())
    report['normalized_photo_cases'] = len(frames['normalized']['cases'])
    report['normalized_complete_scene_cases'] = len(completed['normalized']['cases'])
    report['qemu_calendar_transport_report'] = '../qemu/calendar-transport-validation.json'
    report['qemu_calendar_transitions'] = sum(flow.get('transitions',len(flow.get('cases',[])))
                                            for flow in calendar_network['flows'].values())
    report['qemu_calendar_completed_frames'] = sum(flow.get('completed_frames',sum(len(row['samples']) for row in flow.get('cases',[])))
                                                 for flow in calendar_network['flows'].values())
    report['work_status'] = 'Reconstructed firmware; confirmed factory corrections are marked and tested'
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Verified application {app_sha}: {len(app)} bytes, {partitions["factory"] - len(app)} bytes free')
    print(f'Entry comments: {function_count}; correction markers: {marked_count}; DIRAM: {diram["used"]} bytes')


if __name__ == '__main__':
    main()
