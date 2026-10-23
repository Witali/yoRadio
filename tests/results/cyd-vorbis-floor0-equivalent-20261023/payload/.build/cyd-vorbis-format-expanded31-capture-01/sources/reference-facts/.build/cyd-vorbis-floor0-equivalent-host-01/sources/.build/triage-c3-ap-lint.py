from collections import Counter
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
old_path = root / '.build/lint-c3-network-power-final/report.json'
new_path = root / '.build/lint-c3-ap-timeout-01/report.json'
old, new = [json.loads(path.read_text(encoding='utf-8')) for path in (old_path, new_path)]
def normalize(path):
    path = path.replace('\\', '/')
    if '/native-httpd-rfc6455/' in path:
        return 'httpd-overlay/' + path.rsplit('/', 1)[1]
    return path
def diagnostics(row):
    return Counter((normalize(d['file']), d['severity'], d['check'], d['message'])
                   for d in row['diagnostics'])
previous = {normalize(row['file']): row for row in old['results']}
assert len(previous) == new['units'] == 65
deltas = []
for row in new['results']:
    prior = previous[normalize(row['file'])]
    before, after = diagnostics(prior), diagnostics(row)
    if before != after:
        deltas.append({'file': row['file'], 'new': list((after-before).elements()),
                       'removed': list((before-after).elements())})
assert old['config_sha256'] == new['config_sha256']
assert new['complete'] and new['errors'] == 0 and new['all_inputs_unchanged_after_analysis']
assert not deltas, deltas
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = dict(passed=True, units=65, warnings=new['warnings'], errors=new['errors'],
              baseline_report_sha256=sha(old_path), current_report_sha256=sha(new_path),
              sdkconfig_identical=True, diagnostic_multisets_identical_ignoring_line_offsets=True,
              diagnostic_deltas=deltas, changed_production_unit_warnings={
                  row['file']: len(row['diagnostics']) for row in new['results']
                  if row['file'].endswith(('/network_service.c', '/runtime_settings.c', '/websocket_service.c'))},
              scope='Compare every complete-unit diagnostic by path/severity/check/message; normalize only generated overlay directory names and ignore source line offsets. This does not resolve or suppress pre-existing warnings. All 758 Clang inputs were frozen and verified unchanged after analysis.')
(root / '.build/c3-ap-lint-triage.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, indent=2))
