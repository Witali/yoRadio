"""Replay saved queue ownership/extent observations; no audio-duration inference."""
import collections
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, 'tools/esp32c3_tests')
from common import require
from production_health import validate_input_queue, output_window
from sustained_output import sustained_window

base = Path('.build/c3-input-usage-20261015/tls-pauses/pauses')
report = json.loads((base/'report.json').read_text())
health = json.loads((base/'health.json').read_text())
batch = next(x for x in json.loads((base/'status.json').read_text())
             if x['case'] == report['fixture_name'])
rows = [x for x in health if batch['started_at'] <= x['at'] <= batch['ended_at']]
_, measured = sustained_window(batch['samples'], rows, report['observation_seconds'])

def extent(values):
    return dict(min=min(values), median=statistics.median(values), max=max(values)) if values else None

def summarize(rows):
    queues = [validate_input_queue(x['input_queue']) for x in rows]
    require(all('ready_bytes' in q for q in queues), 'Missing usage instrumentation')
    ready = [q for q in queues if q['ready']]
    reading = [q for q in queues if q['reading']]
    return dict(samples=len(rows),
        resident=sorted(set(q['resident'] for q in queues)),
        ownership_histogram=dict(sorted(collections.Counter(
            f"ready={q['ready']},reading={q['reading']},writing={q['writing']}" for q in queues).items())),
        ready_nonempty_samples=len(ready),
        ready_extent_bytes=extent([q['ready_bytes'] for q in queues]),
        ready_slot_fill_fraction=extent([q['ready_bytes']/(q['ready']*q['packet_capacity']) for q in ready]),
        ready_sample_weighted_fill_fraction=(sum(q['ready_bytes'] for q in ready)/
            sum(q['ready']*q['packet_capacity'] for q in ready)) if ready else None,
        ready_unused_capacity=extent([q['ready']*q['packet_capacity']-q['ready_bytes'] for q in ready]),
        reading_slot_fill_fraction=extent([q['reading_bytes']/(q['reading']*q['packet_capacity']) for q in reading]))

audit=json.loads((base/'audit.json').read_text())
result=dict(image=report['image'], output=output_window(measured), sustained=summarize(measured), pauses=[],
    scope='Sampled committed extents include packet headers; reading is the whole lease, not its unconsumed suffix. Writing leases are excluded from playable bytes. Fill is sample-weighted, not a histogram of all packets. Server pauses do not prove exact device arrival times.')
for pause in audit['delivery']['pauses']:
    start,end=pause['started_at'],pause['ended_at']
    near=[r for r in measured if start-2 <= r['at'] <= end+2]
    result['pauses'].append(dict(requested_seconds=pause['requested_seconds'],
        preceding=summarize([r for r in measured if start-5 <= r['at'] < start]),
        samples=[dict(seconds=r['at']-batch['started_at'], queue=r['input_queue'], output=r['output']) for r in near]))
(base/'usage-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='pauses'}))
