"""Locate expanded-queue DMA increments without claiming sub-window causality."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'sources/tools/esp32c3_tests'))
from staged_dma import parse

folder = ROOT/'physical/expanded'
batch = next(b for b in json.loads((folder/'status.json').read_text()) if b['case'].startswith('load:stress-flac'))
rows = json.loads((folder/'performance.json').read_text())
report = json.loads((folder/'report.json').read_text())
start, end = batch['started_at'], batch['ended_at']
points = [v for row in rows if (v := parse(row)) is not None and start <= v['at'] <= end]
incidents = []
for previous, current in zip(points, points[1:]):
    if current['q_overruns'] == previous['q_overruns']: continue
    low, high = previous['at'], current['at']
    selected = [s for s in batch['samples'] if low <= start+s['seconds'] <= high]
    near = [dict(seconds=r['at']-start, line=r['line']) for r in rows if low-1 <= r['at'] <= high+6]
    delivery = []
    for event in report.get('server_events', []):
        if event.get('fixture') != 'stress-flac-48000-2ch-16bit-610s': continue
        delivery.extend(w for w in event.get('delivery', {}).get('windows', []) if w['started_at'] < high and w['ended_at'] > low)
    incidents.append(dict(from_seconds=low-start, to_seconds=high-start,
        overruns=current['q_overruns']-previous['q_overruns'],
        write_errors=current['errors']-previous['errors'],
        min_rssi=min(s['rssi'] for s in selected), max_rssi=max(s['rssi'] for s in selected),
        max_http_ms=max(s['request_ms'] for s in selected), rows=near, delivery=delivery))
result = dict(incidents=incidents, scope='Five-second counter intervals and overlapping observations; RSSI/host delivery correlation is not causal packet-loss or acoustic proof.')
(ROOT/'incidents.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({**result, 'incidents': [{k:v for k,v in i.items() if k not in ('rows','delivery')} for i in incidents]}, indent=2))
