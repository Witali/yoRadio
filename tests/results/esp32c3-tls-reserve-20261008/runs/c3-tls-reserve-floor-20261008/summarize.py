import json
from pathlib import Path

root = Path(__file__).resolve().parent
image = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-floor')
summary = dict(status='NOT_QUALIFIED_FOR_PRODUCTION',
               report='docs/ESP32C3_TLS_RESERVE_20261008.md', physical_runs=[])
for name in ('matrix/framing', 'matrix/records', 'extended/formats',
             'extended/small-repeat', 'extended/alternate-600', 'repeat/tls-small'):
    path = root/name/'report.json'
    if not path.exists():
        summary['physical_runs'].append(dict(name=name, result='NOT_RUN'))
        continue
    report = json.loads(path.read_text())
    rows = json.loads((root/name/'performance.json').read_text())
    faults = [row for row in rows if 'PERF allocation failed:' in row['line']]
    summary['physical_runs'].append(dict(name=name,
        cases=[dict(name=c['name'], result=c['result'], reason=c.get('reason'),
                    evidence=c.get('evidence'), exception_chain=c.get('exception_chain'))
               for c in report['cases']],
        allocation_failures=len(faults), first_allocation_failure=faults[:1],
        pool_events=[r for r in rows if 'TLS_RESERVE capacity=' in r['line']],
        input_events=[r for r in rows if 'TLS_INPUT released=' in r['line']]))
summary['restoration'] = {}
for name in ('matrix', 'extended', 'repeat'):
    final = json.loads((root/name/'final-board.json').read_text())
    assert final['result'] == 'PASS'
    summary['restoration'][name] = final['result']
summary['limits'] = ['Retain original small-record WebUI timeout as a failure; do not replace it with a repeat.',
    'Separate physical memory/format gates from acoustic/DMA continuity and PCM identity.',
    'Public stations, negative certificate cases, high-depth FLAC/LPC32 and extended reconnect/load/OTA qualification remain.']
(root/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
(image/'qualification.json').write_text(json.dumps(summary, indent=2)+'\n')
manifest = json.loads((image/'manifest.json').read_text())
manifest['qualification'] = ('NOT QUALIFIED FOR PRODUCTION: startup input minimum with a static full-record TLS slot; '
    'laboratory-only trust root. Detailed passing and failed physical cases are retained in qualification.json '
    'and docs/ESP32C3_TLS_RESERVE_20261008.md. Original small-record polling timeout remains a failure. '
    'All three controllers restored the ordinary awake image and verified settings/playback.')
(image/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print('Saved startup-minimum qualification')
