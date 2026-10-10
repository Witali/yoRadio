"""Replay saved local playback/heap gates and verify source/restore identities.

WebSocket message comparisons, OTA HTTP exchanges and private settings equality
remain recorded live assertions, explicitly distinguished from raw replay.
"""
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'test-sources/tools/esp32c3_tests'))
from common import Failure, check_playback, check_recovery_heap, check_transitions, matches, require
from production_health import check_health
from audio_test_server.fixtures import SEQUENCES

P = ROOT / 'physical'
initial = json.loads((P / 'initial.json').read_text())
phases = json.loads((P / 'phases.json').read_text())
report = json.loads((P / 'local/report.json').read_text())
health = json.loads((P / 'local/health.json').read_text())
batches = json.loads((P / 'local/status.json').read_text())
specs = json.loads((ROOT / 'fixture-specs.json').read_text())
cases = {c['name']: c for c in report['cases']}
actions = {a['name']: a for a in report['actions']}
assert len(cases) == len(report['cases']) == 42
assert report['board']['app_elf_sha256'] == initial['candidate']['app_elf_sha256']
assert report['test_sources_sha256'] == initial['test_sources_sha256']
assert hashlib.sha256((ROOT / 'physical.py').read_bytes()).hexdigest() == initial['controller_sha256']
for name, digest in initial['test_sources_sha256'].items():
    assert hashlib.sha256((ROOT / 'test-sources' / name).read_bytes()).hexdigest() == digest, name
for name, spec in specs.items():
    assert spec['sha256'] == report['fixture_hashes'][name], name

replayed, recorded_only = [], []
def batch(name, action_name):
    action = actions[action_name]
    selected = [b for b in batches if b['case'] == name and
                action['started_at'] <= b['started_at'] <= b['ended_at'] <= action['ended_at']]
    require(len(selected) == 1, 'Missing or ambiguous playback batch: ' + name)
    require('interrupted' not in selected[0], 'Interrupted observation: ' + name)
    return selected[0]['samples']

def replay(name, fn):
    try:
        evidence = fn()
        verdict = 'PASS'
    except Failure as error:
        verdict = 'FAIL'
        assert cases[name]['reason'] == str(error), (name, cases[name], str(error))
    assert cases[name]['result'] == verdict, name
    if verdict == 'PASS':
        assert cases[name]['evidence'] == json.loads(json.dumps(evidence)), name
    replayed.append(name)

def file_case(name, fixture):
    evidence = check_playback(batch(fixture, name), specs[fixture])
    require(any(not s['audio'] for s in batch(fixture + ':eof', name)), 'Finite stream never reached EOF')
    return dict(**evidence, serial_capture_enabled=False)

def transition(name, fixture):
    sequence = SEQUENCES[fixture]
    check_transitions(batch(fixture, name), [specs[n] for n in sequence])
    return dict(sequence=sequence)

def fault(name, mode):
    require(any(not r['audio'] for r in batch('fault:' + mode, name)[-3:]), 'Fault did not leave playback')
    check_playback(batch('recovered:' + mode, name), specs['lc-22050-mono'])
    return dict(recovered=True)

for name in cases:
    if name == 'initial-idle':
        replay(name, lambda: dict(samples=report['idle']['initial']))
    elif name.startswith('http:'):
        replay(name, lambda n=name: file_case(n, n.split(':')[1]))
    elif name.startswith('idle:'):
        replay(name, lambda n=name: dict(samples=report['idle'][n.split(':')[1]]))
    elif name.startswith('recovery:'):
        def recover(n=name):
            check_recovery_heap(report['idle']['initial'], report['idle'][n.split(':')[1]])
            return dict(compared_with='initial', free_loss_tolerance=2048, largest_loss_tolerance=4096)
        replay(name, recover)
    elif name.startswith('transition:'):
        replay(name, lambda n=name: transition(n, n.split(':')[1]))
    elif name == 'stop-play-generation':
        def stop_play():
            check_playback(batch(name, name), specs['lc-22050-mono'])
            return dict(stale_generation_rejected=True)
        replay(name, stop_play)
    elif name.startswith('network:'):
        mode = name.split(':')[1]
        replay(name, lambda n=name, m=mode: file_case(n, 'lc-48000-stereo')
               if m in ('redirect', 'jitter') else fault(n, m))
    elif name == 'lifetime-health':
        replay(name, lambda: check_health(health))
    elif name == 'websocket-format-and-reconnect':
        check_playback(batch('ws-warmup', name), specs['lc-48000-stereo'])
        recorded_only.append(name)
    elif name == 'stop-and-settings':
        recorded_only.append(name)
    else:
        raise AssertionError('Unreviewed gate: ' + name)
assert set(replayed + recorded_only) == set(cases)
restore = json.loads((P / 'restoration.json').read_text())
assert restore['identity']['app_elf_sha256'] == initial['quiet']['app_elf_sha256']
assert all(restore['persistence'].values())
assert len(restore['states']) == 3 and all(not s['audio'] for s in restore['states'])
phase_results = {}
for phase in phases:
    label = phase['name']
    current = report if label == 'local' else json.loads((P / 'ota.json').read_text())
    assert current['board']['app_elf_sha256'] == initial['candidate']['app_elf_sha256']
    assert current['test_sources_sha256'] == initial['test_sources_sha256']
    if label == 'ota':
        expected = {'ota:' + name for name in ('wrong-chip', 'wrong-project', 'corrupt-image',
                    'truncated-image', 'extra-byte', 'missing-boundary', 'spiffs-target',
                    'oversized-request', 'disconnect', 'stall', 'roundtrip:1', 'roundtrip:2',
                    'while-playing', 'slow')} | {'restore-saved-station'}
        assert len(current['cases']) == 15 and {c['name'] for c in current['cases']} == expected
        playing = next(c for c in current['cases'] if c['name'] == 'ota:while-playing')
        if playing['result'] == 'PASS':
            assert matches(playing['evidence']['playback_before'], specs['he-44100-stereo'])
            events = json.loads((P / 'ota-server-events.json').read_text())
            assert any(e['mode'] == 'stream' and e['fixture'] == 'he-44100-stereo' and
                       e['pacing_ratio'] == 1.0 and e['sent'] > 0 for e in events)
    passed = sum(c['result'] == 'PASS' for c in current['cases'])
    assert phase['code'] == (0 if passed == len(current['cases']) else 1)
    phase_results[label] = dict(passed=passed, total=len(current['cases']),
        failures=[c['name'] for c in current['cases'] if c['result'] != 'PASS'])
result = dict(replay='PASS', phases=phase_results, replayed_local_gates=replayed,
              recorded_only_local_gates=recorded_only,
              ota_scope='Live HTTP rejection/acceptance, image/partition and settings checks; exchanges are not replayed',
              health=check_health(health), sdk_lifetime_minimum_heap=min(h['minimum_heap'] for h in health),
              idle_medians={n:{k:statistics.median(h[k] for h in rows) for k in ('heap','largest','tasks')}
                            for n,rows in report['idle'].items()},
              exact_listened_image_restored=True)
encoded = json.dumps(result, indent=2) + '\n'
target = ROOT / 'review.json'
if target.exists():
    assert target.read_text() == encoded
else:
    target.write_text(encoded)
print(json.dumps({k:v for k,v in result.items() if k not in ('replayed_local_gates', 'idle_medians')}))
