"""Replay public-file evidence and preserve failed TCP-connect brackets."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require,check_recovery_heap
from public_file_acceptance import check_finite_playback,check_finite_health
from production_health import check_health,check_decoder_health,output_window
base=Path('.build/c3-input-tail-quiet-20261015/https-files/public-files')
r=json.loads((base/'report.json').read_text())
states=json.loads((base/'status.json').read_text())
health=json.loads((base/'health.json').read_text())
phases=[json.loads(s) for s in (base/'request-phases.jsonl').read_text().splitlines()]
require(any(c['name']=='all-decoder-health' for c in r['cases']),'Campaign incomplete')
out=dict(image=r['image'],counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
         failures=[c for c in r['cases'] if c['result']!='PASS'],file_replay=[],recovery_replay=[],failed_connects=[],
         scope='Retained failed cases are not overwritten by diagnostic counter brackets or later passes.')
for check,name in ((check_health,'health'),(check_decoder_health,'decoder_health')):
    try:out[name]=dict(result='PASS',**check(health))
    except Exception as e:out[name]=dict(result='FAIL',reason=str(e))
for action in r['actions']:
    name=action['name']
    if not name.startswith('https:'):continue
    codec,hint=name.split(':')[1:]
    row=dict(name=name,result='FAIL')
    try:
        batches=[s for s in states if s['case']==name]
        require(len(batches)==1,'Missing unique observation')
        batch=batches[0]
        played=check_finite_playback(batch['samples'],r['references']['sources'][codec]['spec'])
        steady=[h for h in health if batch['started_at']+played['first_playback_seconds']+3<=h['at']<=
                batch['started_at']+played['first_stopped_seconds']-1]
        row.update(playback=played,**check_finite_health(steady),result='PASS')
    except Exception as e:row['reason']=str(e)
    out['file_replay'].append(row)
for name,rows in r['idle'].items():
    if name=='initial':continue
    row=dict(name=name,result='FAIL')
    try:check_recovery_heap(r['idle']['initial'],rows);row['result']='PASS'
    except Exception as e:row['reason']=str(e)
    out['recovery_replay'].append(row)
for phase in phases:
    if phase['phase']!='connect' or phase['result']=='PASS':continue
    end=phase['at']+phase['ms']/1000
    row=dict(request=phase['request'],at=phase['at'],milliseconds=phase['ms'],socket_attempts=phase.get('socket_attempts',[]))
    preceding=[h for h in health if h['at']<phase['at']]
    snapshots=[(name,s) for name,s in r.get('failure_snapshots',{}).items() if s['started_at']>=end and s['started_at']-end<1]
    if preceding and len(snapshots)==1:
        name,snapshot=snapshots[0]
        row.update(case=name,snapshot=snapshot,health_before=preceding[-1])
        try:row['sampled_output_bracket']=output_window([preceding[-1],snapshot['health'][0]])
        except Exception as e:row['bracket_error']=str(e)
    else:row['bracket_unavailable']=True
    out['failed_connects'].append(row)
(base/'audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('file_replay','recovery_replay','failed_connects')}))
