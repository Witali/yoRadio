import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from pipeline_probe import analyze_pipeline
from production_health import check_health,check_decoder_health
from public_file_acceptance import check_finite_playback
base=Path('.build/c3-decode-probe-20261015/public')
out=[]
for directory in sorted(base.glob('flac-*')):
    r=json.loads((directory/'report.json').read_text())
    hs=json.loads((directory/'health.json').read_text())
    states=json.loads((directory/'status.json').read_text())
    result=dict(suite=directory.name,counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
        complete=any(c['name']=='all-decoder-health' for c in r['cases']),cases=[],health=check_health(hs),decoder=check_decoder_health(hs))
    for batch in states:
        if not batch['case'].startswith('https:flac:'):continue
        played=check_finite_playback(batch['samples'],r['references']['sources']['flac']['spec'])
        start=batch['started_at'];steady=[h for h in hs if start+played['first_playback_seconds']+3<=h['at']<=start+played['first_stopped_seconds']-1]
        pipeline=analyze_pipeline(steady)
        changed=[]
        for a,b in zip(steady,steady[1:]):
            if a['output']['completion_queue_drops']!=b['output']['completion_queue_drops']:
                changed.append(dict(seconds=[a['at']-start,b['at']-start],before=a,after=b))
        result['cases'].append(dict(case=batch['case'],playback=played,pipeline=pipeline,changed_intervals=changed,
            input_resident=sorted({h['input_queue']['resident'] for h in steady}),
            input_occupied_range=[min(h['input_queue']['occupied'] for h in steady),max(h['input_queue']['occupied'] for h in steady)]))
    out.append(result)
(base/'pipeline-audit.json').write_text(json.dumps(out,indent=2)+'\n')
for row in out:
    print(row['suite'],row['counts'],'complete',row['complete'])
    for case in row['cases']:print(case['case'],case['pipeline']['output'],'retained',case['pipeline']['retained_events'],'process_max_ms',case['pipeline']['process_max_since_boot_ms'])
