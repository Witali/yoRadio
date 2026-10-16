"""Require complete photo/fade evidence before publishing a full validation report."""
from copy import deepcopy


def validate_photo_frames(data):
    """Reject partial runs, reordered photos, omitted fade phases or incorrect LEDC restoration."""
    def require(value, message):
        if not value:
            raise ValueError('Photo frames: '+message)

    cases = {'all-photos': (31, 5, 0, 0, 500),
             'masked-night': (10, 2, 100, 1, 500),
             'none-dark': (0, 1, 1000, 0, 500)}
    require(data['passed'] and data['inputs_unchanged'], 'failed or changing inputs')
    require(set(data['flows']) == {'original', 'reconstructed'}, 'missing firmware variant')
    levels = (300, 600, 1000, 600, 300, 0)
    for variant, flows in data['flows'].items():
        require(set(flows) == set(cases), 'missing mask/brightness profile')
        for name, flow in flows.items():
            mask, cycles, day_level, night_mode, night_level = cases[name]
            expected_case = dict(name=name, mask=mask, cycles=cycles, day=day_level,
                                 night_mode=night_mode, night=night_level)
            require(flow['case'] == expected_case and flow['passed'] and all(flow['checks'].values()),
                    'profile or integrity checks failed')
            required_checks = {'all_pixels_checked', 'expected_fade_steps', 'hardware_breakpoints_only',
                               'no_guest_state_writes', 'photo_order', 'executable_media_unchanged', 'no_panic'}
            if variant == 'reconstructed' and night_mode:
                required_checks.add('synchronized_night_restore')
            require(required_checks <= set(flow['checks']), 'missing integrity/panic/state-write check')
            phases = [2, 3, 4, 5]+list(range(6))*(cycles-1)
            require([row['fade_before'] for row in flow['samples']] == phases, 'missing/reordered fade phase')
            selected = [slot for row in flow['samples'] for slot in row['selected']]
            require(selected == [slot for slot in range(5) if mask & (1 << slot)], 'incorrect photo order')
            previous = None
            night_verified = False
            for row in flow['samples']:
                phase = row['fade_before']
                require(previous is None or [phase, row['next_slot_before']] == previous,
                        'broken state continuity')
                previous = row['state_after']
                require(previous[0] == (phase+1) % 6 and 0 <= previous[1] < 5,
                        'incorrect returned slideshow state')
                require(row['passed'] and row['code_unchanged'] and row['compared_pixels'] == 57600 and
                        row['different_pixels'] == 0 and row['qemu_rgb_sha256'] == row['replayed_rgb_sha256'],
                        'full frame differs or code changed')
                require(row['literal_factory_duty'] == levels[phase]*8191//1000,
                        'literal factory fade arithmetic changed')
                correction = variant == 'reconstructed' and phase == 5
                require(row['brightness_restore_correction'] == correction, 'incorrect correction boundary')
                duty = levels[phase]*8191//1000
                if correction:
                    clock = row['restore_calendar']
                    require(clock is not None and 0 <= clock['hour'] < 24 and 0 <= clock['minute'] < 60,
                            'missing schedule calendar')
                    minute = clock['hour']*60+clock['minute']
                    day = minute < 22*60 and (minute > 720 or minute > 9*60)
                    night = bool(night_mode and not day)
                    require(clock['night_selected'] == night, 'incorrect schedule window')
                    duty = (night_level if night else day_level)*8191//1000
                    night_verified |= bool(night and clock['clock_valid'])
                else:
                    require(row['restore_calendar'] is None, 'unexpected schedule substitution')
                require(row['expected_duty'] == row['backlight']['high_duty'] == duty and
                        row['backlight']['resolution_bits'] == 13 and
                        row['backlight']['brightness'] == 1000-min(duty, 8192)*1000//8192,
                        'incorrect PWM duty/brightness')
            if night_mode and variant == 'reconstructed':
                require(night_verified, 'no synchronized night-brightness restoration')
    normalized = data['normalized']
    require(all(normalized[key] == data[key] for key in
                ('app_sha256', 'native_elf_sha256', 'factory_elf_sha256')), 'normalized executable differs')
    require(normalized['passed'] and len(normalized['cases']) == 9, 'missing independent complete-photo scenes')
    expected = {(1 << slot, (slot+1) % 5, '10.0.2.15') for slot in range(5)} | {
        (31, 4, '192.168.43.1'), (10, 4, '255.255.255.255'),
        (0, 0, '10.0.2.15'), (0, 4, '192.168.43.1')}
    require({(row['mask'], row['next_slot'], row['address']) for row in normalized['cases']} == expected,
            'normalized scenes omitted a photo, skip or empty mask')
    require(all(row['passed'] and row['compared_pixels'] == 57600 and row['different_pixels'] == 0 and
                row['factory'] == row['native'] for row in normalized['cases']),
            'normalized decoder/footer/state outputs differ')


def contract_rejection_checks(data):
    """Prove that incomplete, reordered and differently identified evidence cannot pass."""
    validate_photo_frames(data)
    native = lambda item: item['flows']['reconstructed']['all-photos']
    mutations = [
        ('missing-variant', lambda item: item['flows'].pop('original')),
        ('missing-profile', lambda item: item['flows']['original'].pop('none-dark')),
        ('missing-phase', lambda item: native(item)['samples'].pop()),
        ('wrong-photo-order', lambda item: native(item)['samples'][0].update(selected=[4])),
        ('missing-no-panic', lambda item: native(item)['checks'].pop('no_panic')),
        ('code-changed', lambda item: native(item)['samples'][0].update(code_unchanged=False)),
        ('wrong-duty', lambda item: native(item)['samples'][0]['backlight'].update(high_duty=0)),
        ('wrong-schedule-window', lambda item: item['flows']['reconstructed']['masked-night']['samples'][-1]['restore_calendar'].update(night_selected=False)),
        ('missing-normalized-photo', lambda item: item['normalized']['cases'].pop()),
        ('mixed-executable', lambda item: item['normalized'].update(native_elf_sha256='0'*64)),
    ]
    checks = []
    for name, mutate in mutations:
        changed = deepcopy(data)
        mutate(changed)
        try:
            validate_photo_frames(changed)
        except ValueError:
            checks.append({'case': name, 'passed': True})
        else:
            raise ValueError('Photo frame contract accepted '+name)
    return checks
