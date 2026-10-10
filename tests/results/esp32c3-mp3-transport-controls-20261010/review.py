"""Replay transport-control observations, retaining the first harness failure."""
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

P = ROOT / 'physical-v2'
initial = json.loads((P / 'initial.json').read_text())
assert hashlib.sha256((ROOT / 'physical-v2.py').read_bytes()).hexdigest() == initial['controller_sha256']
for name, digest in initial['test_sources_sha256'].items():
    assert hashlib.sha256((ROOT / 'test-sources' / name).read_bytes()).hexdigest() == digest
manifest = json.loads((ROOT / 'fixtures/manifest.json').read_text())
for entry in manifest['fixtures']:
    assert hashlib.sha256((ROOT / 'fixtures' / entry['file']).read_bytes()).hexdigest() == entry['sha256']
saved = json.loads((P / 'results.json').read_text())
assert set(saved) == {'local44100','local48000','public-http','public-https'}
batches = json.loads((P / 'status.json').read_text())
health = json.loads((P / 'health.json').read_text())

def evaluate(fn):
    try: return dict(result='PASS', evidence=fn())
    except Failure as error: return dict(result='FAIL', reason=str(error))

details = {}
for name, original in saved.items():
    batch, = [b for b in batches if b['case'] == name]
    states = batch['samples']
    rows = [h for h in health if batch['started_at'] <= h['at'] <= batch['ended_at']]
    steady, measured = sustained_window(states, rows, 90)
    replay = dict(format=evaluate(lambda:check_playback(states,original['reference']['spec'],minimum=45,warmup=15)),
                  output=evaluate(lambda:check_output(measured)), memory=evaluate(lambda:check_memory(measured)))
    assert replay == original['checks']
    assert analyze_pipeline(measured) == original['pipeline']
    assert check_health(measured) == original['health']
    assert rows[0]['pipeline']['stream_failure'] == original['failure_before']
    assert rows[-1]['pipeline']['stream_failure'] == original['failure_after']
    first = next((s for s in states if s['audio']), None)
    stopped = next((s for s in states if first and s['seconds'] > first['seconds'] and not s['audio']), None)
    active = [h for s,h in zip(steady,measured) if s['audio'] and (not stopped or s['seconds'] < stopped['seconds'])]
    host_info = None
    if name.startswith('public-'):
        host = json.loads((P / (name+'-host.json')).read_text())
        progress = dict(line.split('=',1) for line in (P / (name+'-host-progress.log')).read_text().splitlines() if '=' in line)
        host_info = dict(completed=host['exit_code']==0 and not host.get('timed_out') and progress.get('progress')=='end' and int(progress.get('out_time_us','0'))>=94_000_000,
            progress=progress, exit_code=host['exit_code'], error_bytes=(P / (name+'-host-errors.log')).stat().st_size)
    details[name] = dict(checks=replay, sampled_health=original['health'],
        first_stopped=stopped, active_pipeline=analyze_pipeline(active) if len(active)>=2 else None,
        new_failures=(original['failure_after']['sequence']-original['failure_before']['sequence'])&0xffffffff,
        last_failure=original['failure_after'], host=host_info)
summary = json.loads((P / 'summary.json').read_text())
assert check_health(health) == summary['health'] and all(summary['persistence'].values())
for folder in (ROOT/'physical', P):
    restoration = json.loads((folder/'restoration.json').read_text())
    assert restoration['identity']['app_elf_sha256'] == initial['quiet']['app_elf_sha256']
    assert all(restoration['persistence'].values()) and len(restoration['states']) == 3
    assert all(not s['audio'] for s in restoration['states'])
assert (ROOT/'physical/controller-failure.json').exists()
result = dict(review='PASS', cases=details, health=summary['health'], recovery=summary['recovery'],
              original_harness_failure_preserved=True, exact_listened_image_restored=True)
encoded=json.dumps(result,indent=2)+'\n';target=ROOT/'review.json'
if target.exists(): assert target.read_text()==encoded
else: target.write_text(encoded)
for name,d in details.items():
    print(name,{k:v['result'] for k,v in d['checks'].items()},'new_failures',d['new_failures'],
          'host_complete',d['host']['completed'] if d['host'] else None)
print('Evidence replay and both restorations: PASS')
