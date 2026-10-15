"""Replay the bounded ISR history for the actual observed playback interval."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
from pipeline_probe import analyze_pipeline
from production_health import check_health,check_decoder_health
base=Path('.build/c3-confirm-probe-20261014/https-radio/public-radio')
r=json.loads((base/'report.json').read_text())
require(any(c['name']=='all-decoder-health' for c in r['cases']),'Campaign unfinished')
states=json.loads((base/'status.json').read_text());health=json.loads((base/'health.json').read_text())
out=dict(image=r['image'],laboratory_diagnostic=True,cases=[],
         scope='Call phases and checkpoint ages; not scheduler states or acoustic continuity. Overwritten events remain counted.')
for batch in states:
    if not batch['case'].startswith('https:'):continue
    rows=[h for h in health if batch['started_at']+15<=h['at']<=batch['ended_at']]
    last=batch['samples'][-1]['seconds'] if batch['samples'] else 0
    row=dict(name=batch['case'],requested_seconds=r['public_seconds'],last_observation_seconds=last,
             full_duration_observed=last>=r['public_seconds']-1,result='FAIL')
    try:
        row['pipeline']=analyze_pipeline(rows)
        row['health']=check_health(rows);row['decoder_health']=check_decoder_health(rows)
        row['age_ranges_by_phase']={}
        for phase in range(8):
            events=[e for e in row['pipeline']['events'] if e['phases']==phase]
            if not events:continue
            row['age_ranges_by_phase'][phase]=dict(retained=len(events),ages_ms={
                name:dict(minimum=min(e['ages_ms'][name] for e in events),maximum=max(e['ages_ms'][name] for e in events))
                for name in ('output_checkpoint','pcm_packet','encoded_packet','http_read')})
        row['result']='PASS' # Integrity of the replay; output counters may still report a failure.
    except Exception as error:row['reason']=str(error)
    out['cases'].append(row)
(base/'pipeline-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
