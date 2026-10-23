"""Require complete current-main cache-backed LCD/fade evidence."""
from copy import deepcopy

def validate_first_photo_seconds(native,stock):
    """Keep warm-up inside the timing boundary; do not accept the known regression."""
    if not 0 < native <= stock:raise ValueError('Cache LCD: first photo slower than the measured factory profile')


def validate(data):
    """Reject missing photos/phases/pixels, mixed inputs and false cache readiness."""
    def require(value, message):
        if not value:raise ValueError('Cache LCD: '+message)

    require(data['passed'] and data['inputs_unchanged'], 'failed/changing inputs')
    require(set(data['flows']) == {'reconstructed'}, 'wrong observed application')
    require(data['network_acceptance'] is False and data['hardware_tested'] is False,
            'storage/LCD proof mislabeled as network/hardware acceptance')
    profiles = {'all-photos': (31, 5, 0, 0, 500),
                'masked-night': (10, 2, 100, 1, 500),
                'none-dark': (0, 1, 1000, 0, 500),
                'bad-first': (31, 4, 0, 0, 500)}
    flows = data['flows']['reconstructed']
    require(set(flows) == set(profiles), 'missing profile')
    levels = [300, 600, 1000, 600, 300, 0]
    for name, values in profiles.items():
        mask, cycles, day_level, night_mode, night_level = values
        flow = flows[name]
        expected = dict(name=name, mask=mask, cycles=cycles, day=day_level,night_mode=night_mode,night=night_level)
        bad_slots = 1 if name == 'bad-first' else 0
        if bad_slots:expected['bad_slots'] = bad_slots
        require(flow['case'] == expected, 'wrong fixture')
        checks = {'all_pixels_checked', 'expected_fade_steps', 'hardware_breakpoints_only',
                  'no_guest_state_writes', 'photo_order', 'direct_flash_backing',
                  'executable_media_unchanged', 'no_panic'}
        if night_mode:checks.add('synchronized_night_restore')
        require(flow['passed'] and flow['owners_stopped'] and checks <= set(flow['checks']) and
                all(flow['checks'].values()), 'integrity/lifecycle check missing or failed')
        observed = flow['cycles_observed']
        require(isinstance(observed, int) and (cycles < observed <= 6 if night_mode else observed == cycles),
                'missing or unbounded cycles')
        phases = [2, 3, 4, 5]+list(range(6))*(observed-1)
        require([x['fade_before'] for x in flow['samples']] == phases, 'missing/reordered phase')
        enabled = [slot for slot in range(5) if mask & ~bad_slots & (1 << slot)]
        order = [enabled[i % len(enabled)] for i in range(observed)] if enabled else []
        require([slot for row in flow['samples'] for slot in row['selected']] == order, 'wrong/skipped photo')
        previous = None
        for row in flow['samples']:
            phase = row['fade_before']
            require(previous is None or previous == [phase, row['next_slot_before']], 'broken state continuity')
            previous = row['state_after']
            require(previous[0] == (phase+1) % 6 and 0 <= previous[1] < 5, 'wrong returned state')
            require(row['passed'] and row['code_unchanged'] and row['compared_pixels'] == 57600 and
                    row['different_pixels'] == 0 and row['qemu_rgb_sha256'] == row['replayed_rgb_sha256'],
                    'pixels changed, masked or omitted')
            require(row['intentional_bad_slots'] == bad_slots, 'undeclared invalid source correction')
            if phase == 2 and enabled:
                order = [(row['next_slot_before']+step)%5 for step in range(5)]
                wanted = next(slot for slot in order if mask & ~bad_slots & (1<<slot))
                require(row['present_mask'] & (1<<wanted), 'valid next photo skipped while preparing cache')
            require(0 <= row['guest_seconds'] <= 300, 'observation budget exceeded')
            correction = phase == 5
            require(row['brightness_restore_correction'] == correction and
                    row['literal_factory_duty'] == levels[phase]*8191//1000, 'incorrect correction boundary')
            duty = levels[phase]*8191//1000
            if correction:
                clock = row['restore_calendar']
                require(clock is not None and 0 <= clock['hour'] < 24 and 0 <= clock['minute'] < 60,
                        'missing actual restoration calendar')
                minute = clock['hour']*60+clock['minute']
                night = bool(night_mode and not (minute < 22*60 and (minute > 720 or minute > 9*60)))
                require(clock['night_selected'] == night, 'wrong night window')
                duty = (night_level if night else day_level)*8191//1000
            else:require(row['restore_calendar'] is None, 'substituted restoration')
            require(row['expected_duty'] == row['backlight']['high_duty'] == duty and
                    row['backlight']['resolution_bits'] == 13 and
                    row['backlight']['brightness'] == 1000-min(duty, 8192)*1000//8192,
                    'wrong physical duty/resolution/brightness')
        if night_mode:
            control = flow['night_ntp_control']
            require(control['initial_drop_mask'] == 7 and control['released_after_cycles'] == cycles,
                    'missing external delayed-SNTP fixture')
            early = [x['restore_calendar'] for x in flow['samples'][:4+6*(cycles-1)] if x['restore_calendar']]
            require(len(early) == cycles and all(not x['clock_valid'] for x in early), 'early sync was substituted')
            require(any(x['restore_calendar'] and x['restore_calendar']['clock_valid'] and
                        x['restore_calendar']['night_selected'] for x in flow['samples']), 'no actual night sync')
    first = flows['all-photos']['samples'][0]
    validate_first_photo_seconds(first['guest_seconds'], data['factory_first_photo_seconds'])
    require(first['present_mask'] == 1, 'first photo still waits for unrelated caches')
    cold = data['cold']
    require(cold['passed'] and cold['owners_stopped'] and all(cold['checks'].values()) and
            cold['checks']['cold_cache_no_program_or_erase_attempts'] and
            cold['checks']['cold_cache_candidates_exact'], 'cold hit writes or changes cache')
    require(cold['case'] == flows['all-photos']['case'] and len(cold['samples']) == 28,
            'incomplete cold slideshow')
    require([s for row in cold['samples'] for s in row['selected']] == [0,1,2,3,4], 'cold photo order')
    require(all(r['passed'] and r['compared_pixels'] == 57600 and r['different_pixels'] == 0 and
                r['qemu_rgb_sha256'] == r['replayed_rgb_sha256'] for r in cold['samples']), 'cold full frame differs')
    require(set(cold['cold_write_traps']) == {'flash_program','flash_erase'} and
            all(cold['cold_write_traps'].values()), 'missing real JPEG program/erase traps')
    require([r['fade_before'] for r in cold['samples']] == [2,3,4,5]+list(range(6))*4, 'cold fade phases')
    previous = None
    for row in cold['samples']:
        phase = row['fade_before'];duty = levels[phase]*8191//1000
        require(previous is None or previous == [phase,row['next_slot_before']], 'cold state discontinuity')
        previous = row['state_after']
        require(previous[0] == (phase+1)%6 and 0 <= previous[1] < 5, 'cold returned state')
        require(row['code_unchanged'] and row['intentional_bad_slots'] == 0 and
                row['brightness_restore_correction'] == (phase == 5), 'cold code/correction changed')
        require(row['literal_factory_duty'] == duty and row['expected_duty'] == row['backlight']['high_duty'] == duty and
                row['backlight']['resolution_bits'] == 13 and
                row['backlight']['brightness'] == 1000-min(duty,8192)*1000//8192, 'cold duty/brightness')
        if phase == 2:require(row['present_mask'] & (1<<row['selected'][0]), 'cold cache not ready')
    validate_first_photo_seconds(cold['samples'][0]['guest_seconds'], data['factory_first_photo_seconds'])


def rejection_checks(data):
    """Ensure a green flag alone cannot waive missing full-frame/cache evidence."""
    validate(data)
    flow = lambda item:item['flows']['reconstructed']['all-photos']
    mutations = [
        ('missing-profile', lambda x:x['flows']['reconstructed'].pop('none-dark')),
        ('missing-phase', lambda x:flow(x)['samples'].pop()),
        ('wrong-photo', lambda x:flow(x)['samples'][0].update(selected=[4])),
        ('missing-source-check', lambda x:x.update(inputs_unchanged=False)),
        ('missing-process-reap', lambda x:flow(x).update(owners_stopped=False)),
        ('snapshot', lambda x:flow(x)['checks'].update(direct_flash_backing=False)),
        ('protected-write', lambda x:flow(x)['checks'].update(executable_media_unchanged=False)),
        ('pixels-omitted', lambda x:flow(x)['samples'][0].update(compared_pixels=57599)),
        ('wrong-pixel', lambda x:flow(x)['samples'][0].update(different_pixels=1)),
        ('wrong-duty', lambda x:flow(x)['samples'][0]['backlight'].update(high_duty=0)),
        ('cache-unready', lambda x:flow(x)['samples'][0].update(present_mask=0)),
        ('false-network-claim', lambda x:x.update(network_acceptance=True)),
        ('slower-startup', lambda x:flow(x)['samples'][0].update(guest_seconds=x['factory_first_photo_seconds']+1)),
        ('unrelated-warmup', lambda x:flow(x)['samples'][0].update(present_mask=31)),
        ('cold-write', lambda x:x['cold']['checks'].update(cold_cache_no_program_or_erase_attempts=False)),
        ('missing-cold', lambda x:x['cold']['samples'].pop()),
        ('missing-night-sync', lambda x:[r['restore_calendar'].update(clock_valid=False)
            for r in x['flows']['reconstructed']['masked-night']['samples'] if r['restore_calendar']]),
    ]
    rejected = []
    for name, mutate in mutations:
        changed = deepcopy(data);mutate(changed)
        try:validate(changed)
        except ValueError:rejected.append(name)
        else:raise ValueError('Cache LCD contract accepted '+name)
    return rejected
