"""Require complete native concurrent-client evidence and exact compiled inputs."""
from copy import deepcopy
import math

CHECKS = {'clock_cache_advances_during_weather', 'exactly_one_upload_session', 'active_photo_unpublished',
    'concurrent_exact_retries_accepted', 'concurrent_conflicting_retry_rejected',
    'scan_and_settings_during_upload', 'concurrent_settings_both_accepted', 'independent_fields_preserved',
    'weather_still_in_flight_during_upload', 'completed_photo_exact', 'clock_resumes_after_upload',
    'pre_restart_settings_accepted', 'both_restart_requests_acknowledged', 'one_observed_restart_for_pair',
    'settings_survive_warm_restart', 'partial_photo_hidden_after_restart', 'complete_photo_survives_restart',
    'first_vm_no_panic', 'cold_boot_uses_new_vm', 'settings_survive_cold_boot',
    'partial_photo_hidden_after_cold_boot', 'complete_photo_survives_cold_boot',
    'new_upload_after_interrupted_restart', 'cold_boot_no_panic', 'protected_regions_unchanged'} | {
        'chunk_and_get_' + str(index) for index in range(1, 10)}
BATCHES = {
    'competing-upload-starts': ('/start_upload', '/start_upload'),
    'identical-chunk-retries': ('/upload_chunk', '/upload_chunk'),
    'exact-and-conflicting-retries': ('/upload_chunk', '/upload_chunk'),
    'scan-and-settings-during-upload': ('/scan', '/getsettings'),
    'independent-setting-writes': ('/SetTimeModeValue', '/setgifvalue'),
    'settings-before-restart': ('/SetTimeModeValue', '/setgifvalue'),
    'duplicate-restart-requests': ('/restart', '/restart'),
    **{'chunk-and-get-' + str(index): ('/upload_chunk', '/getgifvalue') for index in range(1, 10)}}
PROTECTED = {'boot_and_partitions', 'application_and_gap', 'photos_1_to_3',
             'animations_and_weather', 'unused_tail'}
GUARDS = ('failed', 'changing-inputs', 'missing-check', 'failed-check', 'missing-batch',
          'duplicate-batch', 'two-uploads', 'accepted-conflicting-retry', 'late-batch', 'nonfinite-time',
          'failed-request', 'stale-renderer', 'weather-not-running', 'changed-protected-flash',
          'wrong-app', 'wrong-elf', 'wrong-qemu', 'wrong-test', 'wrong-formatter', 'wrong-slot')


def validate_concurrency(data, expected):
    """Reject green reports that omit an interleaving, state check or byte identity."""
    def require(value, reason):
        if not value:
            raise ValueError('Concurrent clients: ' + reason)

    def elapsed(value):
        return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 6

    require(data['passed'] is True and data['inputs_unchanged'] is True and
            data['all_functionality_verified'] is False, 'failed or wrong scope')
    require(set(data['checks']) == CHECKS and all(value is True for value in data['checks'].values()),
            'missing/failed acceptance condition')
    for key in ('app_sha256', 'source_sha256', 'native_elf_sha256', 'qemu_sha256'):
        require(data[key] == expected[key], 'different ' + key)
    for name, key in (('concurrency_qemu.py', 'test_sha256'), ('photo_protocol.py', 'formatter_sha256')):
        matches = [sha for path, sha in data['inputs_sha256'].items()
                   if path.replace('\\', '/').endswith('/Small_TV/src/tests/' + name)]
        require(matches == [expected[key]], 'different traffic/protocol code')
    rows = data['paired_batches']
    require(len(rows) == len(BATCHES) and {row['label'] for row in rows} == set(BATCHES),
            'missing/duplicate paired traffic')
    for row in rows:
        require(tuple(row['paths']) == BATCHES[row['label']] and elapsed(row['guest_seconds']),
                'wrong paths or unbounded pair')
        if row['label'] == 'competing-upload-starts':
            require(sorted(row['statuses']) == [200, 400], 'second upload session accepted')
            require(data['winner_slot'] == 4 + row['statuses'].index(200), 'wrong winner')
        else:
            require(row['statuses'] == ([200, 400] if row['label'] == 'exact-and-conflicting-retries'
                                         else [200, 200]), 'wrong paired response')
    require(data['winner_slot'] in (4, 5) and data['loser_slot'] == 9 - data['winner_slot'], 'wrong slots')
    requests = data['requests']
    require(len(requests) == 68 and all(row['status'] == 200 and elapsed(row['guest_seconds']) for row in requests),
            'missing/failed sequential traffic')
    require(data['held_weather_worker_state'] & 1, 'weather was not running')
    resume = data['renderer_resume']
    require(resume['before_finish']['synced'] is True and resume['after_finish']['synced'] is True and
            resume['before_finish'] != resume['after_finish'], 'renderer did not resume')
    require(set(data['protected_before']) == set(data['protected_after']) == PROTECTED and
            data['protected_before'] == data['protected_after'], 'protected flash changed/omitted')


def contract_rejection_checks(data, expected):
    """Demonstrate refusal of missing traffic, false state and mismatched artifacts."""
    validate_concurrency(data, expected)
    batch = lambda item, label: next(row for row in item['paired_batches'] if row['label'] == label)
    change_input = lambda item, filename: item['inputs_sha256'].update({
        next(path for path in item['inputs_sha256'] if path.replace('\\', '/').endswith('/Small_TV/src/tests/' + filename)): '0' * 64})
    changes = (
        lambda item: item.update(passed=False),
        lambda item: item.update(inputs_unchanged=False),
        lambda item: item['checks'].pop('partial_photo_hidden_after_cold_boot'),
        lambda item: item['checks'].update(cold_boot_no_panic=False),
        lambda item: item['paired_batches'].pop(),
        lambda item: item['paired_batches'].append(deepcopy(item['paired_batches'][0])),
        lambda item: batch(item, 'competing-upload-starts').update(statuses=[200, 200]),
        lambda item: batch(item, 'exact-and-conflicting-retries').update(statuses=[200, 200]),
        lambda item: item['paired_batches'][0].update(guest_seconds=6.01),
        lambda item: item['paired_batches'][0].update(guest_seconds=float('nan')),
        lambda item: item['requests'][0].update(status=500),
        lambda item: item['renderer_resume'].update(after_finish=deepcopy(item['renderer_resume']['before_finish'])),
        lambda item: item.update(held_weather_worker_state=0),
        lambda item: item['protected_after'].update(photos_1_to_3='0' * 64),
        lambda item: item.update(app_sha256='0' * 64),
        lambda item: item.update(native_elf_sha256='0' * 64),
        lambda item: item.update(qemu_sha256='0' * 64),
        lambda item: change_input(item, 'concurrency_qemu.py'),
        lambda item: change_input(item, 'photo_protocol.py'),
        lambda item: item.update(loser_slot=3))
    checks = []
    for name, change in zip(GUARDS, changes):
        altered = deepcopy(data)
        change(altered)
        try:
            validate_concurrency(altered, expected)
        except (ValueError, KeyError, TypeError):
            checks.append({'name': name, 'passed': True})
        else:
            raise ValueError('Concurrent clients report accepted mutation: ' + name)
    return checks


def validate_concurrency_guards(data):
    """Require all rejection controls before publishing a full-suite report."""
    rows = data['contract_checks']
    if len(rows) != len(GUARDS) or {row['name'] for row in rows} != set(GUARDS) or any(
            row['passed'] is not True for row in rows):
        raise ValueError('Concurrent clients: missing consumer rejection checks')
