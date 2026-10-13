"""Replay FLAC timing evidence; host writes are not device receive timestamps."""
import argparse
import hashlib
import json
from pathlib import Path

from common import require
from pipeline_probe import analyze_pipeline
from production_health import output_window


def review(root, label):
    inputs = {}
    def read(relative, optional=False):
        path = root / relative
        if optional and not path.exists(): return None
        data = path.read_bytes()
        inputs[relative] = hashlib.sha256(data).hexdigest()
        return json.loads(data)
    batches = read(label + '/status.json')
    health = read(label + '-health.json')
    arenas = read(label + '-arena.json')
    timings = read(label + '-timing.json', True)
    queues = read(label + '-input.json', True)
    server = read('server.json')
    require(sum(len(b['samples']) for b in batches) == len(health) == len(arenas),
            'Incomplete or unpaired status/health/arena evidence')
    require(timings is None or len(timings) == len(health), 'Unpaired allocator timing')
    require(queues is None or len(queues) == len(health), 'Unpaired input queue statistics')
    results, offset = {}, 0
    for batch in batches:
        start, offset = offset, offset + len(batch['samples'])
        case = batch['case']
        if not case.startswith('flac-level8') or case.endswith((':eof', ':stop')): continue
        indexes = [i for i,s in enumerate(batch['samples'], start) if s['seconds'] >= 3]
        rows = [health[i] for i in indexes]
        require(case not in results, 'Repeated trials must have distinct names')
        # Fault counters remain explicit below. Isolate DMA deltas for
        # diagnosis even when qualification already failed at startup.
        counter_rows = [dict(h, allocation_failures=0, task_watchdog_events=0) for h in rows]
        output = output_window(counter_rows)
        states = [batch['samples'][i-start] for i in indexes]
        item = dict(output=output, rssi_range=[min(s['rssi'] for s in states), max(s['rssi'] for s in states)],
                    min_heap=min(h['heap'] for h in rows), min_largest=min(h['largest'] for h in rows),
                    observation_errors=batch.get('errors', []), drop_intervals=[])
        item['faults'] = {k: [rows[0][k], rows[-1][k]]
                         for k in ('allocation_failures', 'task_watchdog_events')}
        for before, after in zip(indexes, indexes[1:]):
            delta = (health[after]['output']['completion_queue_drops'] -
                     health[before]['output']['completion_queue_drops']) & 0xffffffff
            if delta:
                item['drop_intervals'].append(dict(drops=delta,
                    seconds=[batch['samples'][i-start]['seconds'] for i in (before,after)],
                    rssi=[batch['samples'][i-start]['rssi'] for i in (before,after)]))
        private = [arenas[i] for i in indexes]
        if all(a is not None for a in private):
            item['arena'] = dict(live_range=[min(a['live'] for a in private),max(a['live'] for a in private)],
                failures_delta=private[-1]['failures']-private[0]['failures'])
        if timings is not None and all(timings[i] is not None for i in indexes):
            first, last = timings[indexes[0]], timings[indexes[-1]]
            item['allocator'] = {k:dict(calls_delta=(last[k][0]-first[k][0]) & 0xffffffff,
                lifetime_max_us=last[k][1]) for k in first}
        if all('pipeline' in h for h in rows): item['pipeline'] = analyze_pipeline(counter_rows)
        if queues is not None and all(queues[i] is not None for i in indexes):
            item['input_queue_ranges'] = {k:[min(queues[i][k] for i in indexes),
                max(queues[i][k] for i in indexes)] for k in queues[indexes[0]]}
        # Only host events intersecting this Play window; delivery completion
        # can occur during EOF observation. Preserve the full matching record.
        item['server'] = [e for e in server if e.get('fixture') == 'flac-level8' and
            batch['started_at'] - 2 <= e.get('delivery', {}).get('started_at', -1) <= batch['ended_at']]
        results[case] = item
    return dict(input_sha256=inputs, cases=results,
                scope='Steady observations >=3 s; excludes startup, EOF and Stop. Not analog continuity.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--label', choices=('baseline', 'candidate'), required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.write_text(json.dumps(review(args.root, args.label), indent=2) + '\n')
