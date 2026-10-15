import collections,json
from pathlib import Path
base=Path('.build/c3-raw-tail-20261015/physical')
rows=json.loads((base/'summary.json').read_text())
result=[]
for row in rows:
    probe=row['pipeline'];events=probe['events']
    report=json.loads((base/row['case']/'report.json').read_text())
    flags=collections.Counter((e['decoder_work']['feed_active'],e['decoder_work']['pcm_wait_active']) for e in events)
    item=dict(case=row['case'],output=probe['output'],retained=probe['retained_events'],
        overwritten=probe['overwritten_events'],process_max_since_boot_ms=probe['process_max_since_boot_ms'],
        work_states=[dict(feed_active=k[0],pcm_wait_active=k[1],events=v) for k,v in sorted(flags.items())],
        web_memory=report['web_memory'],ages_ms={},work_ms={})
    if events:
        for k in events[0]['ages_ms']:
            values=[e['ages_ms'][k] for e in events];item['ages_ms'][k]=[min(values),max(values)]
        for k in ('feed_elapsed_ms','pcm_wait_elapsed_ms','last_completed_batch_process_max_ms'):
            values=[e['decoder_work'][k] for e in events];item['work_ms'][k]=[min(values),max(values)]
    result.append(item)
    print(json.dumps(item))
(base/'work-inspection.json').write_text(json.dumps(result,indent=2)+'\n')
