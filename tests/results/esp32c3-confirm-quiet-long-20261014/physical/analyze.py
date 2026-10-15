import json, statistics, sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from production_health import check_health,check_decoder_health,output_window
from sustained_output import check_memory,check_output
from common import check_playback,matches,require

base=Path('.build/c3-confirm-quiet-long-20261014/https-radio/public-radio')
r=json.loads((base/'report.json').read_text());h=json.loads((base/'health.json').read_text())
b=next(b for b in json.loads((base/'status.json').read_text()) if b['case'].startswith('https:'))
rows=[x for x in h if b['started_at']+15<=x['at']<=b['ended_at']]
spec=r['references']['groovesalad-128-aac']['spec']
out=dict(image=r['image'],samples=len(rows),last_seconds=b['samples'][-1]['seconds'],
         output=output_window(rows),checks={},minutes=[])
for name,fn in [('health',lambda:check_health(rows)),('decoder',lambda:check_decoder_health(rows)),
                ('memory',lambda:check_memory(rows)),('output',lambda:check_output(rows)),
                ('format',lambda:check_playback(b['samples'],spec,minimum=int(585*.6),warmup=15))]:
    try:out['checks'][name]=dict(result='PASS',evidence=fn())
    except Exception as error:out['checks'][name]=dict(result='FAIL',reason=str(error))
out['first_decoded_format_seconds']=next(s['seconds'] for s in b['samples'] if matches(s,spec))
out['maximum_status_health_ms']=max(s['request_ms'] for s in b['samples'])
out['heap_endpoint_medians']={key:[statistics.median(x[key] for x in rows[:3]),
    statistics.median(x[key] for x in rows[-3:])] for key in ('heap','largest')}
for minute in range(10):
    window=[x for x in rows if minute*60<=x['at']-b['started_at']<(minute+1)*60]
    if window:out['minutes'].append(dict(minute=minute,samples=len(window),
        **{key:dict(min=min(x[key] for x in window),median=statistics.median(x[key] for x in window),
                    max=max(x[key] for x in window)) for key in ('heap','largest')}))
out['idle']={k:{key:statistics.median(x[key] for x in v) for key in ('heap','largest','tasks')} for k,v in r['idle'].items()}
out['rssi']={key:fn(s['rssi'] for s in b['samples']) for key,fn in [('minimum',min),('maximum',max),('median',statistics.median)]}
out['scope']='Independent gates; original memory failure retained. Endpoint decline alone does not identify a leak.'
(base/'independent-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
