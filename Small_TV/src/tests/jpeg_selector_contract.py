"""Require complete selector evidence independently from its reported pass flags."""
from copy import deepcopy
import hashlib

from jpeg_selector_fixtures import cases, upload_cases

IDENTITY = ('app_sha256', 'source_sha256', 'native_elf_sha256', 'factory_elf_sha256')


def validate_selectors(report, expected):
    """Check fixture identity, valid pixels/guards and early invalid rejection."""
    def require(value, message):
        if not value:
            raise ValueError('JPEG selector evidence: ' + message)
    require(report['passed'] and report['inputs_unchanged'], 'run did not pass')
    require(all(report[key] == expected[key] for key in IDENTITY), 'wrong executable/source identity')
    fixtures = {name: (valid, hashlib.sha256(data).hexdigest()) for name, valid, data in cases()}
    require(len(report['cases']) == len(fixtures) == 168 and
            {row['name'] for row in report['cases']} == set(fixtures), 'missing or duplicate cases')
    for row in report['cases']:
        valid, digest = fixtures[row['name']]
        require(row['passed'] and row['expected_valid'] is valid and row['fixture_sha256'] == digest,
                'wrong fixture/classification')
        draw, check = row['native'], row['validation']
        require(check['changed_pixels'] == 0, 'validation drew pixels')
        if valid:
            require(draw['result'] == check['result'] == 0 and draw['decoder_started'] and
                    check['decoder_started'] and draw['pixel_differences'] == 0, 'valid pixels/guards differ')
        else:
            require(draw['result'] == check['result'] == 0x102 and not draw['decoder_started'] and
                    not check['decoder_started'] and draw['changed_pixels'] == 0,
                    'invalid selector reached entropy or output')


def rejection_checks(report):
    """Prove consumers reject incomplete, stale, swapped and falsely passed results."""
    expected = {key: report[key] for key in IDENTITY}
    validate_selectors(report, expected)
    results = []
    for name in ('missing-case', 'changed-input', 'wrong-elf', 'wrong-fixture',
                 'accepted-invalid', 'entropy-started', 'validation-drew', 'valid-guard'):
        candidate = deepcopy(report)
        invalid = next(row for row in candidate['cases'] if not row['expected_valid'])
        valid = next(row for row in candidate['cases'] if row['expected_valid'])
        if name == 'missing-case': candidate['cases'].pop()
        elif name == 'changed-input': candidate['inputs_unchanged'] = False
        elif name == 'wrong-elf': candidate['native_elf_sha256'] = '0' * 64
        elif name == 'wrong-fixture': valid['fixture_sha256'] = '0' * 64
        elif name == 'accepted-invalid': invalid['validation']['result'] = 0
        elif name == 'entropy-started': invalid['native']['decoder_started'] = True
        elif name == 'validation-drew': valid['validation']['changed_pixels'] = 1
        else: valid['native']['pixel_differences'] = 1
        try:
            validate_selectors(candidate, expected)
        except (ValueError, KeyError):
            results.append(dict(name=name, passed=True))
        else:
            raise ValueError('Consumer accepted invalid selector evidence: ' + name)
    return results


def validate_selector_evidence(report, expected, guards):
    """Apply the same complete gate in suite publication and artifact validation."""
    validate_selectors(report, expected)
    if len(guards) != 8 or not all(row['passed'] for row in guards) or guards != rejection_checks(report):
        raise ValueError('JPEG selector evidence rejection controls did not pass')


def validate_photo_selectors(report):
    """Require real HTTP publication/download and absent invalid selected tables."""
    rows = report['selector_uploads']
    fixtures = {name: (valid, data) for name, valid, data in upload_cases()}
    if set(rows) != set(fixtures) or any(report['checks'].get(name) is not True for name in
                                       ('selector_uploads_valid', 'selector_missing_rejected')):
        raise ValueError('Missing JPEG selector upload evidence')
    for name, (valid, data) in fixtures.items():
        row = rows[name]
        if (row['expected_valid'] is not valid or not row['passed'] or row['fixture_bytes'] != len(data) or
                row['fixture_sha256'] != hashlib.sha256(data).hexdigest() or row['finish_status'] != (200 if valid else 400) or
                row['metadata'] != dict(exists=valid, size=len(data) if valid else 0) or row['exact_download'] is not valid):
            raise ValueError('JPEG selector upload result differs: ' + name)
