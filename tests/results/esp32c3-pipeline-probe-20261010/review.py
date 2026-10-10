"""Replay quiet TLS renegotiation gates and verify exact application restoration."""
import json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from common import Failure,check_recovery_heap,matches,require
from production_health import check_health,output_window
from quiet_tls_records import check_record_window,check_format,check_response,check_renegotiation
from sustained_output import sustained_window,check_output,check_memory
phase=sys.argv[1] if len(sys.argv)>1 else 'physical-walltime'
assert phase in ('physical-walltime','physical-comparison')
P=ROOT/phase
review_name='review.json' if phase=='physical-walltime' else 'comparison-review.json'
r=json.loads((P/'records/report.json').read_text())
health=json.loads((P/'records/health.json').read_text())
batches=json.loads((P/'records/status.json').read_text())
specs=json.loads((ROOT/'fixture-inputs.json').read_text())
cases={c['name']:c for c in r['cases']}
assert len(cases)==len(r['cases'])
results={}
checked=set()
def replay(name,fn):
    try:
        value=fn();verdict='PASS'
    except Failure as error:
        value=None;verdict='FAIL'
        assert cases[name]['reason']==str(error),(name,cases[name],str(error))
    assert cases[name]['result']==verdict,name
    if verdict=='PASS':assert cases[name]['evidence']==json.loads(json.dumps(value)),name
    checked.add(name)
    return value

for batch in batches:
    key=batch['case']
    if key.startswith('idle:'):continue
    name,mode=key.split(':')
    spec=specs[name]
    assert spec['sha256']==r['fixture_hashes'][name]
    assert 'interrupted' not in batch,batch.get('exception_chain')
    states=batch['samples']
    start,end=batch['started_at'],batch['ended_at']
    rows=[h for h in health if start<=h['at']<=end]
    steady,measured=sustained_window(states,rows,r['seconds'])
    window=dict(output=output_window(measured),health=check_health(measured),
                maximum_status_health_ms=max(s['request_ms'] for s in states))
    assert window==r['windows'][key],key
    fmt=replay(key+':format',lambda:check_format(states,spec,r['seconds']))
    first=next((start+s['seconds'] for s in states if matches(s,spec)),float('inf'))
    observation=r['record_observations'][key]
    records=replay(key+':records',lambda:check_record_window(observation,mode,spec,first,observation['captured_at']))
    renegotiation=replay(key+':renegotiation',lambda:check_renegotiation(observation,first,observation['captured_at'],r['renegotiate_seconds']))
    replay(key+':output',lambda:check_output(measured))
    replay(key+':memory',lambda:check_memory(measured))
    replay(key+':response',lambda:check_response(states))
    replay(key+':collection',lambda:dict(samples=len(states),sustained_samples=len(steady)))
    final=r['idle'][key]
    replay(key+':recovery',lambda:check_recovery_heap(r['idle']['initial'],final))
    results[key]=dict(**window,format=fmt,records=records,renegotiation=renegotiation,
        rssi_range=[min(s['rssi'] for s in states),max(s['rssi'] for s in states)])
assert set(results)=={n+':'+m for n in r['names'] for m in r['modes']}
assert len(r['server_events_after_stop']['events'])==len(results)
faults=replay('lifetime-health',lambda:check_health(health))
assert cases['stop-and-settings']['result']=='PASS'
assert all(cases['stop-and-settings']['evidence'].values())
checked.add('stop-and-settings')
assert checked==set(cases)
assert json.loads((P/'phase.json').read_text())['code']==(0 if all(c['result']=='PASS' for c in cases.values()) else 1)
restore=json.loads((P/'restoration.json').read_text())
assert restore['identity']['app_elf_sha256']=='76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b'
assert all(restore['persistence'].values())
assert len(restore['states'])==3 and all(not s['audio'] for s in restore['states'])
result=dict(replay='PASS',counts=dict(passed=sum(c['result']=='PASS' for c in cases.values()),total=len(cases)),
    failed_cases=[n for n,c in cases.items() if c['result']!='PASS'],windows=results,
    lifetime_health=faults,exact_listened_image_restored=True,
    idle_medians={n:{k:statistics.median(h[k] for h in rows) for k in ('heap','largest','tasks')}
                  for n,rows in r['idle'].items()})
encoded=json.dumps(result,indent=2)+'\n'
if (ROOT/review_name).exists():assert (ROOT/review_name).read_text()==encoded
else:(ROOT/review_name).write_text(encoded)
print(json.dumps({k:v for k,v in result.items() if k not in ('windows','idle_medians')}))
for name,window in results.items():
    print(name,json.dumps(window))
