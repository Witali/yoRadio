"""Validate real HTTP brightness changes between completed photo fades."""


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
