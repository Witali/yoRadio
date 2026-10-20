"""Share strict DHT evidence requirements between the runner and publication tools."""
from copy import deepcopy


def validate_dht(report, expected):
    """Require every named valid/invalid boundary and its actual machine observations."""
    def require(value, message):
        if not value:
            raise ValueError('JPEG DHT evidence: ' + message)
    require(report['passed'] and report['inputs_unchanged'], 'run or inputs did not pass')
    for field in ('app_sha256', 'source_sha256', 'native_elf_sha256', 'factory_elf_sha256'):
        require(report[field] == expected[field], 'different ' + field)
    legal = {0, 0xf0} | {run * 16 + size for run in range(16) for size in range(1, 11)}
    valid = {'minimal', 'all-legal-symbols', 'sparse-16-bit', 'last-legal-16-bit-word'}
    invalid = {'reserved-ac-%02x' % value for value in range(256) if value not in legal}
    invalid |= {'reserved-dc-%02x' % value for value in (12, 15, 255)}
    invalid |= {'all-one-dc-depth-%d' % depth for depth in range(1, 12)}
    invalid |= {'all-one-ac-depth-%d' % depth for depth in range(1, 17)}
    rows = report['cases']
    require(len(rows) == 128 and {row['name'] for row in rows} == valid | invalid, 'missing/duplicate boundary cases')
    for row in rows:
        require(row['passed'] and row['expected_valid'] is (row['name'] in valid), 'incorrect case result')
        require(row['validation_pixel_changes'] == 0, 'validation drew pixels')
        if row['name'] in valid:
            require(row['validation_result'] == 0 and row['validation_decoder_started'] and row['different_pixels'] == 0,
                    'valid decode differs or was skipped')
            require(all(row[tag]['result'] == 0 and row[tag]['decoder_started'] and
                        row[tag]['expected_pixel_differences'] == 0 for tag in ('factory', 'native')),
                    'valid pixels or guards differ')
        else:
            require(row['native']['result'] == row['validation_result'] == 0x102 and
                    not row['native']['decoder_started'] and not row['validation_decoder_started'] and
                    row['native']['changed_pixels'] == 0, 'malformed DHT accepted or reached entropy')


def rejection_checks(report):
    """Prove that incomplete, stale or contradictory reports cannot be published."""
    expected = {field: report[field] for field in ('app_sha256', 'source_sha256', 'native_elf_sha256', 'factory_elf_sha256')}
    validate_dht(report, expected)
    checks = []
    for name in ('missing-case', 'different-elf', 'changed-inputs', 'accepted-invalid',
                 'entropy-started', 'validation-drew', 'valid-guard-changed'):
        broken = deepcopy(report)
        invalid = next(row for row in broken['cases'] if not row['expected_valid'])
        if name == 'missing-case': broken['cases'].pop()
        elif name == 'different-elf': broken['native_elf_sha256'] = '0' * 64
        elif name == 'changed-inputs': broken['inputs_unchanged'] = False
        elif name == 'accepted-invalid': invalid['validation_result'] = 0
        elif name == 'entropy-started': invalid['native']['decoder_started'] = True
        elif name == 'validation-drew': invalid['validation_pixel_changes'] = 1
        else: broken['cases'][0]['native']['expected_pixel_differences'] = 1
        try:
            validate_dht(broken, expected)
        except (ValueError, KeyError):
            checks.append(dict(name=name, passed=True))
        else:
            checks.append(dict(name=name, passed=False))
    return checks


def validate_photo_dht(report):
    """Require real upload/finalize rejection and no published invalid photo."""
    cases = report['invalid_dht']
    if (set(cases) != {'reserved-ac-size', 'reserved-ac-zero', 'all-one-ac-word'} or
            not report['checks']['reserved_dht_rejected'] or any(row['finish_status'] != 400 or
            row['metadata'] != {'exists': False, 'size': 0} for row in cases.values())):
        raise ValueError('JPEG DHT photo upload accepted or omitted a reserved-table case')
