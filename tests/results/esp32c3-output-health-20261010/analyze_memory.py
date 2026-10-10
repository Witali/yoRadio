import json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'physical/files/report.json').read_text())
health=json.loads((ROOT/'physical/files/health.json').read_text())
batches=json.loads((ROOT/'physical/files/status.json').read_text())
offset=0
for batch in batches:
    rows=batch['samples'];paired=health[offset:offset+len(rows)];offset+=len(rows)
    if batch['case'].startswith('https:'):break
steady=[(s,h) for s,h in zip(rows,paired) if s['seconds']>=15]
low=[dict(seconds=s['seconds'],heap=h['heap'],largest=h['largest'],rssi=s['rssi'],
          request_ms=s['request_ms'],output=h['output']) for s,h in steady if h['largest']<8192]
histogram={str(v):sum(h['largest']==v for s,h in steady) for v in sorted({h['largest'] for s,h in steady})}
idle={phase:{key:statistics.median(row[key] for row in samples) for key in ('heap','largest','tasks')}
      for phase,samples in report['idle'].items()}
result=dict(budget_largest_bytes=8192,below_budget_samples=low,largest_histogram=histogram,
            idle_medians=idle,lifetime_minimum_heap=min(h['minimum_heap'] for h in health),
            distinction='Headroom gate failure, not an observed allocation failure; keep original threshold and failed verdict',
            next_step='Measure allocation sizes and lifetimes under TLS frame growth before changing reserves or accepting a smaller budget')
(ROOT/'memory-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(below_budget_samples=len(low),minimum_largest=min(h['largest'] for s,h in steady),
                     lifetime_minimum_heap=result['lifetime_minimum_heap'],idle=idle)))
