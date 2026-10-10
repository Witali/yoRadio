"""Replay diagnostic findings without treating diagnostics as production acceptance."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'test-sources/tools/esp32c3_tests'))
from common import Failure, check_playback, require
from production_health import check_health
from sustained_output import sustained_window, check_output, check_memory
from pipeline_probe import analyze_pipeline

P = ROOT / 'physical'
initial = json.loads((P / 'initial.json').read_text())
for path, digest in initial['test_sources_sha256'].items():
    assert hashlib.sha256((ROOT / 'test-sources' / path).read_bytes()).hexdigest() == digest
assert hashlib.sha256((ROOT / 'physical.py').read_bytes()).hexdigest() == initial['controller_sha256']
saved = json.loads((P / 'results.json').read_text())
batches = json.loads((P / 'status.json').read_text())
health = json.loads((P / 'health.json').read_text())
assert set(saved) == {'mp3-first', 'he64', 'mp3-repeat'}

def evaluate(fn):
    try: return dict(result='PASS', evidence=fn())
    except Failure as error: return dict(result='FAIL', reason=str(error))

details = {}
for name, result in saved.items():
    batch, = [b for b in batches if b['case'] == name]
    states = batch['samples']
    rows = [h for h in health if batch['started_at'] <= h['at'] <= batch['ended_at']]
    steady, measured = sustained_window(states, rows, 120)
    replay = dict(format=evaluate(lambda: check_playback(states, result['reference']['spec'], minimum=63, warmup=15)),
                  output=evaluate(lambda: check_output(measured)), memory=evaluate(lambda: check_memory(measured)))
    assert replay == result['checks']
    assert analyze_pipeline(measured) == result['pipeline']
    assert check_health(measured) == result['health']
    assert rows[-1]['pipeline']['stream_failure'] == result['last_failure']
    first_play = next((s for s in states if s['audio']), None)
    stopped = next((s for s in states if first_play and s['seconds'] > first_play['seconds'] and not s['audio']), None)
    # Restrict continuity interpretation to observations while status is playing.
    # Keep the whole-window result above as originally recorded, including idle.
    active = [(s,h) for s,h in zip(steady,measured) if s['audio'] and (not stopped or s['seconds'] < stopped['seconds'])]
    active_probe = analyze_pipeline([h for s,h in active]) if len(active) >= 2 else None
    host = json.loads((P / (name + '-host.json')).read_text())
    progress = dict(line.split('=',1) for line in (P / (name + '-host-progress.log')).read_text().splitlines() if '=' in line)
    host_ok = host['exit_code'] == 0 and not host.get('timed_out') and progress.get('progress') == 'end' and int(progress.get('out_time_us','0')) >= 124_000_000
    details[name] = dict(checks=replay, first_playing=first_play, first_stopped=stopped,
        failure_delta=(result['last_failure']['sequence'] - rows[0]['pipeline']['stream_failure']['sequence']) & 0xffffffff,
        last_failure=result['last_failure'], active_pipeline=active_probe,
        host_decode_completed=host_ok, host_progress=progress,
        host_error_bytes=(P / (name + '-host-errors.log')).stat().st_size,
        sampled_health=result['health'])
restored = json.loads((P / 'restoration.json').read_text())
assert restored['identity']['app_elf_sha256'] == initial['quiet']['app_elf_sha256']
assert all(restored['persistence'].values()) and len(restored['states']) == 3
assert all(not s['audio'] for s in restored['states'])
summary = json.loads((P / 'summary.json').read_text())
assert check_health(health) == summary['health'] and all(summary['persistence'].values())
result = dict(review='PASS', cases=details, health=summary['health'], recovery=summary['recovery'],
              exact_listened_image_restored=True, scope='Diagnostic image; host connection is independent, not a packet/PCM capture of the board connection')
encoded = json.dumps(result, indent=2) + '\n'
target = ROOT / 'review.json'
if target.exists(): assert target.read_text() == encoded
else: target.write_text(encoded)
for name, d in details.items():
    a=d['active_pipeline']
    print(name, 'new_failures',d['failure_delta'],'TLS',d['last_failure']['tls_code'],
          'active_drops',a['output']['completion_queue_drops'] if a else None,
          'host_complete',d['host_decode_completed'])
print('Evidence replay and exact restoration: PASS')
