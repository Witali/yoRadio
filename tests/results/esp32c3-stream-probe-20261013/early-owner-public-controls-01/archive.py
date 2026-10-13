from pathlib import Path
import hashlib
import json
import shutil
import statistics
import sys

root = Path.cwd()
sys.path.insert(0, str(root/'tools/esp32c3_tests'))
from audit_stream_probe import check_decoder_faults
from common import check_recovery_heap

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

destination = root/'tests/results/esp32c3-stream-probe-20261013/early-owner-public-controls-01'
destination.mkdir(exist_ok=False)
(destination/'.gitattributes').write_text('* -text\n')
summary = dict(production_qualified=False, runs={})
for label in ('held', 'prefix'):
    source = root/f'.build/early-owner-public-{label}-http-01/results.json'
    r = json.loads(source.read_text())
    assert r['controller_sha256'] == sha(root/'tools/esp32c3_tests/prefix_control.py')
    assert r['watchdog_disabled_verified'] and r['heap_recovery'] == 'PASS'
    assert r['installed']['app_elf_sha256'] == r['candidate']['app_elf_sha256']
    assert r['candidate'] == json.loads((root/'firmware/development/esp32c3-idf-6.1-r9a97-early-owner-public/manifest.json').read_text())['image']
    restore = r['restoration']
    assert restore['image']['app_elf_sha256'] == r['initial']['app_elf_sha256']
    assert not restore['status']['audio']
    assert all(restore[k] for k in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'))
    assert [c['name'] for c in r['cases']] == ['deadline-without-watchdog', 'stop-during-prefix', 'replace-during-prefix']
    assert all(c['result'] == 'PASS' for c in r['cases'])
    assert 9.5 <= r['cases'][0]['deadline_seconds'] <= 13
    assert r['cases'][1]['stop_seconds'] < 2
    assert r['cases'][2]['replacement_seconds'] < 12
    c = r['cases'][2]
    assert c['active_before']['output'] == c['active_after']['output']
    checks = [check_decoder_faults(c, required=True) for c in r['cases']]
    health = r['idle_before'] + r['idle_after']
    for c in r['cases']:
        health.extend(c[k] for k in ('before','after','active_before','active_after') if k in c)
    assert len({h['boot_id'] for h in health}) == 1
    assert all(h['allocation_failures'] == h['task_watchdog_events'] == h['decoder_failure']['sequence'] == 0 for h in health)
    check_recovery_heap(r['idle_before'], r['idle_after'])
    shutil.copyfile(source, destination/f'{label}.json')
    summary['runs'][label] = dict(passed=3, restored=True, decoder_health=checks,
        deadline_seconds=r['cases'][0]['deadline_seconds'], stop_seconds=r['cases'][1]['stop_seconds'],
        replacement_seconds=r['cases'][2]['replacement_seconds'],
        lifetime_min_heap=min(h['minimum_heap'] for h in health),
        settled_medians={k:[statistics.median(h[k] for h in r[phase]) for phase in ('idle_before','idle_after')] for k in ('heap','largest')},
        allocation_failures=0, decoder_failures=0, watchdog_events=0)
for rel in ('tools/esp32c3_tests/prefix_control.py','tools/esp32c3_tests/audit_stream_probe.py',
            'tools/esp32c3_tests/stream_probe_cases.py','tools/esp32c3_tests/common.py',
            'tools/esp32c3_tests/production_health.py','tools/esp32c3_tests/ota.py',
            'tools/esp32c3_tests/connection_retry.py','tools/esp32c3_tests/tls_error_codes.py',
            'tools/audio_test_server/server.py','tools/audio_test_server/icy.py'):
    p = destination/'sources'/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(root/rel,p)
shutil.copyfile(__file__,destination/'archive.py')
summary['scope'] = 'HTTP delayed-header and four-lease candidate cancellation controls on the public-root image. Sampled health and settled recovery; not TLS record or acoustic qualification.'
(destination/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(destination/'sha256.json').write_text(json.dumps({p.relative_to(destination).as_posix():sha(p) for p in sorted(destination.rglob('*')) if p.is_file()},indent=2)+'\n')
print(json.dumps(summary,indent=2))
