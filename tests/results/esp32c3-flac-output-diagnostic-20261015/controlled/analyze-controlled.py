import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
from pipeline_probe import analyze_pipeline
from production_health import check_health,check_decoder_health
base=Path('.build/c3-flac-output-diagnostic-20261015/controlled')
out=[]
for mode in ('control','pauses'):
    directory=base/mode
    r=json.loads((directory/'report.json').read_text())
    require(any(c['name']=='decoder' for c in r['cases']),'Incomplete case')
    states=json.loads((directory/'status.json').read_text());hs=json.loads((directory/'health.json').read_text())
    batch=next(s for s in states if s['case']=='public-flac-reference')
    paired=[h for h in hs if batch['started_at']<=h['at']<=batch['ended_at']]
    require(len(paired)==len(batch['samples']),'Unpaired playback')
    selected=[h for s,h in zip(batch['samples'],paired) if s['seconds']>=2]
    events=[]
    for a,b in zip(selected,selected[1:]):
        if a['output']['completion_queue_drops']!=b['output']['completion_queue_drops']:
            events.append(dict(seconds=[a['at']-batch['started_at'],b['at']-batch['started_at']],before=a,after=b))
    result=dict(mode=mode,counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
        failures=[c for c in r['cases'] if c['result']!='PASS'],health=check_health(hs),decoder=check_decoder_health(hs),
        pipeline=analyze_pipeline(selected),changed_intervals=events,server_events=r['server_events'])
    out.append(result)
(base/'pipeline-audit.json').write_text(json.dumps(out,indent=2)+'\n')
for row in out:print(json.dumps({k:row[k] for k in ('mode','counts','pipeline','server_events')}))
