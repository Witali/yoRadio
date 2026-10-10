"""Reanalyze public playback windows without erasing the runner's verdicts."""
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'test-sources/tools/esp32c3_tests'))
from common import Failure, check_playback, check_recovery_heap, matches, require
from production_health import check_health, output_window
from sustained_output import sustained_window, check_output, check_memory
from aac_reference import verified_spec

P = ROOT / 'physical'
report = json.loads((P / 'public/report.json').read_text())
health = json.loads((P / 'public/health.json').read_text())
batches = json.loads((P / 'public/status.json').read_text())
initial = json.loads((P / 'initial.json').read_text())
streams = json.loads((ROOT / 'public_streams.json').read_text())['streams']
assert report['board']['app_elf_sha256'] == initial['candidate']['app_elf_sha256']
assert report['public_urls'] == streams
assert report['test_sources_sha256'] == initial['test_sources_sha256']
assert hashlib.sha256((ROOT / 'physical.py').read_bytes()).hexdigest() == initial['controller_sha256']
for name, digest in initial['test_sources_sha256'].items():
    assert hashlib.sha256((ROOT / 'test-sources' / name).read_bytes()).hexdigest() == digest, name
cases = {c['name']: c for c in report['cases']}
assert len(cases) == len(report['cases']) == 10
assert all('https:' + name in cases for name in streams)

def evaluate(fn):
    try:
        return dict(result='PASS', evidence=fn())
    except Failure as error:
        return dict(result='FAIL', reason=str(error))

windows = {}
for name in streams:
    original = cases['https:' + name]
    reference = report.get('references', {}).get(name)
    selected = [b for b in batches if b['case'] == 'https:' + name]
    if not reference or len(selected) != 1 or 'interrupted' in selected[0]:
        windows[name] = dict(original=original, result='INCOMPLETE',
                             reason='Missing reference or complete observation')
        continue
    batch, spec = selected[0], reference['spec']
    assert reference['tls_verify'] is True
    if spec['codec'] == 'aac':
        assert verified_spec(reference['ffprobe_spec'], reference['faad'], reference['frames']) == spec
    rows = [h for h in health if batch['started_at'] <= h['at'] <= batch['ended_at']]
    steady, measured = sustained_window(batch['samples'], rows, report['public_seconds'])
    def format_check():
        first = next((s['seconds'] for s in batch['samples'] if matches(s, spec)), None)
        require(first is not None and first <= 15, 'Full PCM format arrived after warmup')
        return dict(first_full_pcm_seconds=first, **check_playback(batch['samples'], spec,
                    minimum=int((report['public_seconds'] - 15) * .6), warmup=15))
    maximum = max(s['request_ms'] for s in batch['samples'])
    def response_check():
        require(maximum < 2000, 'WebUI response exceeded 2 seconds')
        return dict(maximum_ms=maximum)
    below = [h for h in measured if h['largest'] < 8192 or h['heap'] < 16384]
    windows[name] = dict(original=original, spec=spec, output=output_window(measured),
        health=check_health(measured), maximum_status_health_ms=maximum,
        rssi_range=[min(s['rssi'] for s in batch['samples']), max(s['rssi'] for s in batch['samples'])],
        checks=dict(format=evaluate(format_check), output=evaluate(lambda: check_output(measured)),
                    memory=evaluate(lambda: check_memory(measured)), response=evaluate(response_check)),
        below_budget_samples=[dict(seconds=h['at'] - batch['started_at'], heap=h['heap'], largest=h['largest']) for h in below])

faults = check_health(health)
recovery = evaluate(lambda: check_recovery_heap(report['idle']['initial'], report['idle']['public']))
restored = json.loads((P / 'restoration.json').read_text())
assert restored['identity']['app_elf_sha256'] == initial['quiet']['app_elf_sha256']
assert all(restored['persistence'].values())
assert len(restored['states']) == 3 and all(not s['audio'] for s in restored['states'])
passed = sum(c['result'] == 'PASS' for c in cases.values())
assert json.loads((P / 'phase.json').read_text())['code'] == (0 if passed == len(cases) else 1)
result = dict(review='PASS', original_acceptance=dict(passed=passed, total=len(cases)),
    original_failures=[dict(name=n, reason=c.get('reason')) for n,c in cases.items() if c['result'] != 'PASS'],
    scope='Original live gates retained; additional paired windows start at batch time + 15 s, which may differ slightly from the live runner pre-command timestamp',
    windows=windows, lifetime_health=faults, sdk_lifetime_minimum_heap=min(h['minimum_heap'] for h in health),
    recovery=recovery, exact_listened_image_restored=True,
    idle_medians={n:{k:statistics.median(h[k] for h in rows) for k in ('heap','largest','tasks')}
                  for n,rows in report['idle'].items()})
encoded = json.dumps(result, indent=2) + '\n'
target = ROOT / 'review.json'
if target.exists():
    assert target.read_text() == encoded
else:
    target.write_text(encoded)
print(json.dumps({k:v for k,v in result.items() if k not in ('windows','idle_medians')}))
for name, window in windows.items():
    print(name, json.dumps({k:v for k,v in window.items() if k not in ('original', 'below_budget_samples')}))
