import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
from pipeline_probe import analyze_pipeline
from production_health import check_health,check_decoder_health
base=Path('.build/c3-read512-20261015')
campaign=sys.argv[1];root=base/campaign
rows=[]
for path in sorted(root.rglob('report.json')):
    report=json.loads(path.read_text());folder=path.parent
    require(any(c['name']=='decoder' for c in report['cases']),'Incomplete run')
    states=json.loads((folder/'status.json').read_text())
    health=json.loads((folder/'health.json').read_text())
    batch=next(s for s in states if s['case']=='public-flac-reference')
    paired=[h for h in health if batch['started_at']<=h['at']<=batch['ended_at']]
    require(len(paired)==len(batch['samples']),'Unpaired health/status')
    selected=[h for s,h in zip(batch['samples'],paired) if s['seconds']>=2]
    pipeline=analyze_pipeline(selected)
    row=dict(case=folder.relative_to(root).as_posix(),
        results={v:sum(c['result']==v for c in report['cases']) for v in ('PASS','FAIL','BLOCKED')},
        failures=[c for c in report['cases'] if c['result']!='PASS'],
        health=check_health(health),decoder=check_decoder_health(health),pipeline=pipeline,
        resident_slots=sorted(set(h['input_queue']['resident'] for h in selected)),
        input_queue_first=selected[0]['input_queue'],
        requested_pauses=report['delivery_pause_schedule'],
        measured_pauses=report['server_events'][0].get('pauses',[]),
        tcp_nodelay_requested=report['server_events'][0]['tcp_nodelay_requested'],
        tcp_nodelay_actual=report['server_events'][0]['tcp_nodelay_actual'],
        delivery_windows=report['server_events'][0]['delivery']['windows'],
        drop_intervals=[])
    for a,b in zip(selected,selected[1:]):
        delta=b['output']['completion_queue_drops']-a['output']['completion_queue_drops']
        if delta:row['drop_intervals'].append(dict(
            seconds=[a['at']-batch['started_at'],b['at']-batch['started_at']],drops=delta,
            input_before=a['input_queue'],input_after=b['input_queue']))
    rows.append(row)
    print(json.dumps({k:row[k] for k in ('case','results','resident_slots','health')},ensure_ascii=False))
    print(json.dumps(pipeline['output']))
    print(json.dumps(row['drop_intervals']))
(root/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
