from pathlib import Path
import hashlib
import json
import shutil

root = Path.cwd()
source = root/'.build/early-owner-public-full-http-01'
destination = root/'tests/results/esp32c3-stream-probe-20261013/early-owner-public-full-01'
report = json.loads((source/'results.json').read_text())
audit = json.loads((source/'audit.json').read_text())
assert audit['passed'] and len(audit['cases']) == 20
assert all(c['decoder_health']['missing'] == 0 for c in audit['cases'])

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert report['controller_sha256'] == digest(root/'tools/esp32c3_tests/stream_probe.py')
assert report['candidate'] == json.loads((root/'firmware/development/esp32c3-idf-6.1-r9a97-early-owner-public/manifest.json').read_text())['image']
destination.mkdir(parents=True, exist_ok=False)
(destination/'.gitattributes').write_text('* -text\n')
for name in ('results.json', 'audit.json'):
    shutil.copyfile(source/name, destination/name)
shutil.copyfile(__file__, destination/'archive.py')
for rel in ('tools/esp32c3_tests/stream_probe.py',
            'tools/esp32c3_tests/stream_probe_cases.py',
            'tools/esp32c3_tests/audit_stream_probe.py',
            'tools/esp32c3_tests/common.py',
            'tools/esp32c3_tests/production_health.py',
            'tools/esp32c3_tests/ota.py',
            'tools/esp32c3_tests/connection_retry.py',
            'tools/esp32c3_tests/tls_error_codes.py',
            'tools/audio_test_server/server.py',
            'tools/audio_test_server/icy.py',
            'tests/test-stream-probe-audit.py'):
    target = destination/'sources'/rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root/rel, target)
health = []
for case in report['cases']:
    for key in ('before', 'after', 'active_before', 'active_after', 'failure_health'):
        if key in case:
            health.append(case[key])
    health.extend(case.get('transition_health', []))
summary = dict(passed=True, cases=len(report['cases']), transport=report['transport'],
    image=report['candidate'], restoration_verified=audit['restored'],
    allocation_failures=max(h['allocation_failures'] for h in health),
    decoder_failures=max(h['decoder_failure']['sequence'] for h in health),
    watchdog_events=max(h['task_watchdog_events'] for h in health),
    lifetime_min_heap=min(h['minimum_heap'] for h in health),
    decoder_health_samples=sum(c['decoder_health']['checked'] for c in audit['cases']),
    production_qualified=False,
    scope='Finite HTTP AUTO format, terminal status and transition matrix on the exact public-root image. Sampled active output counters; no HTTPS matrix, analog continuity or full production qualification claim.')
(destination/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
checks = {p.relative_to(destination).as_posix():digest(p)
          for p in sorted(destination.rglob('*')) if p.is_file()}
(destination/'sha256.json').write_text(json.dumps(checks, indent=2)+'\n')
print(json.dumps(summary, indent=2))
