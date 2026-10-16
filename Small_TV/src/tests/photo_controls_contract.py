"""Validate real HTTP display-control effects and complete photo output."""


def validate_photo_brightness(data):
    """Require both firmwares, unchanged media, a bounded update and all complete photo pixels."""
    def require(value, message):
        if not value:
            raise ValueError('Photo idle brightness: '+message)

    require(data['passed'] and data['inputs_unchanged'], 'failed or changing inputs')
    require(set(data['flows']) == {'original', 'reconstructed'}, 'missing firmware variant')
    checks = {'first_photo_complete', 'settings_changed', 'idle_brightness_bounded',
              'complete_photo_frame', 'no_new_fade', 'hardware_breakpoints_only',
              'no_guest_state_writes', 'executable_media_unchanged', 'no_panic'}
    for flow in data['flows'].values():
        require(flow['passed'] and set(flow['checks']) == checks and all(flow['checks'].values()),
                'missing HTTP/frame/state/integrity check')
        require(flow['photo_interval'] == 60 and flow['idle_state_before'] == [0, 1],
                'did not change settings during a long idle interval')
        require(flow['http_status'] == 200 and 0 <= flow['http_guest_seconds'] <= 3 and
                0 <= flow['after_request_guest_seconds'] <= 1, 'unbounded HTTP/brightness response')
        require(flow['backlight']['high_duty'] == 4095 and flow['backlight']['brightness'] == 501 and
                flow['backlight']['resolution_bits'] == 13, 'wrong 50-percent PWM output')
        require(flow['different_pixels'] == 0 and flow['qemu_rgb_sha256'] == flow['replayed_rgb_sha256'],
                'complete photo/footer frame differs')


def validate_photo_controls(data):
    """Require three same-theme commands and round-robin fades without configuration revisions."""
    def require(value, message):
        if not value:
            raise ValueError('Photo theme command: '+message)

    require(data['passed'] and data['inputs_unchanged'], 'failed or changing inputs')
    require(set(data['flows']) == {'original', 'reconstructed'}, 'missing firmware variant')
    common = {'first_photo_complete', 'three_same_theme_commands', 'hardware_breakpoints_only',
              'no_guest_state_writes', 'executable_media_unchanged', 'no_panic'}
    for variant, flow in data['flows'].items():
        required = common | ({'no_redundant_configuration_revision', 'explicit_theme_requests'}
                             if variant == 'reconstructed' else set())
        require(flow['passed'] and set(flow['checks']) == required and all(flow['checks'].values()),
                'missing command/integrity check')
        require(len(flow['reselects']) == 3, 'missing repeated selection')
        for row, slot in zip(flow['reselects'], (1, 0, 1)):
            require(row['passed'] and row['selected_slot'] == slot and row['state_after'] == [0, slot+1] and
                    row['expected_state'] == [0, slot+1] and row['post_status'] == 200 and
                    0 <= row['guest_seconds'] <= 2, 'lost, reset or delayed selection')
            require(row['compared_pixels'] == 57600 and row['different_pixels'] == 0 and
                    row['qemu_rgb_sha256'] == row['replayed_rgb_sha256'] and
                    row['backlight']['high_duty'] == 0 and row['backlight']['brightness'] == 1000,
                    'complete selected photo/footer differs')
        if variant == 'reconstructed':
            require(flow['configuration_generation_before'] == flow['configuration_generation_after'] and
                    flow['theme_requests_after']-flow['theme_requests_before'] == 3,
                    'commands were conflated with stored configuration revisions')


def validate_photo_reinit(data):
    """Require a fresh complete photo after a command interrupts the previous fade."""
    def require(value, message):
        if not value:
            raise ValueError('Photo active reinitialization: '+message)

    require(data['passed'] and data['inputs_unchanged'], 'failed or changing inputs')
    require(set(data['flows']) == {'original', 'reconstructed'}, 'missing firmware variant')
    common = {'active_fade_command', 'first_photo_complete', 'http_command_accepted',
              'hardware_breakpoints_only', 'no_guest_state_writes', 'executable_media_unchanged', 'no_panic'}
    for variant, flow in data['flows'].items():
        required = common | ({'known_factory_blank_screen'} if variant == 'original' else
                             {'complete_next_photo', 'bounded_response', 'full_backlight'})
        require(flow['passed'] and set(flow['checks']) == required and all(flow['checks'].values()),
                'missing command/frame/integrity check')
        require(flow['photo_interval'] == 60 and flow['state_before_request'] == [3, 1] and
                flow['state_when_command_executes'] in ([3, 1], [4, 1], [5, 1]) and
                flow['http_status'] == 200, 'did not interrupt a real active fade')
        require(flow['compared_pixels'] == 57600 and flow['backlight']['high_duty'] == 0 and
                flow['backlight']['brightness'] == 1000 and flow['backlight']['resolution_bits'] == 13,
                'wrong surface or final backlight')
        if variant == 'original':
            require(flow['state_after'] == [0, 1] and flow['all_pixels_black'] and
                    flow['different_pixels'] > 0 and not flow['literal_output_matches_fixed_requirement'] and
                    2 <= flow['guest_seconds'] < 3, 'factory defect was not directly observed')
        else:
            require(flow['state_after'] == [0, 2] and not flow['all_pixels_black'] and
                    flow['different_pixels'] == 0 and flow['literal_output_matches_fixed_requirement'] and
                    flow['qemu_rgb_sha256'] == flow['replayed_rgb_sha256'] and
                    0 <= flow['guest_seconds'] <= 2, 'next photo was lost, blank or delayed')
