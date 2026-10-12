import json,statistics,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Failure,sha,check_playback
from production_health import check_health
from sustained_output import sustained_window,check_memory,check_output
ROOT=Path(__file__).resolve().parent
P=ROOT/'physical-observed'
load=lambda name:json.loads((P/name).read_text())
initial=load('initial.json')
assert initial['controller_sha256']==sha((ROOT/'physical_observed.py').read_bytes())
for name,digest in initial['test_sources'].items():
    assert sha(Path(name).read_bytes())==digest,name
    assert sha((ROOT/'test-sources'/name).read_bytes())==digest,name
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
details={}
for name,result in load('results.json').items():
    variant=result['variant']
    batches={b['case']:b for b in load(variant+'/status.json')}
    batch=batches[name]
    rows=load(variant+'/health.json')
    selected=[h for h in rows if batch['started_at']<=h['at']<=batch['ended_at']]
    steady,health=sustained_window(batch['samples'],selected,60)
    checks=dict(transport=dict(result='FAIL' if batch['errors'] else 'PASS',errors=batch['errors']),
        format=evaluate(lambda:check_playback(batch['samples'],result['spec'],minimum=27,warmup=15)),
        output=evaluate(lambda:check_output(health)),memory=evaluate(lambda:check_memory(health)))
    assert all(checks[k]==result[k] for k in checks),name
    metrics={k:dict(minimum=min(r[k] for r in health),median=statistics.median(r[k] for r in health),
        first=statistics.median(r[k] for r in health[:3]),last=statistics.median(r[k] for r in health[-3:])) for k in ('heap','largest')}
    details[name]=dict(checks=checks,metrics=metrics,health=check_health(health),
        maximum_response_ms=max(s['request_ms'] for s in batch['samples']))
assert len(details)==4
restored=load('restoration.json')
assert restored['identity']['app_elf_sha256']==initial['baseline']['app_elf_sha256']
assert restored['same_station'] and all(restored['persistence'].values())
assert all(s['audio']==initial['original']['audio'] for s in restored['states'][-3:])
assert all(s['sample_rate']>0 and s['channels']>0 for s in restored['states'][-3:])
first=json.loads((ROOT/'physical/baseline/status.json').read_text())[-1]
assert first['interrupted']=='URLError'
first_restore=json.loads((ROOT/'physical/restoration.json').read_text())
assert first_restore['same_station'] and all(first_restore['persistence'].values())
review=dict(review='PASS',restoration=True,cases=details,first_attempt=dict(result='INCOMPLETE',
    case=first['case'],exception_chain=first['exception_chain'],elapsed_seconds=first['elapsed_seconds'],
    candidate_installed=False,restoration=True))
repeat=json.loads((ROOT/'physical-repeat/restoration.json').read_text())
assert repeat['same_station'] and all(repeat['persistence'].values())
review['second_attempt']=dict(result='INCOMPLETE',phase='stop before local HE-AAC',
    exception='URLError caused by TimeoutError (terminal output)',candidate_installed=False,restoration=True)
trace=[json.loads(line) for line in (P/'request-phases.jsonl').read_text().splitlines()]
review['transport']=dict(connects=sum(r['phase']=='connect' for r in trace),
    failed_phases=[r for r in trace if r['result']=='FAIL'])
control=ROOT/'physical-cold-control'
control_initial=json.loads((control/'initial.json').read_text())
assert control_initial['controller_sha256']==sha((ROOT/'physical_cold_control.py').read_bytes())
for name,digest in control_initial['test_sources'].items():assert sha(Path(name).read_bytes())==digest,name
control_rows=json.loads((control/'baseline/health.json').read_text())
control_batches={b['case']:b for b in json.loads((control/'baseline/status.json').read_text())}
control_details={}
for name,result in json.loads((control/'results.json').read_text()).items():
    batch=control_batches[name]
    selected=[h for h in control_rows if batch['started_at']<=h['at']<=batch['ended_at']]
    steady,health=sustained_window(batch['samples'],selected,60)
    checks=dict(transport=dict(result='FAIL' if batch['errors'] else 'PASS',errors=batch['errors']),
        format=evaluate(lambda:check_playback(batch['samples'],result['spec'],minimum=27,warmup=15)),
        output=evaluate(lambda:check_output(health)),memory=evaluate(lambda:check_memory(health)))
    assert all(checks[k]==result[k] for k in checks),name
    control_details[name]=dict(checks=checks,health=check_health(health),
        metrics={k:dict(minimum=min(r[k] for r in health),median=statistics.median(r[k] for r in health),
        first=statistics.median(r[k] for r in health[:3]),last=statistics.median(r[k] for r in health[-3:])) for k in ('heap','largest')})
assert len(control_details)==2
control_restore=json.loads((control/'restoration.json').read_text())
assert control_restore['same_station'] and all(control_restore['persistence'].values())
assert control_restore['identity']['app_elf_sha256']==initial['baseline']['app_elf_sha256']
assert all(s['audio']==control_initial['original']['audio'] and s['sample_rate']>0 for s in control_restore['states'][-3:])
review['rebooted_baseline_control']=dict(cases=control_details,restoration=True)
for name,digest in json.loads((ROOT/'source-hashes.json').read_text()).items():
    assert sha((ROOT/'build-sources'/name).read_bytes())==digest,name
(ROOT/'review.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps(review,indent=2))
