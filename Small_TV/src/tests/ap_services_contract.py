"""Require complete AP HTTP/LCD/task/cache evidence in the suite and publisher."""
from copy import deepcopy
from pathlib import Path
import re

from netif_observer import FACTORY_SHA, require

REQUESTS = [('POST', '/updateCity'), ('POST', '/advancedset'), ('POST', '/settings'),
            ('POST', '/setclocktype'), ('GET', '/getsettings'), ('GET', '/getclocktype')]


def validate_ap_services(report, expected):
    """Reject unchanged-screen claims without both real roles and worker/cache checks."""
    try:
        require(report['passed'] is True and report['inputs_unchanged'] is True, 'AP services run did not pass')
        require(report['factory_native_frame_identical'] is True and set(report['flows']) ==
                {'original', 'reconstructed'}, 'Missing paired AP frames')
        for key in ('app_sha256', 'native_elf_sha256', 'qemu_sha256'):
            require(report[key] == expected[key], 'AP service identity differs: ' + key)
        recorded = [sha for path, sha in report['inputs_sha256'].items() if Path(path).name == 'ap_services_qemu.py']
        require(recorded == [expected['test_sha256']], 'AP observer source differs')
        frames = []
        for variant, flow in report['flows'].items():
            require(flow['passed'] is True and flow['executable_media_unchanged'] is True and
                    flow['uart']['passed'] is True and flow['uart']['rom_boots'] == 1 and not flow['uart']['errors'],
                    'AP code or UART integrity failed')
            require(flow['http'] == [{'method': method, 'path': path, 'status': 200} for method, path in REQUESTS],
                    'Incomplete AP settings requests')
            require(set(flow['snapshots']) == {'ready', 'after-settings'}, 'Missing AP snapshots')
            ready, after = (flow['snapshots'][label] for label in ('ready', 'after-settings'))
            require(ready['guest_seconds'] >= 30 and after['guest_seconds'] >= 45 and
                    after['guest_seconds'] > ready['guest_seconds'], 'AP startup or settings observation too early')
            for snapshot in (ready, after):
                require(re.fullmatch('[a-f0-9]{64}', snapshot['frame_sha256']) is not None, 'Missing RGB frame digest')
                frames.append(snapshot['frame_sha256'])
                if variant == 'reconstructed':
                    tasks = snapshot['tasks']
                    names = {task['name'] for task in tasks}
                    require(len(tasks) == len(names) == 9 and {'httpd', 'clock_display', 'captive_dns', 'wifi'} <= names
                            and not names & {'time_sync', 'weather_http', 'wifi_fallback'}, 'AP worker allocation differs')
                    require(all(task['stack_high_water_free_bytes'] > 0 for task in tasks) and
                            snapshot['heap']['free_bytes'] > 0, 'No observed AP task/heap headroom')
                    require(snapshot['weather'] == {'worker_state': 0, 'valid': False, 'generation': 0}, 'AP cache changed')
                    require(snapshot['role']['connected'] is False and snapshot['role']['ap_active'] is True and
                            snapshot['role']['time_synced'] is False, 'AP role or synchronization changed')
            if variant == 'reconstructed':
                require(flow['rom_counter_checks'] == 2 * sum(len(row['heap']['heaps']) for row in (ready, after)),
                        'Missing exact ROM heap counter crosscheck')
                app = next(row for row in flow['sources']['images'] if row['file'] == 'app.bin')
                require(app['sha256'] == expected['app_sha256'] and
                        flow['sources']['source_sha256'] == expected['source_sha256'], 'AP booted another native archive')
            else:
                require(flow['sources']['full_flash_sha256'] == FACTORY_SHA, 'AP booted another factory dump')
        require(len(set(frames)) == 1, 'Factory/native complete AP frames differ')
    except (KeyError, TypeError, StopIteration) as error:
        raise ValueError('Incomplete AP service evidence') from error


def rejection_checks(report, expected):
    """Prove that wrong binaries, extra workers and stale/partial frames cannot pass."""
    validate_ap_services(report, expected)
    native = ('flows', 'reconstructed')
    snapshot = native + ('snapshots', 'after-settings')
    mutations = [('failed', ('passed',), False), ('changed-inputs', ('inputs_unchanged',), False),
        ('wrong-app', ('app_sha256',), '0' * 64), ('wrong-elf', ('native_elf_sha256',), '0' * 64),
        ('wrong-qemu', ('qemu_sha256',), '0' * 64), ('missing-factory', ('flows', 'original'), None),
        ('missing-http', native + ('http',), []), ('changed-code', native + ('executable_media_unchanged',), False),
        ('reset', native + ('uart', 'rom_boots'), 2),
        ('different-frame', snapshot + ('frame_sha256',), '0' * 64),
        ('early-frame', snapshot + ('guest_seconds',), 31),
        ('weather-worker', snapshot + ('tasks', 0, 'name'), 'weather_http'),
        ('time-worker', snapshot + ('tasks', 0, 'name'), 'time_sync'),
        ('pending-request', snapshot + ('weather', 'worker_state'), 2),
        ('changed-cache', snapshot + ('weather', 'generation'), 1),
        ('ap-got-ip', snapshot + ('role', 'connected'), True),
        ('false-time-sync', snapshot + ('role', 'time_synced'), True),
        ('missing-rom-check', native + ('rom_counter_checks',), 0)]
    checks = []
    for name, path, value in mutations:
        changed = deepcopy(report)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate_ap_services(changed, expected)
        except ValueError:
            checks.append({'name': name, 'passed': True})
        else:
            raise AssertionError('AP service contract accepted invalid evidence: ' + name)
    return checks
