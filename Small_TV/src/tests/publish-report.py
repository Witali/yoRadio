"""Publish compact verified functional evidence without VM logs, private state or images."""
import argparse
import hashlib
import json
from pathlib import Path
from photo_frame_contract import validate_photo_frames
from photo_controls_contract import validate_photo_brightness, validate_photo_controls, validate_photo_reinit
from photo_settings_contract import validate_photo_settings
from advanced_qemu import validate_advanced
from http_body_contract import validate_http_body, validate_http_body_guards
from concurrency_contract import validate_concurrency, validate_concurrency_guards
from boot_state_contract import validate_boot_state, validate_boot_rejections

ROOT = Path(__file__).resolve().parents[3]


def main():
    """Require a full passing automated run and unchanged test/firmware inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('functional-validation.json'))
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding='utf-8-sig'))
    groups = {row['name']: row for row in report['groups']}
    required = ('report_aggregation', 'native', 'platform', 'frontend', 'integrity', 'timezone_sources', 'machine', 'machine_control', 'machine_classic', 'machine_weather', 'machine_calendar', 'machine_jpeg', 'machine_jpeg_inputs', 'machine_timezones', 'machine_time_state', 'machine_text', 'machine_network', 'qemu_profile', 'qemu')
    if not report['passed'] or report['automatic_profile'] != 'host_machine_qemu':
        raise ValueError('Only a complete passing automated run may replace the published result')
    if any(groups[name]['status'] != 'passed' for name in required):
        raise ValueError('An automated group did not pass')
    for row in report['test_inputs']:
        data = (ROOT / row['file']).read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Test changed after the run: ' + row['file'])
    for row in groups['frontend']['result']['inputs']:
        if hashlib.sha256((ROOT / row['file']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Frontend changed after the run: ' + row['file'])
    for row in groups['timezone_sources']['result']['inputs']:
        if hashlib.sha256((ROOT / row['file']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Timezone source/updater changed after the run: ' + row['file'])
    app = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed/app.bin'
    if hashlib.sha256(app.read_bytes()).hexdigest() != report['app_sha256']:
        raise ValueError('Firmware changed after the run')
    machine = groups['machine']['result']
    controls = groups['machine_control']['result']
    classic = groups['machine_classic']['result']
    weather = groups['machine_weather']['result']
    calendar = groups['machine_calendar']['result']
    jpeg = groups['machine_jpeg']['result']
    jpeg_inputs = groups['machine_jpeg_inputs']['result']
    timezones = groups['machine_timezones']['result']
    time_state = groups['machine_time_state']['result']
    text = groups['machine_text']['result']
    network = groups['machine_network']['result']
    if (not jpeg_inputs['passed'] or not jpeg_inputs['inputs_unchanged'] or
            jpeg_inputs['app_sha256'] != report['app_sha256'] or
            jpeg_inputs['source_sha256'] != report['source_sha256'] or
            jpeg_inputs['native_elf_sha256'] != text['native_elf_sha256'] or
            jpeg_inputs['factory_elf_sha256'] != text['factory_elf_sha256'] or
            len(jpeg_inputs['valid']) != 8 or len(jpeg_inputs['invalid']) != 12 or
            any(not row['passed'] for row in jpeg_inputs['valid'] + jpeg_inputs['invalid'])):
        raise ValueError('Additional JPEG gate omitted cases or used different executables')
    huffman = jpeg_inputs['huffman']
    if (not huffman['passed'] or len(huffman['valid']) != 4 or len(huffman['invalid']) != 17 or
            {row['name'] for row in huffman['valid']} !=
                {'one-bit', 'long-dc', 'long-ac', 'long-dc-and-ac'} or
            {row['name'] for row in huffman['invalid']} !=
                {'dc-depth-1'} | {'ac-depth-' + str(depth) for depth in range(1, 17)} or
            any(not row['passed'] for row in huffman['valid'] + huffman['invalid']) or
            any(row['decoder_started'] for row in huffman['invalid'])):
        raise ValueError('Huffman gate omitted depth/boundary cases or accepted an impossible tree')
    for item in jpeg_inputs['test_inputs']:
        if hashlib.sha256((ROOT / item['file']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Additional JPEG fixture/adapter changed: ' + item['file'])
    if (network['app_sha256'] != report['app_sha256'] or
            network['source_sha256'] != report['source_sha256'] or
            network['native_elf_sha256'] != text['native_elf_sha256'] or
            network['factory_elf_sha256'] != text['factory_elf_sha256'] or
            set(network['event_cases']) != {'factory','native'} or
            any({row['case'] for row in cases} != {'new-dhcp-lease','reconnect-resets-retries'}
                or len(cases) != 2 or any(not row['passed'] for row in cases)
                for cases in network['event_cases'].values()) or
            len(network['factory_dispatch']) != 16 or
            {(row['theme'],row['station_state']) for row in network['factory_dispatch']} !=
                {(theme,state) for theme in range(4) for state in (0,1,2,5)} or
            any(not row['passed'] for row in network['factory_dispatch'])):
        raise ValueError('Station event/dispatch gate omitted states or used different executables')
    if not timezones['complete_country_set'] or timezones['legacy_only'] or len(timezones['countries']) != 109:
        raise ValueError('Timezone gate did not execute every recovered country key')
    if not jpeg['complete_asset_set'] or len(jpeg['cases']) != 107:
        raise ValueError('JPEG gate did not execute every public image')
    if any(data['app_sha256'] != report['app_sha256'] for data in (machine, controls, classic, weather, calendar, jpeg, timezones, time_state, text, groups['integrity']['result'])):
        raise ValueError('Groups tested different applications')
    qemu = groups['qemu']['result']
    profile = groups['qemu_profile']['result']
    for row in profile['inputs']:
        if hashlib.sha256((ROOT / row['file']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Profile/firmware wiring changed after execution: ' + row['file'])
    profile_input = next(row for row in profile['inputs'] if row['file'].endswith('/small-tv-c2.json'))
    if (profile_input['sha256'] != qemu['profile_sha256'] or
            any(qemu['helper_sha256'][key] != value for key, value in profile['compiler_sha256'].items())):
        raise ValueError('Profile validation and firmware used different profile/compiler inputs')
    if not qemu['inputs_unchanged']:
        raise ValueError('Emulator or helpers changed during execution')
    validate_boot_state(qemu, {
        'app_sha256': report['app_sha256'], 'elf_sha256': text['native_elf_sha256'],
        'observer_test_sha256': qemu['boot_observer_test_sha256']})
    validate_boot_rejections(qemu)
    for name in ('startup_wait', 'weather_wait', 'advanced_http', 'photo_http', 'photo_frames', 'photo_brightness', 'photo_controls', 'photo_reinit', 'photo_settings'):
        gate = qemu[name]
        if (not gate['passed'] or not gate['inputs_unchanged'] or
                gate['app_sha256'] != report['app_sha256'] or
                gate['native_elf_sha256'] != text['native_elf_sha256'] or
                gate['qemu_sha256'] != qemu['qemu_sha256'] or gate['helper_sha256'] != qemu['helper_sha256']):
            raise ValueError('Guest observer failed or used different inputs: ' + name)
        items = gate['test_inputs']
        items = items.items() if isinstance(items, dict) else ((item['file'], item['sha256']) for item in items)
        for path, sha in items:
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != sha:
                raise ValueError('Guest observer changed: ' + path)
    startup, held_weather = qemu['startup_wait'], qemu['weather_wait']
    photo = qemu['photo_http']
    advanced = qemu['advanced_http']
    validate_advanced(advanced)
    body_http = qemu['body_http']
    validate_http_body(body_http, {'app_sha256': report['app_sha256'], 'source_sha256': report['source_sha256'],
        'qemu_sha256': qemu['qemu_sha256'],
        'test_sha256': hashlib.sha256((ROOT / 'Small_TV/src/tests/http_body_qemu.py').read_bytes()).hexdigest()})
    validate_http_body_guards(body_http)
    concurrency_http = qemu['concurrency_http']
    validate_concurrency(concurrency_http, {'app_sha256': report['app_sha256'], 'source_sha256': report['source_sha256'],
        'qemu_sha256': qemu['qemu_sha256'], 'native_elf_sha256': text['native_elf_sha256'],
        'test_sha256': hashlib.sha256((ROOT / 'Small_TV/src/tests/concurrency_qemu.py').read_bytes()).hexdigest(),
        'formatter_sha256': hashlib.sha256((ROOT / 'Small_TV/src/tests/photo_protocol.py').read_bytes()).hexdigest()})
    validate_concurrency_guards(concurrency_http)
    if advanced['profile_sha256'] != qemu['profile_sha256'] or advanced['source_sha256'] != report['source_sha256']:
        raise ValueError('Advanced editor tested different profile/source inputs')
    for item in advanced['artifact_inputs']:
        if hashlib.sha256((app.parent/item['file']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Advanced editor artifact changed: '+item['file'])
    frames = qemu['photo_frames']
    validate_photo_frames(frames)
    if len(frames['contract_checks']) != 12 or any(not row['passed'] for row in frames['contract_checks']):
        raise ValueError('Photo frame contract rejection checks did not pass')
    idle_brightness = qemu['photo_brightness']
    validate_photo_brightness(idle_brightness)
    controls_http = qemu['photo_controls']
    validate_photo_controls(controls_http)
    reinit_http = qemu['photo_reinit']
    validate_photo_reinit(reinit_http)
    photo_settings = qemu['photo_settings']
    validate_photo_settings(photo_settings)
    if (len(photo_settings['contract_checks']) != 14 or any(not row['passed'] for row in photo_settings['contract_checks']) or
            photo_settings['profile_sha256'] != qemu['profile_sha256'] or photo_settings['source_sha256'] != report['source_sha256'] or
            photo_settings['factory_elf_sha256'] != text['factory_elf_sha256']):
        raise ValueError('Photo in-flight settings omitted rejection checks or used different inputs')
    if reinit_http['profile_sha256'] != qemu['profile_sha256'] or reinit_http['source_sha256'] != report['source_sha256']:
        raise ValueError('Photo active commands tested different profile/source inputs')
    if controls_http['profile_sha256'] != qemu['profile_sha256'] or controls_http['source_sha256'] != report['source_sha256']:
        raise ValueError('Photo theme commands tested different profile/source inputs')
    if idle_brightness['profile_sha256'] != qemu['profile_sha256'] or idle_brightness['source_sha256'] != report['source_sha256']:
        raise ValueError('Photo brightness tested a different profile/source')
    if (frames['profile_sha256'] != qemu['profile_sha256'] or
            frames['source_sha256'] != report['source_sha256'] or
            frames['factory_elf_sha256'] != text['factory_elf_sha256'] or
            frames['normalized']['app_sha256'] != frames['app_sha256'] or
            frames['normalized']['native_elf_sha256'] != frames['native_elf_sha256'] or
            frames['normalized']['factory_elf_sha256'] != frames['factory_elf_sha256']):
        raise ValueError('Photo frames or normalized scenes used different inputs')
    photo_checks = {'valid_gray_published', 'malformed_huffman_rejected', 'busy_and_retry_policy',
                    'valid_published', 'download_exact', 'first_boot_no_panic', 'owned_flash_changed',
                    'cold_boot_new_vm', 'cold_boot_metadata', 'cold_boot_download_exact', 'cold_boot_no_panic',
                    'immediate_finish_cut_bounded', 'immediate_finish_new_vm', 'immediate_finish_persisted',
                    'interrupted_slot_unpublished', 'interrupted_start_cut_bounded', 'immediate_finish_no_panic',
                    'interrupted_boot_new_vm', 'interrupted_photo_hidden', 'new_upload_after_interruption',
                    'interrupted_boot_no_panic'}
    if (photo['profile_sha256'] != qemu['profile_sha256'] or set(photo['checks']) != photo_checks or
            not all(photo['checks'].values()) or photo['invalid']['finish_status'] != 400 or
            photo['invalid']['metadata'] != {'exists': False, 'size': 0} or
            any(not 0 <= photo[key] < .5 for key in
                ('finish_response_to_stop_guest_seconds', 'start_response_to_stop_guest_seconds'))):
        raise ValueError('Real photo upload/download/cold-boot checks omitted a stage or accepted invalid data')
    if not 0 <= startup['ready_wait_guest_seconds'] <= .5 or startup['different_colors'] < 2:
        raise ValueError('Ready clock still waits on startup or its first frame is blank')
    if (not held_weather['during']['request_state'] & held_weather['compiled_running_mask'] or
            held_weather['during']['wait_guest_seconds'] > 1.5 or
            held_weather['during']['rgb_sha256'] == held_weather['before']['rgb_sha256']):
        raise ValueError('Clock did not advance while the weather reply was withheld')
    if not qemu['http_initial_setup']['passed']:
        raise ValueError('Real HTTP initial setup did not pass')
    uri_targets = qemu['uri_targets_http']
    if (not uri_targets['passed'] or not uri_targets['inputs_unchanged'] or
            uri_targets['app_sha256'] != report['app_sha256'] or
            uri_targets['source_sha256'] != report['source_sha256'] or
            uri_targets['qemu_sha256'] != qemu['qemu_sha256'] or
            set(uri_targets['variants']) != {'original', 'reconstructed'} or
            any(not row['vm_stopped'] or not row['no_panic'] or not row['checks'] or
                not all(row['checks'].values()) for row in uri_targets['variants'].values())):
        raise ValueError('URI request-target comparison omitted a firmware or used different inputs')
    if not qemu['weather_http']['passed']:
        raise ValueError('Real weather HTTP/value/LCD comparison did not pass')
    fields = qemu['field_http']
    if not fields['passed'] or fields['qemu_sha256'] != qemu['qemu_sha256']:
        raise ValueError('Real field HTTP/scroll comparison did not pass on this emulator')
    if not fields['flows']['reconstructed']['checks']['responsive_refresh_phase']:
        raise ValueError('Field scroll was not checked during a held weather reply')
    time_http = qemu['time_http']
    if (not time_http['passed'] or time_http['qemu_sha256'] != qemu['qemu_sha256']
            or time_http['layout']['elf_sha256'] != time_state['native_elf_sha256']):
        raise ValueError('Real SNTP comparison used a different emulator or compiled time-state image')
    required_time_stages = {'before_first_reply', 'synchronized_2024', 'server_2_2025',
                            'year-jump', 'backward-leap-day', 'post-2038',
                            'reset_before_notification', 'reset_recovered'}
    if not required_time_stages <= set(time_http['flows']['reconstructed']['stages']):
        raise ValueError('Real SNTP gate omitted a required calendar/reset stage')
    if time_state['source_sha256'] != report['source_sha256']:
        raise ValueError('Time-state gate used a different source archive')
    text_http = qemu['text_http']
    if (not text_http['passed'] or text_http['qemu_sha256'] != qemu['qemu_sha256']
            or text_http['cache_layout']['elf_sha256'] != text['native_elf_sha256']
            or text['native_elf_sha256'] != time_state['native_elf_sha256']
            or text['source_sha256'] != report['source_sha256']
            or text_http['font_source_sha256'] != text['font_source_sha256']):
        raise ValueError('UTF-8 machine/HTTP gates used different inputs')
    font = ROOT / 'Small_TV/src/third_party/spleen/spleen-6x12.bdf'
    if hashlib.sha256(font.read_bytes()).hexdigest() != text['font_source_sha256']:
        raise ValueError('UTF-8 font source changed after execution')
    if (len(text['glyph_checks']) != (text['unicode_glyphs'] + text['ascii_glyphs_per_height']) * 3
            or any(not row['passed'] for key in ('glyph_checks', 'render_cases', 'decode_checks', 'prefix_checks', 'literal_factory') for row in text[key])):
        raise ValueError('UTF-8 gate omitted glyphs or failed a scalar/prefix/render case')
    required_text_cases = {'cyrillic', 'unicode-scroll', 'latin', 'unsupported-cjk', 'split-label-budget'}
    for variant in ('original', 'reconstructed'):
        flow = text_http['flows'][variant]
        if not flow['passed'] or not flow['checks']['no_panic'] or {row['case'] for row in flow['cases']} != required_text_cases:
            raise ValueError('UTF-8 HTTP gate omitted required healthy-flow cases')
    native_text = text_http['flows']['reconstructed']
    if (not native_text['checks']['native_glyphs_width_scroll_guards']
            or any(not row['frame']['passed'] for row in native_text['cases'])
            or not next(row for row in native_text['cases'] if row['case'] == 'unicode-scroll')['scroll']['passed']
            or not text_http['factory_utf8_city_fault']['passed']):
        raise ValueError('UTF-8 HTTP gate omitted native field/scroll guards or literal factory fault')
    regional = qemu['regional_http']
    if (not regional['passed'] or regional['qemu_sha256'] != qemu['qemu_sha256'] or
            regional['settings_layout']['elf_sha256'] != text['native_elf_sha256']):
        raise ValueError('Regional settings gate used a different executable or emulator')
    regional_keys = {row['country'] for row in json.loads(
        (ROOT/'Small_TV/src/resources/timezones/manifest.json').read_text())['countries']
                     if '-' in row['country']}
    for variant in ('original','reconstructed'):
        flow = regional['flows'][variant]
        if (not flow['passed'] or not all(flow['checks'].values()) or
                {row['key'] for row in flow['cases']} != regional_keys or
                not flow['raw_import']['passed'] or not flow['cold_boot']['passed'] or
                any(not row['passed'] or not row['raw_persistence'] for row in flow['cases'])):
            raise ValueError('Regional settings gate omitted keys/import/persistence/calendar')
    if (not regional['flows']['reconstructed']['maximum_input']['passed'] or
            regional['flows']['reconstructed']['invalid_inputs_rejected'] != 3 or
            not regional['nvs_migration']['passed'] or not all(regional['nvs_migration']['checks'].values()) or
            any(not row['matches_iana'] for row in regional['flows']['reconstructed']['cases']) or
            any(not row['weather_key_preserved'] for row in regional['flows']['reconstructed']['cases'])):
        raise ValueError('Regional settings gate omitted maximum inputs/cache/rejection checks')
    calendar_http = qemu['calendar_http']
    from calendar_qemu import requirements
    calendar_requirements = requirements()
    if (not calendar_http['passed'] or calendar_http['app_sha256'] != report['app_sha256'] or
            calendar_http['source_sha256'] != report['source_sha256'] or
            calendar_http['native_elf_sha256'] != text['native_elf_sha256'] or
            calendar_http['qemu_sha256'] != qemu['qemu_sha256'] or
            calendar_http['profile_sha256'] != qemu['profile_sha256'] or
            calendar_http['helper_sha256'] != qemu['helper_sha256'] or
            calendar_http['requirements'] != calendar_requirements or
            set(calendar_http['flows']) != {'original','reconstructed'}):
        raise ValueError('Calendar transport matrix used different inputs or omitted requirements')
    for item in calendar_http['test_inputs']:
        if hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Calendar test/reference changed since execution')
    expected_cases = {(theme, case['name']) for theme in ('classic','simple','dial') for case in calendar_requirements}
    for variant, flow in calendar_http['flows'].items():
        if (not flow['passed'] or not all(flow['checks'].values()) or len(flow['cases']) != len(expected_cases) or
                {(row['theme'],row['name']) for row in flow['cases']} != expected_cases):
            raise ValueError('Calendar transport matrix omitted a theme or transition')
        for row in flow['cases']:
            required_case = next(case for case in calendar_requirements if case['name'] == row['name'])
            if (any(row[key] != value for key,value in required_case.items()) or not row['passed'] or
                    not row['natural_transition_without_resync'] or len(row['samples']) != 2 or
                    not row['boundary_utc']-10 <= row['samples'][0]['packet_utc'] < row['boundary_utc'] or
                    not row['boundary_utc']+2 <= row['samples'][1]['packet_utc'] <= row['boundary_utc']+6):
                raise ValueError('Calendar transition lacked natural before/after samples')
            for sample in row['samples']:
                if (not sample['passed'] or not sample['code_unchanged'] or sample['compared_pixels'] != 57600 or
                        sample['literal_replay_different_bytes'] or
                        (variant == 'original' and not sample['matches_literal_factory_calendar']) or
                        (variant == 'reconstructed' and (not sample['matches_iana'] or sample['corrected_different_pixels']))):
                    raise ValueError('Calendar sample failed actual time or complete-frame checks')
    completed = qemu['completed_scenes']
    if (not completed['passed'] or completed['app_sha256'] != report['app_sha256'] or
            completed['native_elf_sha256'] != text['native_elf_sha256'] or
            completed['qemu_sha256'] != qemu['qemu_sha256'] or not completed['normalized']['passed']):
        raise ValueError('Completed scene comparison used different inputs or did not pass')
    if set(completed['scenes']) != {'classic','classic-weather','dial'} or len(completed['normalized']['cases']) != 40:
        raise ValueError('Completed scene comparison omitted a required theme/control case')
    for item in completed['test_inputs']:
        if hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Completed scene test changed since execution')
    for theme, flows in completed['scenes'].items():
        if set(flows) != {'original','reconstructed'}:
            raise ValueError('Completed scene comparison omitted an application')
        for flow in flows.values():
            if (not flow['passed'] or len(flow['samples']) != 4 or
                    not flow['samples'][-1]['mature'] or flow['samples'][-1]['virtual_seconds'] < 40 or
                    any(not row['passed'] or row['different_pixels'] or not row['code_unchanged'] or
                        not row['digital_requested_brightness_applied'] for row in flow['samples'])):
                raise ValueError('Completed scene comparison omitted full frames or brightness checks')
    qemu_sources = [qemu['boot_reset']['reconstructed']['prepared']['sources']]
    qemu_sources.extend(qemu[name]['sources'] for name in ('startup_wait', 'weather_wait', 'photo_http'))
    qemu_sources.extend(row['reconstructed']['source'] for row in qemu['scenes'].values())
    qemu_sources.append(qemu['http_initial_setup']['flows']['reconstructed']['sources'])
    qemu_sources.append(qemu['weather_http']['flows']['reconstructed']['sources'])
    qemu_sources.append(body_http['sources'])
    qemu_sources.append(concurrency_http['sources'])
    qemu_sources.append(fields['flows']['reconstructed']['sources'])
    qemu_sources.append(time_http['flows']['reconstructed']['sources'])
    qemu_sources.append(native_text['sources'])
    qemu_sources.append(regional['flows']['reconstructed']['sources'])
    qemu_sources.append(calendar_http['flows']['reconstructed']['sources'])
    qemu_sources.extend(flows['reconstructed']['sources'] for flows in completed['scenes'].values())
    qemu_sources.extend(flow['sources'] for flow in frames['flows']['reconstructed'].values())
    qemu_sources.append(idle_brightness['flows']['reconstructed']['sources'])
    qemu_sources.append(controls_http['flows']['reconstructed']['sources'])
    qemu_sources.append(reinit_http['flows']['reconstructed']['sources'])
    qemu_sources.extend(flow['sources'] for flow in photo_settings['flows']['reconstructed'].values())
    qemu_sources.append(advanced['sources'])
    for sources in qemu_sources:
        app_image = next(row for row in sources['images'] if row['file'] == 'app.bin')
        if app_image['sha256'] != report['app_sha256'] or sources['source_sha256'] != report['source_sha256']:
            raise ValueError('QEMU tested a different archived application')
    summary = {key: report[key] for key in ('schema_version', 'started_utc', 'finished_utc', 'passed',
                                           'automatic_profile', 'all_functionality_verified',
                                           'source_sha256', 'app_sha256', 'test_inputs', 'notes')}
    summary['native'] = groups['native']['result']
    summary['report_aggregation'] = groups['report_aggregation']['result']
    summary['platform'] = groups['platform']['result']
    summary['frontend'] = groups['frontend']['result']
    summary['integrity'] = groups['integrity']['result']
    summary['timezone_sources'] = groups['timezone_sources']['result']
    summary['qemu_profile'] = profile
    summary['machine'] = {'passed': machine['passed'], 'literal_factory_pixels_equal': machine['equal'],
                          'renderer_cases': len(machine['cases']),
                          'geometry_checks': len(machine['stroke_geometry_checks']),
                          'source_sha256': machine['source_sha256'],
                          'native_elf_sha256': machine['native_elf_sha256'],
                          'approved_fixes': machine['approved_fixes'],
                          'scope': machine['scope']}
    summary['machine_control'] = {key: controls[key] for key in ('passed', 'timer_traces', 'slideshow', 'scope')}
    summary['machine_control']['simple_event_frames'] = controls['simple_events']['frames']
    if not controls['backlight']['passed']:
        raise ValueError('Executed backlight trace comparison failed')
    summary['machine_control']['backlight'] = controls['backlight']
    summary['machine_classic'] = {'passed':classic['passed'],'literal_factory_pixels_equal':classic['literal_equal'],
                                  'renderer_cases':len(classic['renderer_cases']),
                                  'animation_transitions':len(classic['animation']['cases']),
                                  'animation_guards':len(classic['animation']['guards']),
                                  'glyph_geometry_checks':classic['glyph_geometry_checks'],
                                  'approved_fixes':classic['approved_fixes'],'scope':classic['scope']}
    summary['machine_weather'] = {key:weather[key] for key in
        ('passed','app_sha256','source_sha256','factory_elf_sha256','native_elf_sha256','approved_fixes','requested_changes','scope')}
    summary['machine_weather']['case_counts'] = {
        kind:sum(row['kind']==kind for row in weather['cases']) for kind in sorted({row['kind'] for row in weather['cases']})}
    summary['machine_calendar'] = {key:calendar[key] for key in
        ('passed','app_sha256','source_sha256','factory_elf_sha256','native_elf_sha256','approved_fixes','scope')}
    summary['machine_calendar']['renderer_cases'] = len(calendar['cases'])
    summary['machine_jpeg'] = {key:jpeg[key] for key in
        ('passed','app_sha256','source_sha256','factory_elf_sha256','native_elf_sha256',
         'complete_asset_set','approved_fixes','scope')}
    summary['machine_jpeg']['decoded_images'] = len(jpeg['cases'])
    summary['machine_jpeg']['compared_pixels'] = sum(row['compared_pixels'] for row in jpeg['cases'])
    summary['machine_jpeg']['error_validation_checks'] = len(jpeg['errors'])
    summary['machine_jpeg']['placement_checks'] = len(jpeg['placements'])
    summary['machine_jpeg_inputs'] = jpeg_inputs
    summary['machine_timezones'] = {key:timezones[key] for key in
        ('passed','app_sha256','source_sha256','factory_elf_sha256','native_elf_sha256',
         'complete_country_set','iana_version','timezone_manifest_sha256','comparisons',
         'factory_literal_differences','approved_fixes','scope')}
    summary['machine_timezones']['countries'] = len(timezones['countries'])
    summary['machine_timezones']['invalid_inputs'] = len(timezones['invalid_inputs'])
    summary['machine_time_state'] = time_state
    summary['machine_network'] = network
    summary['machine_text'] = {key: text[key] for key in
        ('passed', 'app_sha256', 'source_sha256', 'factory_elf_sha256', 'native_elf_sha256',
         'font_source_sha256', 'unicode_glyphs', 'ascii_glyphs_per_height', 'approved_fixes', 'scope')}
    summary['machine_text']['case_counts'] = {key: len(text[key]) for key in
        ('glyph_checks', 'render_cases', 'decode_checks', 'prefix_checks', 'literal_factory')}
    summary['qemu'] = {'passed': qemu['passed'], 'qemu_sha256': qemu['qemu_sha256'],
                       'profile_sha256': qemu['profile_sha256'], 'scope': qemu['scope'],
                       'helper_sha256': qemu['helper_sha256'],
                       'boot_observer_test_sha256': qemu['boot_observer_test_sha256'],
                       'boot_observer_unit': qemu['boot_observer_unit'],
                       'boot_observer_contract_checks': qemu['boot_observer_contract_checks'],
                       'inputs_unchanged': qemu['inputs_unchanged'],
                       'startup_wait': startup,
                       'weather_wait': held_weather,
                       'photo_http': photo,
                       'photo_frames': frames,
                       'photo_brightness': idle_brightness,
                       'photo_controls': controls_http,
                       'photo_reinit': reinit_http,
                       'photo_settings': photo_settings, 'body_http': body_http, 'concurrency_http': concurrency_http,
                       'uri_targets_http': uri_targets,
                       'advanced_http': advanced,
                       'http_initial_setup': qemu['http_initial_setup'],
                       'weather_http': qemu['weather_http'],
                       'time_http': time_http,
                       'text_http': text_http,
                       'regional_http': regional,
                       'calendar_http': {**{key:calendar_http[key] for key in
                           ('passed','tested_at_utc','app_sha256','source_sha256','native_elf_sha256','qemu_sha256','profile_sha256','helper_sha256','test_inputs','requirements','scope')},
                           'flows': {variant:{'passed':flow['passed'],'sources':flow['sources'],'checks':flow['checks'],
                               'transitions':len(flow['cases']),
                               'completed_frames':sum(len(row['samples']) for row in flow['cases']),
                               'literal_iana_differences':sum(not sample['matches_iana'] for row in flow['cases'] for sample in row['samples'])}
                               for variant,flow in calendar_http['flows'].items()}},
                       'completed_scenes': completed,
                       'boot_reset': {name: {**{key: row[key] for key in ('passed', 'checks', 'duration_seconds', 'network',
                                                                      'firmware', 'qemu_sha256', 'runtime_observation',
                                                                      'clock_layout', 'ntp_observation', 'reset_ntp_observation', 'qemu_diagnostics_enabled')},
                                                   'prepared': {'sources': row['prepared']['sources']}}
                                      for name, row in qemu['boot_reset'].items()},
                       'scenes': {name: {'passed': True,
                                        'variants': {variant: {key: row[variant][key] for key in ('no_panic', 'ntp_reply', 'virtual_seconds')}
                                                     for variant in ('original', 'reconstructed')},
                                        'equal_pixels_min': row['equal_pixels_min'],
                                        'equal_pixels_max': row['equal_pixels_max']}
                                  for name, row in qemu['scenes'].items()}}
    summary['qemu']['field_http'] = {key:fields[key] for key in ('passed','tested_at_utc','qemu_sha256','cache_layout','scroll_layout','scope')}
    summary['qemu']['field_http']['flows'] = {}
    for variant,row in fields['flows'].items():
        reduced={key:row[key] for key in ('passed','sources','checks','stages')}
        if variant=='reconstructed':
            reduced['scroll']={key:row['scroll'][key] for key in ('passed','evidence')}
            reduced['scroll']['observed_frames']=len(row['scroll']['frames'])
            reduced['refresh']=row['refresh']
            reduced['theme_reset']=row['theme_reset']
        else:
            reduced['literal_long']=row['literal_long']
            reduced['not_applicable_factory']=row['not_applicable_factory']
        summary['qemu']['field_http']['flows'][variant]=reduced
    summary['not_run'] = [row for row in report['groups'] if row['status'] == 'not_run']
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Published verified functional evidence:', args.output)


if __name__ == '__main__':
    main()
