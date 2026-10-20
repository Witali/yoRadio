"""Consume bounded JPEG header evidence without accepting incomplete controls."""
from copy import deepcopy

VALID = {f'{mode}-baseline' for mode in ('gray', 'rgb')}
VALID |= {f'{mode}-dri-valid-{value}' for mode in ('gray', 'rgb') for value in (0, 1, 65535)}
VALID |= {f'{mode}-quantizer-255' for mode in ('gray', 'rgb')}
VALID |= {f'gray-component-id-{value}' for value in (0, 17, 255)} | {'rgb-custom-component-ids'}
INVALID = {f'{mode}-dri-length-{value}' for mode in ('gray', 'rgb') for value in (0, 1, 3, 4, 16)}
INVALID |= {f'{mode}-sos-length-{value}' for mode, length in (('gray', 6), ('rgb', 10))
            for value in (*range(length), *range(length + 1, length + 4))}
INVALID |= {f'{mode}-sos-{field}-{value}' for mode in ('gray', 'rgb')
            for field, values in (('ss', (1, 255)), ('se', (0, 62)), ('ahal', (1, 16, 255))) for value in values}
INVALID |= {'gray-unknown-component-0'} | {f'rgb-unknown-component-{index}' for index in range(3)}
INVALID |= {'duplicate-frame-1-1-3', 'duplicate-frame-1-2-1', 'duplicate-frame-2-2-3', 'duplicate-scan', 'reordered-scan'}
INVALID |= {f'zero-quantizer-{index}' for index in range(64)}


def validate_headers(report, expected):
    """Require named boundaries, actual decoder entry observation and full pixel guards."""
    def require(value, message):
        if not value:
            raise ValueError('JPEG header evidence: ' + message)
    require(report['passed'] and report['inputs_unchanged'], 'run did not pass')
    for field in ('app_sha256', 'source_sha256', 'native_elf_sha256', 'factory_elf_sha256'):
        require(report[field] == expected[field], 'wrong ' + field)
    rows = report['cases']
    require(len(rows) == len(VALID | INVALID) and {row['name'] for row in rows} == VALID | INVALID,
            'missing or duplicate boundaries')
    for row in rows:
        valid = row['name'] in VALID
        require(row['passed'] and row['expected_valid'] is valid, 'wrong case classification')
        require(row['validation']['changed_pixels'] == 0, 'validation drew pixels')
        if valid:
            require(row['validation']['result'] == 0 and row['validation']['decoder_started'], 'valid validation skipped')
            require(all(row[tag]['result'] == 0 and row[tag]['decoder_started'] and row[tag]['pixel_differences'] == 0
                        for tag in ('factory', 'native')), 'valid pixels/guards differ')
        else:
            require(row['native']['result'] == row['validation']['result'] == 0x102 and
                    not row['native']['decoder_started'] and not row['validation']['decoder_started'] and
                    row['native']['changed_pixels'] == 0, 'malformed header accepted or reached entropy')


def rejection_checks(report):
    """Reject omitted, stale, accepted-invalid and incorrectly drawn evidence."""
    expected = {key: report[key] for key in ('app_sha256', 'source_sha256', 'native_elf_sha256', 'factory_elf_sha256')}
    validate_headers(report, expected)
    results = []
    for name in ('missing-case', 'changed-input', 'wrong-elf', 'accepted-invalid', 'entropy-started', 'validation-drew', 'valid-guard'):
        candidate = deepcopy(report)
        invalid = next(row for row in candidate['cases'] if not row['expected_valid'])
        valid = next(row for row in candidate['cases'] if row['expected_valid'])
        if name == 'missing-case': candidate['cases'].pop()
        elif name == 'changed-input': candidate['inputs_unchanged'] = False
        elif name == 'wrong-elf': candidate['native_elf_sha256'] = '0' * 64
        elif name == 'accepted-invalid': invalid['validation']['result'] = 0
        elif name == 'entropy-started': invalid['native']['decoder_started'] = True
        elif name == 'validation-drew': invalid['validation']['changed_pixels'] = 1
        else: valid['native']['pixel_differences'] = 1
        try:
            validate_headers(candidate, expected)
        except (ValueError, KeyError):
            results.append({'name': name, 'passed': True})
        else:
            raise ValueError('Consumer accepted invalid header evidence: ' + name)
    return results
