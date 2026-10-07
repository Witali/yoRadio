"""Summarize RX ownership alongside unchanged pool-settle acceptance gates."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

from rx_ownership import analyze
from common import Failure, check_cpu


def summarize(folder):
    paths = {name: folder / (name + '.json') for name in ('report', 'performance', 'status')}
    report, records, observations = (json.loads(paths[n].read_text()) for n in paths)
    result = dict(image=report['board']['app_elf_sha256'],
                  input_sha256={n: hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()},
                  acceptance={c['name']: c['result'] for c in report['cases']},
                  fixture_hashes=report['fixture_hashes'])
    cases = {c['name']: c for c in report['cases']}
    before, after = (cases[n]['evidence'] for n in ('idle-before', 'idle-after'))
    result['idle'] = {key: dict(before=statistics.median(r[key] for r in before),
                              after=statistics.median(r[key] for r in after))
                      for key in ('heap', 'largest', 'tasks')}
    result['phase_metrics'] = {}
    for window in report['windows']:
        name = window['name']
        start, end = window['start']+window['warmup'], window['end']
        selected = [r for r in records if start <= r['at'] <= end]
        item = result['phase_metrics'][name] = {}
        try:
            item['cpu_and_heap'] = dict(result='PASS', **check_cpu(selected,
                max_busy=report.get('cpu_budget_percent', 85), start=start, end=end))
        except Failure as error:
            item['cpu_and_heap'] = dict(result='FAIL', reason=str(error))
        batches = [b for b in observations if b['case'] == name]
        if len(batches) != 1: raise ValueError('Missing/duplicate status phase')
        item['maximum_http_ms'] = max(s['request_ms'] for s in batches[0]['samples'])
    # A malformed capture is retained as failed evidence, never repaired by
    # guessing fields or dropping the damaged snapshot.
    try:
        owner = analyze(records)
    except ValueError as error:
        result['ownership'] = dict(complete=False, reason=str(error))
        return result
    result['ownership'] = {k:v for k,v in owner.items() if k != 'snapshots'}
    windows = report['windows']
    bounds = [('idle-before', float('-inf'), windows[0]['start'])]
    bounds += [(w['name'], w['start'], w['end']) for w in windows]
    bounds += [('idle-after', windows[-1]['end'], float('inf'))]
    result['phases'] = {}
    # C3's pinned TLSF, poisoning/task tracking disabled: 4-byte size header
    # per unique allocation. Keep this inference separate from measured sizes.
    result['inferred_allocator_header_bytes'] = 4
    for name, start, end in bounds:
        rows = [s for s in owner['snapshots'] if start <= s['at'] < end]
        if not rows:
            raise ValueError('No RX snapshots in phase: ' + name)
        result['phases'][name] = dict(
            snapshots=len(rows),
            live_min=min(r['live'] for r in rows), live_max=max(r['live'] for r in rows),
            payload_bytes_min=min(r['allocated_payload_bytes'] for r in rows),
            payload_bytes_max=max(r['allocated_payload_bytes'] for r in rows),
            inferred_heap_bytes_max=max(r['allocated_payload_bytes'] + 4*r['unique_blocks'] for r in rows),
            maximum_walk_us=max(r['walk_us'] for r in rows),
            counter_high_water=max(r['peak'] for r in rows),
            unmatched_releases=max(r['unmatched'] for r in rows))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = summarize(args.folder)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
