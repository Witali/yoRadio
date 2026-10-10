import json
from pathlib import Path

root = Path(__file__).resolve().parent
image = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve')
summary = dict(status='NOT_QUALIFIED_FOR_PRODUCTION',
               report='docs/ESP32C3_TLS_RESERVE_20261008.md', physical_runs=[])
for name in ('physical/tls-alternate', 'matrix/records', 'matrix/framing', 'matrix/formats'):
    report = json.loads((root/name/'report.json').read_text())
    rows = json.loads((root/name/'performance.json').read_text())
    faults = [row for row in rows if 'PERF allocation failed:' in row['line']]
    cases = [dict(name=c['name'], result=c['result'], reason=c.get('reason')) for c in report['cases']]
    summary['physical_runs'].append(dict(name=name, cases=cases,
        allocation_failures=len(faults), first_allocation_failure=faults[:1],
        pool_events=[r for r in rows if 'TLS_RESERVE capacity=' in r['line']],
        input_events=[r for r in rows if 'TLS_INPUT released=' in r['line']]))
summary['restoration'] = {}
for name in ('physical', 'matrix'):
    final = json.loads((root/name/'final-board.json').read_text())
    assert final['result'] == 'PASS'
    summary['restoration'][name] = final['result']
(root/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
(image/'qualification.json').write_text(json.dumps(summary, indent=2)+'\n')
manifest = json.loads((image/'manifest.json').read_text())
manifest['qualification'] = ('NOT QUALIFIED: four paced full/small TLS record modes pass 75 s each, '
    'but all eight TLS framing cases fail (67 allocation failures) and 13 of 44 HTTP/HTTPS '
    'file cases fail (99 allocation failures). Laboratory-only trust root. '
    'Ordinary awake image restored and settings/playback verified after both controllers.')
(image/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print('Saved late-reclamation qualification')
