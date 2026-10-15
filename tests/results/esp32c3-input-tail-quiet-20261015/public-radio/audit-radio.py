"""Replay the exact saved public window; keep every independent verdict."""
import json,statistics,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require,check_recovery_heap
from quiet_acceptance import public_window_checks
from production_health import validate_output,check_health,check_decoder_health
base=Path('.build/c3-input-tail-quiet-20261015/https-radio/public-radio')
r=json.loads((base/'report.json').read_text());health=json.loads((base/'health.json').read_text())
states=json.loads((base/'status.json').read_text())
phases=[json.loads(line) for line in (base/'request-phases.jsonl').read_text().splitlines()]
result=dict(image=r['image'],counts={key:sum(c['result']==key for c in r['cases']) for key in ('PASS','FAIL','BLOCKED')},
    failed_cases=[c for c in r['cases'] if c['result']!='PASS'],failed_request_phases=[p for p in phases if p['result']!='PASS'],public=[])
for name,reference in r.get('references',{}).items():
    batch=next(b for b in states if b['case']=='https:'+name)
    window=r.get('public_checks',{}).get(name)
    entry=dict(name=name,last_seconds=batch['samples'][-1]['seconds'] if batch['samples'] else None)
    if window:
        rows=[h for h in health if window['started_at']+window['warmup_seconds']<=h['at']<=window['ended_at']]
        require(len(rows)==window['health_samples'],'Changed window selection')
        checks=public_window_checks(batch['samples'],rows,reference['spec'],r['public_seconds'])
        require(checks==window['checks'],'Independent replay differs from saved gates')
        entry.update(checks=checks,samples=len(rows),started_at=window['started_at'],ended_at=window['ended_at'],increments=[])
        # Retain output measurements even if an allocation fault rejects the
        # health gate; still reject reboot and malformed/reset counters.
        require(rows and len({h['boot_id'] for h in rows})==1,'Output window rebooted or is absent')
        for a,b in zip(rows,rows[1:]):
            before,after=validate_output(a['output']),validate_output(b['output'])
            require(before['available'] and after['available'],'No output measurement')
            delta={key:(after[key]-before[key])&0xffffffff for key in ('completion_queue_drops','write_errors')}
            if any(delta.values()):entry['increments'].append(dict(from_seconds=a['at']-batch['started_at'],
                to_seconds=b['at']-batch['started_at'],heap=b['heap'],largest=b['largest'],**delta))
        entry['rssi']={key:fn(s['rssi'] for s in batch['samples']) for key,fn in [('minimum',min),('median',statistics.median),('maximum',max)]}
    else:entry['incomplete_window']=True
    result['public'].append(entry)
for name,fn in [('health',lambda:check_health(health)),('decoder',lambda:check_decoder_health(health)),
                ('recovery',lambda:check_recovery_heap(r['idle']['initial'],r['idle']['public']))]:
    try:result[name]=dict(result='PASS',evidence=fn())
    except Exception as error:result[name]=dict(result='FAIL',reason=str(error))
result['idle']={k:{key:statistics.median(s[key] for s in rows) for key in ('heap','largest','tasks')} for k,rows in r['idle'].items()}
result['scope']='Exact saved windows and independent gates. This is live-source sampled evidence, not matched source replay or analog continuity.'
(base/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
