"""Offline audit of the frozen HTTPS run; no board access or private data."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
r = json.loads((root / 'results.json').read_text())
assert r['transport'] == 'https'
assert len(r['cases']) == 16
assert hashlib.sha256((root / 'stream_probe.py').read_bytes()).hexdigest() == r['controller_sha256']
assert r['installed']['app_elf_sha256'] == r['candidate']['app_elf_sha256']
restored = r['restoration']
assert restored['image']['app_elf_sha256'] == r['initial']['app_elf_sha256']
assert not restored['status']['audio']
assert all(restored[k] is True for k in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'))
negative = {'unknown', 'partial', 'truncated-id3'}
rows = []
for case in r['cases']:
    name = case['name']
    assert case['result'] == 'PASS', name
    before, after = case['before'], case['after']
    for key in ('boot_id', 'allocation_failures', 'task_watchdog_events'):
        assert before[key] == after[key], (name, key)
    assert after['allocation_failures'] == after['task_watchdog_events'] == 0
    events = [e for e in r['server'] if e.get('fixture') == name]
    tls = [e for e in events if e.get('tls_version') and e.get('tls_cipher')]
    assert tls, name
    if name not in negative:
        assert any(e.get('complete') is True and e['sent'] == r['fixtures'][name]['bytes'] for e in tls), name
    active = case.get('transition_health', [])
    if 'active_before' in case:
        active = [case['active_before'], case['active_after']]
    if name not in negative:
        assert len(active) >= 2, name
        assert active[-1]['uptime_ms'] > active[0]['uptime_ms']
        for health in active:
            assert health['boot_id'] == before['boot_id']
            assert health['allocation_failures'] == health['task_watchdog_events'] == 0
            assert health['output']['available'] is True
            assert health['output'] == active[0]['output'], name
    rows.append(dict(name=name, result='PASS', active_health_samples=len(active),
        sampled_minimum_heap=min((h['heap'] for h in active), default=None),
        sampled_minimum_largest=min((h['largest'] for h in active), default=None),
        idle_after_heap=after['heap'], idle_after_largest=after['largest'],
        completion_drops_whole_case=after['output']['completion_queue_drops']-before['output']['completion_queue_drops'],
        tls_versions=sorted({e['tls_version'] for e in tls}),
        tls_ciphers=sorted({e['tls_cipher'] for e in tls})))
summary=dict(result='PASS', cases=rows, restored=True,
    scope='16 finite HTTPS cases; active health snapshots only. No sample-exact PCM, acoustic, long-playback, all-underrun or lifetime-zero-overrun claim.')
(root/'summary.json').write_bytes((json.dumps(summary, indent=2)+'\n').encode())
print(json.dumps(summary, indent=2))
