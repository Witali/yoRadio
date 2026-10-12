"""Replay public MP3 observations without turning repeats into fixes."""
import json,statistics,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Failure,sha,check_playback,check_recovery_heap
from ota import image_info
from production_health import check_health
from sustained_output import sustained_window,check_output,check_memory
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'physical'
load=lambda name:json.loads((OUT/name).read_text())
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
initial=load('initial.json')
assert initial['controller_sha256']==sha((ROOT/'physical.py').read_bytes())
for name,digest in initial['test_sources'].items():
    assert sha(Path(name).read_bytes())==digest,name
    assert sha((ROOT/'test-sources'/name).read_bytes())==digest,name
assert image_info(Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease/app.bin').read_bytes())==initial['candidate']
results=load('results.json');review={}
for transport in ('http','https'):
    batch=next(b for b in load('status.json') if b['case']=='mp3:'+transport)
    states=batch['samples'];rows=[h for h in load('health.json') if batch['started_at']<=h['at']<=batch['ended_at']]
    assert len(states)==len(rows),'Unpaired observations'
    steady=[h for s,h in zip(states,rows) if s['seconds']>=15]
    collected=evaluate(lambda:sustained_window(states,rows,600))
    spec=load(transport+'-reference.json')['spec']
    checks=dict(collection=dict(result=collected['result'],reason=collected.get('reason')),
        transport=dict(result='FAIL' if batch['errors'] else 'PASS',errors=batch['errors']),
        format=evaluate(lambda:check_playback(states,spec,minimum=351,warmup=15)),
        output=evaluate(lambda:check_output(steady)),memory=evaluate(lambda:check_memory(steady)))
    assert all(results[transport][key]==value for key,value in checks.items()),transport
    assert results[transport]['health']==check_health(rows)
    host=load(transport+'-host.json');progress={}
    for line in (OUT/(transport+'-ffmpeg-progress.log')).read_text().splitlines():
        if '=' in line:
            key,value=line.split('=',1);progress[key]=value
    assert host['decoded_seconds']==float(progress.get('out_time_us','0'))/1e6
    passed=host['completed'] and host['returncode']==0 and host['decoded_seconds']>=604 and host['error_bytes']==0
    assert host['result']==('PASS' if passed else 'FAIL')
    metrics={k:dict(minimum=min(r[k] for r in steady),median=statistics.median(r[k] for r in steady),first=statistics.median(r[k] for r in steady[:3]),last=statistics.median(r[k] for r in steady[-3:])) for k in ('heap','largest')}
    review[transport]=dict(checks=checks,health=check_health(rows),metrics=metrics,host=host,
        seconds_observed=states[-1]['seconds'],samples=len(states),steady_samples=len(steady),
        maximum_status_health_ms=max(s['request_ms'] for s in states),
        lifetime_heap_low_water=min(h['minimum_heap'] for h in rows),first_stopped=results[transport]['first_stopped'])
recovery=load('recovery.json')
assert recovery['check']==evaluate(lambda:check_recovery_heap(recovery['initial'],recovery['final']))
restored=load('restoration.json')
assert restored['same_station'] and all(restored['persistence'].values())
assert restored['identity']['app_elf_sha256']==initial['baseline']['app_elf_sha256']
assert all(s['audio']==initial['original']['audio'] for s in restored['states'][-3:])
assert not initial['original']['audio'] or all(s['pcm_sample_rate']>0 for s in restored['states'][-3:])
result=dict(review='PASS',scope='Evidence consistency; case failures remain failures',cases=review,recovery=recovery['check'],restoration=True)
(ROOT/'review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
