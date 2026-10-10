import hashlib
import json
from pathlib import Path

root = Path('.build/c3-rxonly-physical-20261008')
physical = root / 'physical'
final = json.loads((physical / 'final-board.json').read_text())
assert final['result'] == 'PASS'
reports = {name: json.loads((physical / name / 'report.json').read_text())
           for name in ('records', 'framing', 'formats')}
for name, report in reports.items():
    assert all(case['result'] == 'PASS' for case in report['cases']), name
counts = {name: len(report['cases']) for name, report in reports.items()}
formats = [c for c in reports['formats']['cases']
           if c['name'].startswith(('http:', 'https:'))]
assert len(formats) == 44
assert sum(c['name'].startswith('tls-record:') for c in reports['records']['cases']) == 4
assert sum(c['name'].startswith('framing:') for c in reports['framing']['cases']) == 8
algorithms = sorted({(event.get('tls_version'), event.get('tls_cipher'))
                     for event in reports['formats'].get('tls_events', [])
                     if event.get('tls_version')})
faults = {}
for name in reports:
    rows = json.loads((physical / name / 'performance.json').read_text())
    faults[name] = [row for row in rows if any(token in row.get('line', '').lower()
                   for token in ('task_timeouts=', 'task watchdog', 'alloc failed',
                                 'allocation failed', 'guru meditation', 'panic'))]
summary = dict(result='PASS', scope='Short physical qualification only',
               report_case_counts=counts, format_cases=len(formats),
               format_algorithms=algorithms, captured_fault_rows=faults,
               records=[c for c in reports['records']['cases']
                        if c['name'].startswith('tls-record:')],
               restoration=final)
(root / 'short-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
folder = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly')
manifest_path = folder / 'manifest.json'
manifest = json.loads(manifest_path.read_text())
assert hashlib.sha256((folder / 'app.bin').read_bytes()).hexdigest() == manifest['image']['sha256']
manifest['qualification'] = ('Laboratory only; build/linked audits and short physical tests pass: '
    '44 HTTP/HTTPS format cases, 4 TLS record modes at 75 seconds, 8 framing/closure cases. '
    'Ten-minute matched-priority comparison and remaining acceptance gates pending; NOT_QUALIFIED.')
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
qualification_path = folder / 'qualification.json'
qualification = json.loads(qualification_path.read_text())
assert qualification['result'] == 'NOT_QUALIFIED'
qualification.update(physical_tests=True, short_physical_tests=dict(
    http_https_formats=44, tls_record_modes=4, tls_record_seconds=75,
    tls_framing_modes=8, restoration='PASS',
    evidence='tests/results/esp32c3-rxonly-physical-20261008'),
    pending=['Ten-minute matched-priority AAC comparison', 'Ten-minute FLAC playback',
             'Remaining acceptance gates in docs/ESP32C3_TLS_RX_RESERVE_20261008.md'])
qualification_path.write_text(json.dumps(qualification, indent=2) + '\n')
print(json.dumps(dict(cases=counts, algorithms=algorithms,
                     captured_fault_rows={name: len(rows) for name, rows in faults.items()},
                     restoration=final['result']), indent=2))
