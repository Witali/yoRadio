import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from pipeline_probe import analyze_pipeline
folder=Path('.build/c3-read25-20261015/physical/read250/control')
states=json.loads((folder/'status.json').read_text());health=json.loads((folder/'health.json').read_text())
batch=next(s for s in states if s['case']=='public-flac-reference')
paired=[h for h in health if batch['started_at']<=h['at']<=batch['ended_at']]
assert len(paired)==len(batch['samples'])
selected=[h for s,h in zip(batch['samples'],paired) if s['seconds']>=2]
result=analyze_pipeline(selected)
print({k:v for k,v in result.items() if k!='events'})
for k in ('output_checkpoint','pcm_packet','encoded_packet','http_read'):
    if result['events']:print(k,min(e['ages_ms'][k] for e in result['events']),max(e['ages_ms'][k] for e in result['events']))
for a,b in zip(selected,selected[1:]):
    delta=b['output']['completion_queue_drops']-a['output']['completion_queue_drops']
    if delta:print('interval',a['at']-batch['started_at'],b['at']-batch['started_at'],'drops',delta,'input',a['input_queue'],b['input_queue'])
(folder/'control-inspection.json').write_text(json.dumps(result,indent=2)+'\n')
