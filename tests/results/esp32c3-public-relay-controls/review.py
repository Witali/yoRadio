import json
import sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Failure,sha,check_playback
from production_health import check_health
from sustained_output import sustained_window,check_memory,check_output
ROOT=Path(__file__).resolve().parent
P=ROOT/'physical'
load=lambda name:json.loads((P/name).read_text())
initial=load('initial.json')
assert initial['controller_sha256']==sha((ROOT/'physical.py').read_bytes())
for name,digest in initial['test_sources'].items():assert sha(Path(name).read_bytes())==digest,name
reference=load('reference.json')
rows=load('health.json')
batches={b['case']:b for b in load('status.json')}
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
details={}
for name,result in load('results.json').items():
    batch=batches[name]
    selected=[h for h in rows if batch['started_at']<=h['at']<=batch['ended_at']]
    steady,health=sustained_window(batch['samples'],selected,90)
    checks=dict(format=evaluate(lambda:check_playback(batch['samples'],reference['spec'],minimum=45,warmup=15)),
                output=evaluate(lambda:check_output(health)),memory=evaluate(lambda:check_memory(health)))
    assert all(checks[k]==result[k] for k in checks)
    assert result['first_stopped']==next((s for s in steady if not s['audio']),None)
    details[name]=dict(checks=checks,first_stopped=result['first_stopped'],health=check_health(health))
assert len(details)==2
events=load('relay-events.json')
assert len(events)==1 and events[0]['ended']
event=events[0]
assert event['upstream_status']==200 and event['icy_requested']
assert event['received']>=event['sent']>0
assert sum(w['bytes'] for w in event['delivery']['windows'])==event['sent']
if event['received']==event['sent']:assert event['received_sha256']==event['sent_sha256']
restored=load('restoration.json')
assert restored['identity']==initial['identity'] and restored['same_station']
assert all(restored['persistence'].values())
assert all(s['audio']==initial['status']['audio'] for s in restored['states'])
assert restored['health']==check_health(rows)
(ROOT/'review.json').write_text(json.dumps(dict(review='PASS',restoration=True,cases=details,
    relay={k:v for k,v in event.items() if k!='delivery'}),indent=2)+'\n')
print('Evidence replay PASS:',{n:{k:v['result'] for k,v in d['checks'].items()} for n,d in details.items()})
