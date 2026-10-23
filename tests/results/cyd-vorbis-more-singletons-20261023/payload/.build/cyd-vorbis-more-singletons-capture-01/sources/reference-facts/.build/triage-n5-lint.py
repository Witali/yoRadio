from collections import Counter
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
previous = json.loads((root / 'tests/results/network-power-transfer-20261019/lint-cyd/report.json').read_text(encoding='utf-8'))
current = json.loads((root / '.build/lint-cyd-network-n5-01/report.json').read_text(encoding='utf-8'))

def diagnostics(report):
    return Counter((re.sub(r'/build-[^/]+/', '/BUILD/', unit['file']), item['check'], item['message'])
                   for unit in report['results'] for item in unit['diagnostics'] if item['severity'] == 'warning')

new = diagnostics(current) - diagnostics(previous)
removed = diagnostics(previous) - diagnostics(current)
rows = []
for (file, check, message), count in sorted(new.items()):
    if check == 'bugprone-suspicious-string-compare':
        assessment = 'Intentional nonzero string/binary comparison in a boolean condition; false is equality. No inverted predicate or unbounded read found.'
    elif check == 'bugprone-not-null-terminated-result' and file.endswith('/network_settings.c'):
        assessment = 'NNET is the four-byte magic of a canonical binary32-byte NVS record, not a C string. The record is zeroed first and no string API reads its magic.'
    else:
        raise AssertionError((file, check, message))
    rows.append(dict(file=file, check=check, message=message, instances=count, assessment=assessment))
assert current['complete'] and current['errors'] == 0 and current['all_inputs_unchanged_after_analysis']
assert previous['warnings'] == 81 and current['warnings'] == 86 and sum(new.values()) == 5 and not removed
result = dict(passed=True, previous_units=previous['units'], current_units=current['units'],
              previous_warnings=previous['warnings'], current_warnings=current['warnings'],
              errors=current['errors'], new_warning_instances=sum(new.values()), new_warning_triage=rows,
              scope='All 52 actual Clang units and 652 frozen inputs passed; five new low-risk diagnostics reviewed explicitly. No warning suppression, no firmware-code-generation or hardware claim.')
(root / '.build/n5-lint-triage.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: value for key, value in result.items() if key != 'new_warning_triage'}))
