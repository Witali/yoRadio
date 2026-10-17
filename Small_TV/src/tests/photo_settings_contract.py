"""Require real in-flight photo-setting commands, full frames and natural timer continuity."""
from copy import deepcopy

CASES = {'disable-before-image': (3, 3, 0, 2, None),
         'disable-after-image': (3, 3, 2, 1, None),
         'disable-all': (1, 3, 2, 0, None),
         'enable-next': (1, 3, 2, 3, None),
         'shorten-interval': (3, 60, 2, 3, 3),
         'lengthen-interval': (3, 5, 2, 3, 9)}


def validate_photo_settings(data):
    """Reject missing phase/HTTP/timer evidence even when the top-level report claims success."""
    def require(value, message):
        if not value:
            raise ValueError('Photo in-flight settings: '+message)

    require(data['passed'] and data['inputs_unchanged'], 'failed or changing inputs')
    require(set(data['flows']) == {'original', 'reconstructed'}, 'missing firmware')
    common = {'direct_flash_backing', 'command_during_requested_fade', 'no_fade_reset', 'http_accepted',
              'saved_value', 'two_complete_frames', 'hardware_breakpoints_only', 'no_guest_state_writes',
              'next_event_keeps_counter_phase', 'executable_media_unchanged', 'no_panic'}
    for flows in data['flows'].values():
        require(set(flows) == set(CASES), 'missing live settings scenario')
        for name, flow in flows.items():
            mask, interval, phase, new_mask, new_interval = CASES[name]
            case = flow['case']
            require((case['mask'], case['interval'], case['phase'], case['expected_mask'], case.get('new_interval')) ==
                    (mask, interval, phase, new_mask, new_interval), 'wrong scenario')
            required = common | ({'timer_not_reset'} if new_interval else set())
            require(flow['passed'] and set(flow['checks']) == required and all(flow['checks'].values()), 'missing integrity/behavior checks')
            command = flow['command']
            require(command['http_status'] == command['get_status'] == 200, 'HTTP request failed')
            before, after = command['state_at_command'], command['state_after_command']
            allowed = (1, 2) if not phase else (3, 4, 5)
            require(before == after and before[0] in allowed, 'not applied in the requested active fade')
            if new_interval:
                require(command['path'] == '/set_display_time' and command['payload'] == {'display_time': new_interval} and
                        command['saved_value'] == {'displaytime': new_interval}, 'wrong interval request/response')
                require(command['timer_before'] == command['timer_after'], 'setting reset the ISR counters')
            else:
                require(command['path'] == '/set_checkbox_state', 'wrong mask endpoint')
                saved_mask = sum(1 << slot for slot in range(5) if command['saved_value']['file'+str(slot+1)+'_switch'])
                require(saved_mask == new_mask, 'wrong saved mask')
            require(len(flow['frames']) == 2, 'missing complete current/next photo')
            require(command['published_at'] <= command['capture_started_at'] <= flow['frames'][0]['guest_seconds'] <
                    flow['frames'][1]['guest_seconds'] <= command['capture_finished_at'] <= command['http_observed_at'],
                    'frame capture was delayed until after an asynchronous response wait')
            slot = 1 if not phase else 0
            next_slot = (slot+1) % 5
            for index, row in enumerate(flow['frames']):
                if index and new_mask:
                    for _ in range(5):
                        if new_mask & (1 << next_slot):
                            break
                        next_slot = (next_slot+1) % 5
                    next_slot = (next_slot+1) % 5
                require(row['passed'] and row['state_after'] == row['expected_state'] == [0, next_slot] and
                        row['compared_pixels'] == 57600 and row['different_pixels'] == 0 and
                        row['qemu_rgb_sha256'] == row['replayed_rgb_sha256'], 'selected image or full pixels differ')
                require(row['backlight']['high_duty'] == 0 and row['backlight']['brightness'] == 1000 and
                        row['backlight']['resolution_bits'] == 13, 'wrong final PWM')
            first = flow['frames'][0]
            period = new_interval or interval
            require(first['active_interval'] == period and 0 <= first['timer']['photo'] <= 255 and
                    0 <= first['timer']['subsecond'] <= 10, 'wrong actual timer interval/counters')
            ticks = max(1, period-first['timer']['photo'])*11-first['timer']['subsecond']
            window = [first['guest_seconds']+(ticks-1)*.1, first['guest_seconds']+ticks*.1+.3]
            require(flow['next_event_window'] == window and window[0] <= flow['next_fade_started_at'] <= window[1],
                    'next fade ignored the interval or lost existing timer phase')


def contract_rejection_checks(data):
    """Demonstrate rejection of incomplete, hidden-overlay, mistimed and pixel-incomplete results."""
    validate_photo_settings(data)
    flow = lambda item: item['flows']['reconstructed']['lengthen-interval']
    mutations = [
        ('missing-variant', lambda item: item['flows'].pop('original')),
        ('missing-scenario', lambda item: item['flows']['original'].pop('disable-all')),
        ('not-active', lambda item: flow(item)['command'].update(state_at_command=[0, 1])),
        ('reset-fade', lambda item: flow(item)['command'].update(state_after_command=[0, 0])),
        ('reset-timer', lambda item: flow(item)['command']['timer_after'].update(photo=255)),
        ('old-interval', lambda item: flow(item)['frames'][0].update(active_interval=5)),
        ('timer-phase-lost', lambda item: flow(item).update(next_fade_started_at=10000)),
        ('missing-frame', lambda item: flow(item)['frames'].pop()),
        ('wrong-pixels', lambda item: flow(item)['frames'][1].update(different_pixels=1)),
        ('wrong-slot', lambda item: flow(item)['frames'][1].update(state_after=[0, 4])),
        ('missing-backing', lambda item: flow(item)['checks'].pop('direct_flash_backing')),
        ('snapshot-backing', lambda item: flow(item)['checks'].update(direct_flash_backing=False)),
        ('missing-panic-check', lambda item: flow(item)['checks'].pop('no_panic')),
        ('http-observed-before-frames', lambda item: flow(item)['command'].update(http_observed_at=0)),
    ]
    checks = []
    for name, mutate in mutations:
        changed = deepcopy(data); mutate(changed)
        try:
            validate_photo_settings(changed)
        except ValueError:
            checks.append({'case': name, 'passed': True})
        else:
            raise ValueError('Photo settings contract accepted '+name)
    return checks
