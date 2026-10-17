"""Require all real body-deadline cases and exact application/test identities."""
from copy import deepcopy
import math

GUARDS = ('failed', 'changing-inputs', 'panic', 'wrong-firmware', 'missing-case',
          'duplicate-case', 'accepted-partial', 'failed-second-client', 'late-second-client',
          'nonfinite-time', 'negative-time', 'relaxed-bound', 'wrong-app', 'wrong-qemu',
          'wrong-test')


def validate_http_body(data, expected):
    """Reject incomplete cases or timing/identity substitutions despite a green flag."""
    def require(value, reason):
        if not value:
            raise ValueError('HTTP body deadline: ' + reason)

    def elapsed(value):
        return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 6

    require(data['passed'] is True and data['inputs_unchanged'] is True and data['no_panic'] is True,
            'failed, changing or crashed run')
    require(data['firmware'] == 'reconstructed' and data['all_functionality_verified'] is False,
            'wrong scope or firmware')
    require(data['second_client_bound_guest_seconds'] == 6, 'relaxed response bound')
    require(data['qemu_sha256'] == expected['qemu_sha256'], 'different emulator')
    require(data['sources']['source_sha256'] == expected['source_sha256'], 'different source archive')
    apps = [row for row in data['sources']['images'] if row['file'] == 'app.bin']
    require(len(apps) == 1 and apps[0]['sha256'] == expected['app_sha256'], 'different application')
    tests = [sha for name, sha in data['inputs_sha256'].items()
             if name.replace('\\', '/').endswith('/Small_TV/src/tests/http_body_qemu.py')]
    require(tests == [expected['test_sha256']], 'different traffic generator')
    rows = data['cases']
    require(len(rows) == 4 and {row['name'] for row in rows} ==
            {'fragmented', 'stalled', 'trickle', 'oversized'}, 'missing/duplicate live case')
    for row in rows:
        require(row['passed'] is True, 'failed case')
        response = row['body_response']
        require(type(response['bytes']) is int and 0 <= response['bytes'] <= 4096,
                'unbounded or missing body response')
        if row['name'] == 'fragmented':
            require(response['status'] == 200 and elapsed(row['guest_seconds']), 'valid fragments failed')
        else:
            require(response['status'] == 400 and row['second_client_status'] == 200 and
                    elapsed(row['second_client_guest_seconds']), 'bad body blocked another client')


def contract_rejection_checks(data, expected):
    """Show that missing traffic, invalid timing and mismatched bytes cannot publish."""
    validate_http_body(data, expected)
    bad_case = lambda item: next(row for row in item['cases'] if row['name'] == 'stalled')
    wrong_app = lambda item: next(row for row in item['sources']['images'] if row['file'] == 'app.bin').update(sha256='0' * 64)
    wrong_test = lambda item: item['inputs_sha256'].update({
        next(name for name in item['inputs_sha256'] if name.replace('\\', '/').endswith('/Small_TV/src/tests/http_body_qemu.py')): '0' * 64})
    changes = (
        lambda item: item.update(passed=False),
        lambda item: item.update(inputs_unchanged=False),
        lambda item: item.update(no_panic=False),
        lambda item: item.update(firmware='original'),
        lambda item: item['cases'].pop(),
        lambda item: item['cases'].append(deepcopy(item['cases'][0])),
        lambda item: bad_case(item)['body_response'].update(status=200),
        lambda item: bad_case(item).update(second_client_status=500),
        lambda item: bad_case(item).update(second_client_guest_seconds=6.01),
        lambda item: bad_case(item).update(second_client_guest_seconds=float('nan')),
        lambda item: bad_case(item).update(second_client_guest_seconds=-1),
        lambda item: item.update(second_client_bound_guest_seconds=60),
        wrong_app,
        lambda item: item.update(qemu_sha256='0' * 64),
        wrong_test)
    results = []
    for name, change in zip(GUARDS, changes):
        altered = deepcopy(data)
        change(altered)
        try:
            validate_http_body(altered, expected)
        except (ValueError, KeyError, TypeError):
            results.append({'name': name, 'passed': True})
        else:
            raise ValueError('HTTP body report accepted mutation: ' + name)
    return results


def validate_http_body_guards(data):
    """Require the complete set of consumer rejection checks in the full report."""
    rows = data['contract_checks']
    if len(rows) != len(GUARDS) or {row['name'] for row in rows} != set(GUARDS) or any(
            row['passed'] is not True for row in rows):
        raise ValueError('HTTP body deadline: missing consumer rejection checks')
