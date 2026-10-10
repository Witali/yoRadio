"""Additional output-counter analysis of bounded finite-file playback windows.

These short windows do not replace sustained-stream qualification or analog
measurement. Startup, EOF and deliberate network-fault windows are excluded.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'test-sources/tools/esp32c3_tests'))
from common import Failure, check_playback, matches as format_matches, require
from production_health import check_health, output_window

folder = ROOT / 'physical/local'
report = json.loads((folder / 'report.json').read_text())
batches = json.loads((folder / 'status.json').read_text())
health = json.loads((folder / 'health.json').read_text())
specs = json.loads((ROOT / 'fixture-specs.json').read_text())
actions = {a['name']: a for a in report['actions']}
results = {}
for case in report['cases']:
    name = case['name']
    if not name.startswith('http:'):
        continue
    _, fixture, hint = name.split(':')
    spec, action = specs[fixture], actions[name]
    require(spec['sha256'] == report['fixture_hashes'][fixture], 'Fixture hash differs')
    matches = [b for b in batches if b['case'] == fixture and
               action['started_at'] <= b['started_at'] <= b['ended_at'] <= action['ended_at']]
    result = dict(original_gate=case['result'], hint=hint, fixture=fixture)
    try:
        require(len(matches) == 1, 'Missing or ambiguous finite playback window')
        batch = matches[0]
        require('interrupted' not in batch, 'Interrupted observation')
        rows = [h for h in health if batch['started_at'] <= h['at'] <= batch['ended_at']]
        require(len(rows) == len(batch['samples']), 'Unpaired status/health')
        check_playback(batch['samples'], spec)
        measured = [h for s, h in zip(batch['samples'], rows) if s['seconds'] >= 2]
        result.update(output=output_window(measured), health=check_health(measured),
                      first_full_pcm_seconds=next(s['seconds'] for s in batch['samples'] if format_matches(s, spec)),
                      maximum_status_health_ms=max(s['request_ms'] for s in batch['samples']))
        require(result['output']['completion_queue_drops'] == 0, 'Completion queue drop in finite playback window')
        require(result['output']['write_errors'] == 0, 'I2S write error in finite playback window')
        result['result'] = 'PASS'
    except Failure as error:
        result.update(result='FAIL', reason=str(error))
    results[name] = result
summary = dict(scope='Short finite-file windows after 2 s warmup and before EOF observation; not sustained or acoustic qualification',
               counts=dict(passed=sum(r['result'] == 'PASS' for r in results.values()), total=len(results)),
               failed=[name for name, row in results.items() if row['result'] != 'PASS'], windows=results)
(ROOT / 'file-output-windows.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'windows'}))
