"""Pair heap and TCP credit from the same snapshot; correlation is not ownership.

Keep original acceptance. Payload credit is not allocated RAM, and refused data
overlaps credit. Never subtract either value from measured heap to 'fix' a gate.
"""
import argparse
import json
import math
from pathlib import Path
import statistics

from common import sha
from network_memory import parse_snapshot, parse_receive_snapshot, ranges, MAX_SAMPLE_GAP_SECONDS


def paired_metrics(rows, start, end):
    if not all(math.isfinite(t) for t in (start, end)) or start >= end:
        raise ValueError('Invalid observation window')
    issues, heap, receive = [], {}, {}
    for row in rows:
        for parser, target in ((parse_snapshot, heap), (parse_receive_snapshot, receive)):
            sample = parser(row)  # Malformed evidence is never silently dropped.
            if sample is not None:
                if sample['seq'] in target:
                    raise ValueError('Duplicate or reset snapshot sequence')
                target[sample['seq']] = sample
    pairs = []
    for seq, h in heap.items():
        if not start <= h['sample_at'] < end:
            continue
        r = receive.get(seq)
        if r is None or r['age_ms'] != h['age_ms']:
            issues.append(f'Unmatched receive snapshot {seq}')
            continue
        if abs(h['sample_at'] - r['sample_at']) > 1:
            issues.append(f'Delayed paired log {seq}')
        if h['age_ms'] > MAX_SAMPLE_GAP_SECONDS * 1000:
            issues.append(f'Stale snapshot {seq}')
        pairs.append(dict(h, **{k: r[k] for k in ('uncredited', 'refused', 'maximum')}))
    for seq, r in receive.items():
        if start <= r['sample_at'] < end and seq not in heap:
            issues.append(f'Unmatched heap snapshot {seq}')
    if len(pairs) < 3:
        issues.append('Fewer than three pairs')
    if any(b['seq'] != a['seq'] + 1 for a, b in zip(pairs, pairs[1:])):
        issues.append('Nonconsecutive sequence')
    if any(b['missed'] != a['missed'] for a, b in zip(pairs, pairs[1:])):
        issues.append('Missed callback')
    times = [start] + [p['sample_at'] for p in pairs] + [end]
    if any(b < a or b - a > MAX_SAMPLE_GAP_SECONDS for a, b in zip(times, times[1:])):
        issues.append('Missing or unordered interval')
    if any(start <= r['at'] < end + MAX_SAMPLE_GAP_SECONDS and
           ('PERF NET_HEAP_WAIT:' in r['line'] or 'serial capture interrupted' in r['line'])
           for r in rows):
        issues.append('Capture or callback warning near window')
    result = dict(metrics_available=not issues, issues=issues, count=len(pairs))
    if issues:
        return result
    # Descriptive correlation only: adjacent snapshots are not independent trials.
    heaps = [p['heap'] for p in pairs]
    credit = [p['uncredited'] for p in pairs]
    result['heap_credit_pearson_r'] = (statistics.correlation(heaps, credit)
        if len(set(heaps)) > 1 and len(set(credit)) > 1 else None)
    keys = ('heap', 'largest', 'blocks', 'active', 'tw', 'uncredited', 'refused', 'maximum')
    result['ranges'] = ranges(pairs, keys)
    result['bins'] = []
    for offset in range(0, math.ceil(end-start), 60):
        subset = [p for p in pairs if start+offset <= p['sample_at'] < min(start+offset+60, end)]
        result['bins'].append(dict(start=start+offset, end=min(start+offset+60, end),
                                   count=len(subset), ranges=ranges(subset, keys)))
    result['samples'] = pairs
    return result


def inspect(folder, name):
    paths = {key: folder/(key+'.json') for key in ('report', 'status', 'performance')}
    report, status, rows = (json.loads(paths[k].read_text()) for k in paths)
    batches = [b for b in status if b['case'] == 'load:'+name]
    if len(batches) != 1:
        raise ValueError('Missing unique load window')
    batch = batches[0]
    start, end = batch['started_at'], batch['ended_at']
    result = dict(board=report['board'], acceptance=report['cases'],
                  window=dict(start=start, end=end, warmup_seconds=10),
                  note=__doc__.strip(), input_sha256={k:sha(p.read_bytes()) for k,p in paths.items()})
    result['paired'] = paired_metrics(rows, start+10, end)
    result['server'] = [{k:e[k] for k in ('mode','fixture','sent','seconds','pacing_ratio') if k in e}
                        for e in report.get('server_events', []) + report.get('tls_events', [])
                        if e.get('fixture') == name]
    result['source_sha256'] = {p.name:sha(p.read_bytes()) for p in
        (Path(__file__), Path(__file__).with_name('network_memory.py'))}
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--case', default='hev2-44100-stereo')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = inspect(args.input, args.case)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result['paired'].items() if k not in ('samples','bins')}))
