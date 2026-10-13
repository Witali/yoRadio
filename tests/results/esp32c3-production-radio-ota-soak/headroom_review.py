"""Keep the failing largest-block gate and describe its sampled time windows."""
import collections,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
load=lambda name:json.loads((ROOT/'physical'/name).read_text())
REQUIRED_LARGEST_FREE_BLOCK=8192
WARMUP_SECONDS=15
batch=next(b for b in load('status.json') if b['case']=='public-he-https-600s')
health=[h for h in load('health.json') if batch['started_at']<=h['at']<=batch['ended_at']]
assert len(health)==len(batch['samples'])
rows=[dict(h,seconds=s['seconds'],rssi=s.get('rssi')) for s,h in zip(batch['samples'],health) if s['seconds']>=WARMUP_SECONDS]
runs=[]
for i,row in enumerate(rows):
    if row['largest']>=REQUIRED_LARGEST_FREE_BLOCK:continue
    if not runs or i!=runs[-1][-1]+1:runs.append([])
    runs[-1].append(i)
intervals=[]
for indexes in runs:
    first,last=indexes[0],indexes[-1]
    intervals.append(dict(samples=len(indexes),
        first_seconds=rows[first]['seconds'],last_seconds=rows[last]['seconds'],
        observed_span_seconds=rows[last]['seconds']-rows[first]['seconds'],
        preceding_seconds=rows[first-1]['seconds'] if first else None,
        following_seconds=rows[last+1]['seconds'] if last+1<len(rows) else None,
        measurements=[{key:rows[i][key] for key in ('seconds','heap','largest','minimum_heap','rssi')} for i in indexes]))
report=dict(result='FAIL' if runs else 'PASS',threshold_bytes=REQUIRED_LARGEST_FREE_BLOCK,
    steady_samples=len(rows),below_budget_samples=sum(map(len,runs)),intervals=intervals,
    largest_histogram=dict(sorted(collections.Counter(r['largest'] for r in rows).items())),
    minimum_heap=min(r['heap'] for r in rows),minimum_largest=min(r['largest'] for r in rows),
    note='Sampled intervals, not continuous coverage or proof of allocation failure. No allocation owner is identified.',
    input_sha256={name:hashlib.sha256((ROOT/'physical'/name).read_bytes()).hexdigest() for name in ('status.json','health.json','soak.json')})
(ROOT/'headroom-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
