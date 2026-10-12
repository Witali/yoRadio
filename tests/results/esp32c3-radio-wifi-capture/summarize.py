"""Summarize retained checks; correlation and incomplete traces are not fixes."""
import json, statistics, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from web_tcp import parse
load=lambda name:json.loads((ROOT/name).read_text())
r=load('review.json');batches=load('physical/status.json');health=load('physical/health.json')
rows=load('physical/performance.json')
frames=[f for row in rows if (f:=parse(row)) is not None]
events=[f for f in frames if f['kind'] in ('event','wifi')]
gaps=[dict(previous=a,next=b,missing=(b['seq']-a['seq']-1)&0xffffffff)
      for a,b in zip(events,events[1:]) if b['seq']!=(a['seq']+1)&0xffffffff]
opus=[]
for batch in batches:
    if not batch['case'].startswith('opus:'):continue
    selected=[h for h in health if batch['started_at']<=h['at']<=batch['ended_at']]
    steady=[h for s,h in zip(batch['samples'],selected) if s['seconds']>=15]
    paired=r['correlations'][batch['case']]['evidence']
    opus.append(dict(case=batch['case'],memory=r['cases'][batch['case']]['memory'],
        first=statistics.median(h['heap'] for h in steady[:3]),
        last=statistics.median(h['heap'] for h in steady[-3:]),
        sampled_minimum=min(h['heap'] for h in steady),
        sampled_largest_minimum=min(h['largest'] for h in steady),
        paired_count=paired['count'],paired_valid=paired['metrics_available'],
        heap_credit_r=paired.get('heap_credit_pearson_r')))
begin=min(b['started_at'] for b in batches);end=max(b['ended_at'] for b in batches)
summary=dict(opus=opus,sequence_gaps=gaps,
    campaign_interval=[begin,end],
    connects=[dict(at=f['request']['at'],ms=f['request']['ms'],
        position='before observations' if f['request']['at']<begin else
        'after observations' if f['request']['at']>end else 'within observations',
        trace_result=f['trace_result']) for f in r['failed_connects']],
    serial_interruptions=load('physical/serial-transport.json'),
    lifetime_low_water=min(h['minimum_heap'] for h in health))
(ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
