"""Bound delay after the device's snapshot, without changing playback verdicts."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
folder=ROOT/'physical/public'
health=json.loads((folder/'health.json').read_text())
requests=[json.loads(line) for line in (folder/'request-phases.jsonl').read_text().splitlines()]
results=[]
for target in health:
    if target['request_ms']<2000:continue
    # Each device timestamp was taken after request start and before response
    # completion. Intersect nearby fast request intervals to bound clock offset.
    near=[r for r in health if r is not target and r['boot_id']==target['boot_id']
          and abs(r['at']-target['at'])<=15 and r['request_ms']<500]
    assert len(near)>=3
    lower=max(r['at']-r['request_ms']/1000-r['uptime_ms']/1000 for r in near)
    upper=min(r['at']-r['uptime_ms']/1000 for r in near)
    assert lower<=upper
    lower-=.010;upper+=.010  # timestamp granularity and bounded local drift slack
    start=target['at']-target['request_ms']/1000
    connect=[r for r in requests if r['phase']=='connect' and abs(r['at']-start)<.01]
    assert len(connect)==1
    trace=[r for r in requests if r['request']==connect[0]['request']]
    result=dict(health=target,nearby_fast_samples=len(near),offset_seconds=[lower,upper],
        post_snapshot_delay_seconds=[target['at']-target['uptime_ms']/1000-upper,
                                     target['at']-target['uptime_ms']/1000-lower],
        request_phases=trace)
    results.append(result)
report=dict(scope='Inference assuming clock offset stays within adjacent-sample bounds plus 10 ms slack; not packet capture',
    original_test_verdicts_unchanged=True,events=results,
    inputs={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
            for name in ('health.json','request-phases.jsonl')})
(ROOT/'latency-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps([dict(request_ms=r['health']['request_ms'],after_snapshot=r['post_snapshot_delay_seconds']) for r in results]))
