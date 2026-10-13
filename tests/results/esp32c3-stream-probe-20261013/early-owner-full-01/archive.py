from pathlib import Path
import hashlib
import json
import shutil

root = Path.cwd()
destination = root / 'tests/results/esp32c3-stream-probe-20261013/early-owner-full-01'
destination.mkdir(parents=True, exist_ok=False)
(destination / '.gitattributes').write_text('* -text\n')

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

summary = dict(production_qualified=False, runs={})
for label, directory, controller in (
    ('full-https', 'early-owner-full-https-01', 'stream_probe.py'),
    ('prefix-https', 'early-owner-prefix-https-01', 'prefix_control.py'),
    ('held-https', 'early-owner-held-https-01', 'prefix_control.py'),
):
    source = root / '.build' / directory
    report = json.loads((source / 'results.json').read_text())
    assert report['controller_sha256'] == digest(root / 'tools/esp32c3_tests' / controller)
    assert report['installed']['app_elf_sha256'] == report['candidate']['app_elf_sha256']
    restore = report['restoration']
    restored = (restore['image']['app_elf_sha256'] == report['initial']['app_elf_sha256']
                and not restore['status']['audio']
                and all(restore[k] is True for k in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged')))
    target = destination / label
    target.mkdir()
    shutil.copyfile(source / 'results.json', target / 'results.json')
    if (source / 'audit.json').exists():
        shutil.copyfile(source / 'audit.json', target / 'audit.json')
    health = []
    for case in report['cases']:
        for key in ('before', 'after', 'active_before', 'active_after', 'failure_health'):
            if key in case:
                health.append(case[key])
        health.extend(case.get('transition_health', []))
    summary['runs'][label] = dict(
        cases=len(report['cases']),
        failures=sum(c.get('result') != 'PASS' for c in report['cases']),
        restored=restored,
        allocation_failures=max(h['allocation_failures'] for h in health),
        decoder_failures=max(h['decoder_failure']['sequence'] for h in health),
        watchdog_events=max(h['task_watchdog_events'] for h in health),
        lifetime_min_heap=min(h['minimum_heap'] for h in health),
        heap_recovery=report.get('heap_recovery'),
    )
for relative in (
    'tools/esp32c3_tests/stream_probe.py',
    'tools/esp32c3_tests/stream_probe_cases.py',
    'tools/esp32c3_tests/audit_stream_probe.py',
    'tools/esp32c3_tests/prefix_control.py',
    'tools/esp32c3_tests/common.py',
    'tools/esp32c3_tests/production_health.py',
    'tools/esp32c3_tests/ota.py',
    'tools/esp32c3_tests/connection_retry.py',
    'tools/esp32c3_tests/tls_error_codes.py',
    'tools/audio_test_server/server.py',
    'tools/audio_test_server/icy.py',
):
    target = destination / 'sources' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / relative, target)
summary['scope'] = ('Finite physical HTTPS format/transition matrix and TLS prefix cancellation controls. '
                    'No absolute RAM floor. No acoustic continuity or long-run qualification claim. '
                    'Original firmware and private settings restoration checked per run.')
save(destination / 'summary.json', summary)
shutil.copyfile(__file__, destination / 'archive.py')
save(destination / 'sha256.json', {
    p.relative_to(destination).as_posix(): digest(p)
    for p in sorted(destination.rglob('*')) if p.is_file() and p.name != 'sha256.json'
})
print(json.dumps(summary, indent=2))
