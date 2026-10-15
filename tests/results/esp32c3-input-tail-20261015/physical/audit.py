"""Correlate imposed TLS pauses, output deltas and bounded ISR observations."""
import json,statistics,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require,check_recovery_heap
from production_health import output_window,check_health,check_decoder_health
from pipeline_probe import analyze_pipeline
from local_sustained import check_delivery_pauses,check_tls_delivery
from sustained_output import sustained_window

base=Path('.build/c3-input-tail-20261015/tls-pauses/pauses')
r=json.loads((base/'report.json').read_text())
require(any(c['name']=='all-decoder-health' for c in r['cases']),'Unfinished observation')
h=json.loads((base/'health.json').read_text())
b=next(x for x in json.loads((base/'status.json').read_text()) if x['case']==r['fixture_name'])
rows=[x for x in h if b['started_at']<=x['at']<=b['ended_at']]
_,measured=sustained_window(b['samples'],rows,r['observation_seconds'])
schedule=[(p['after_bytes'],p['seconds']) for p in r['delivery_pause_schedule']]
out=dict(image=r['image'],counts={k:sum(c['result']==k for c in r['cases']) for k in ('PASS','FAIL','BLOCKED')},
    failures=[c for c in r['cases'] if c['result']!='PASS'],
    pipeline=analyze_pipeline(measured),health=check_health(h),decoder=check_decoder_health(h),
    delivery=check_delivery_pauses(r['server_events'],r['fixture_name'],schedule),
    tls=check_tls_delivery(r['server_events'],r['fixture_name']),
    last_seconds=b['samples'][-1]['seconds'],intervals=[],pauses=[],ages_by_phase={})
out['recovery']=check_recovery_heap(r['idle']['initial'],r['idle']['final'])
out['idle']={k:{key:statistics.median(x[key] for x in v) for key in ('heap','largest','tasks')} for k,v in r['idle'].items()}
for before,after in zip(measured,measured[1:]):
    delta=output_window([before,after])
    if delta['completion_queue_drops'] or delta['write_errors']:
        out['intervals'].append(dict(start_at=before['at'],end_at=after['at'],
            from_seconds=before['at']-b['started_at'],to_seconds=after['at']-b['started_at'],
            output=delta,heap=after['heap'],queue=after.get('input_queue')))
for p in out['delivery']['pauses']:
    out['pauses'].append(dict(requested_seconds=p['requested_seconds'],
        start_seconds=p['started_at']-b['started_at'],end_seconds=p['ended_at']-b['started_at'],
        nearby_samples=[dict(seconds=x['at']-b['started_at'],queue=x.get('input_queue'),output=x['output'],heap=x['heap'])
                        for x in measured if p['started_at']-2<=x['at']<=p['ended_at']+2]))
for phase in range(8):
    events=[e for e in out['pipeline']['events'] if e['phases']==phase]
    if events:out['ages_by_phase'][phase]=dict(retained=len(events),
        ranges_ms={key:[min(e['ages_ms'][key] for e in events),max(e['ages_ms'][key] for e in events)]
                   for key in ('output_checkpoint','pcm_packet','encoded_packet','http_read')})
out['scope']='Host pause schedule and sampled pipeline evidence, not analog capture or proof of the previous live-source cause. Occupied slots include WRITING/READY/READING.'
(base/'audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('pipeline','pauses')}))
