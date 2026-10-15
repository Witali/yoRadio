import json
from pathlib import Path
root=Path('.build/c3-flac-input12-20261015/matched');out=[]
for folder in sorted(root.glob('*/pauses')):
    r=json.loads((folder/'report.json').read_text());states=json.loads((folder/'status.json').read_text())
    hs=json.loads((folder/'health.json').read_text());batch=next(s for s in states if s['case']=='public-flac-reference')
    event=r['server_events'][0];start=batch['started_at']
    row=dict(case=folder.parent.name,pauses=event['pauses'],
        playback_start=start,rssi_range=[min(s['rssi'] for s in batch['samples']),max(s['rssi'] for s in batch['samples'])],
        max_health_request_ms=max(h['request_ms'] for h in hs),
        eof_batches=[dict(case=b['case'],started_at=b['started_at'],ended_at=b['ended_at'],last_samples=b['samples'][-4:]) for b in states if b['case'] not in ('public-flac-reference','initial','final')],
        slow_delivery=[w for w in event['delivery']['windows'] if w.get('max_write_seconds',0)>.4])
    out.append(row)
(root/'delivery-inspection.json').write_text(json.dumps(out,indent=2)+'\n')
for row in out:
    print(json.dumps({k:v for k,v in row.items() if k!='eof_batches'},indent=2))
    for b in row['eof_batches']:
        print(b['case'],[(s['seconds'],s.get('audio'),s.get('format')) for s in b['last_samples']])
