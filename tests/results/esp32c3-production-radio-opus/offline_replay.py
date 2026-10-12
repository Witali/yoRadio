import json,statistics,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'test-sources/tools/esp32c3_tests'))
from common import Failure,sha,check_playback,check_recovery_heap,fixtures
from production_health import check_health
from sustained_output import sustained_window,check_output,check_memory
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'physical'
load=lambda name:json.loads((OUT/name).read_text(encoding='utf-8'))
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
initial=load('initial.json');results=load('results.json');batches=load('status.json');health=load('health.json')
assert initial['controller_sha256']==sha((ROOT/'physical.py').read_bytes())
for name,digest in initial['test_sources'].items():
    assert sha((ROOT/'test-sources'/name).read_bytes())==digest,name
spec=json.loads((ROOT/'fixtures/manifest.json').read_text())['fixtures'][0]
spec['label']='OGG'
reference=json.loads((ROOT/'fixture-reference.json').read_text());assert reference['result']=='PASS' and reference['fixture_sha256']==spec['sha256']
recovery=load('recovery.json');summaries={}
for cycle in range(3):
    name='opus:auto:'+str(cycle+1);batch=next(b for b in batches if b['case']==name)
    rows=[h for h in health if batch['started_at']<=h['at']<=batch['ended_at']];states=batch['samples'];assert len(states)==len(rows)
    steady=[h for s,h in zip(states,rows) if s['seconds']>=15]
    collected=evaluate(lambda:sustained_window(states,rows,60))
    checks=dict(collection=dict(result=collected['result'],reason=collected.get('reason')),
        transport=dict(result='FAIL' if batch['errors'] else 'PASS',errors=batch['errors']),
        format=evaluate(lambda:check_playback(states,spec,minimum=27,warmup=15)),output=evaluate(lambda:check_output(steady)),memory=evaluate(lambda:check_memory(steady)))
    assert all(results[name][k]==v for k,v in checks.items())
    assert results[name]['health']==check_health(rows)
    assert results[name]['recovery']==evaluate(lambda:check_recovery_heap(recovery['initial'],results[name]['idle_health']))
    summaries[name]=dict(checks=checks,recovery=results[name]['recovery'],health=check_health(rows),metrics={k:dict(minimum=min(h[k] for h in steady),first=statistics.median(h[k] for h in steady[:3]),last=statistics.median(h[k] for h in steady[-3:])) for k in ('heap','largest')})
    if cycle==2:
        tail=next(b for b in batches if b['case']==name+':terminal')['samples'];terminal=results[name]['terminal']
        if terminal['result']=='PASS':
            stopped=next(i for i,s in enumerate(tail) if not s['audio'])
            assert len(tail)-stopped==terminal['evidence']['samples']>=2
            assert all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate'] and not s['pcm_channels'] for s in tail[stopped:])
        summaries[name]['terminal']=terminal
restored=load('restoration.json');assert restored['identity']['app_elf_sha256']==initial['baseline']['app_elf_sha256']
assert restored['same_station'] and all(restored['persistence'].values())
assert all(s['audio']==initial['original']['audio'] for s in restored['states'][-3:])
assert not initial['original']['audio'] or all(s['pcm_sample_rate']>0 for s in restored['states'][-3:])
assert recovery['check']==evaluate(lambda:check_recovery_heap(recovery['initial'],recovery['final']))
review=dict(review='PASS',scope='Replay consistency; failures remain failures',cycles=summaries,recovery=recovery['check'],restoration=True)
assert review==json.loads((ROOT/'review.json').read_text()),'Offline replay differs'
(ROOT/'offline-review.json').write_text(json.dumps(review,indent=2)+'\n');print('Offline replay matches original review')
