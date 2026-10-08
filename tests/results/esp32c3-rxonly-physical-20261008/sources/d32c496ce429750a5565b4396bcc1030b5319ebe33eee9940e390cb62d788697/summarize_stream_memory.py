"""Replay a completed continuous AAC study without attributing unrelated RAM.

RX ranges are actual live allocations; TCP receive credit is logical payload.
Their snapshots and CPU heap samples are asynchronous. Window medians are
comparisons, not an exact subtraction or proof of sample-level audio continuity.
"""
import argparse
import json
from pathlib import Path

from common import sha
from network_memory import MAX_SAMPLE_GAP_SECONDS, parse_receive_snapshot, parse_snapshot, ranges
from rx_ownership import analyze
from summarize_sustained import summarize as playback_summary

TLSF_HEADER_BYTES = 4
WARMUP_SECONDS = 10
SUBWINDOW_SECONDS = 300


def summarize(folder):
    names = ('report.json', 'status.json', 'performance.json', 'checkpoint.json')
    raw = {name: (folder/name).read_bytes() for name in names}
    report, batches, records, checkpoint = (json.loads(raw[name]) for name in names)
    if not checkpoint.get('finished') or not checkpoint.get('complete'):
        raise ValueError('Study is incomplete; retain checkpoints without a completed summary')
    loads = [b for b in batches if b['case'].startswith('load:')]
    if len(loads) != 1 or loads[0].get('in_progress') or loads[0].get('interrupted'):
        raise ValueError('Missing, duplicate or interrupted load window')
    load = loads[0]
    start, end = load['started_at'], load['ended_at']
    if end-start < report['load_seconds']:
        raise ValueError('Observed load is shorter than the requested duration')
    name = load['case'].split(':', 1)[1]
    expected = ['idle-before', 'cpu-under-http-load:'+name, 'idle-after',
                'stop-recovery', 'runtime', 'restore-board']
    if [c['name'] for c in report['cases']] != expected:
        raise ValueError('Missing or out-of-order study checks')
    idle_batches = [b for b in batches if b['case'] == 'settled-idle']
    if len(idle_batches) != 2 or any(b.get('interrupted') or b.get('in_progress') for b in idle_batches):
        raise ValueError('Missing completed idle windows')
    result = dict(input_sha256={n: sha(data) for n, data in raw.items()},
                  image=report['board']['app_elf_sha256'],
                  fixture_hashes=report['fixture_hashes'],
                  cpu_budget_percent=report.get('cpu_budget_percent', 85),
                  requested_seconds=report['load_seconds'], observed_seconds=end-start,
                  acceptance=report['cases'], playback=playback_summary(folder),
                  note=__doc__.strip(), acoustic_continuity_qualified=False)
    result['idle'] = {}
    for case in (report['cases'][0], report['cases'][2]):
        if case['result'] == 'PASS':
            result['idle'][case['name']] = ranges(case['evidence']['samples'], ('heap', 'largest', 'tasks'))

    # Never drop a damaged RX row to make the remaining capture pass.
    try:
        owners = analyze(records)
    except ValueError as error:
        result['ownership'] = dict(complete=False, reason=str(error))
        return result
    result['ownership'] = {k: v for k, v in owners.items() if k != 'snapshots'}
    snapshots = owners['snapshots']
    # Inferred pinned TLSF headers, explicitly separate from measured ranges.
    # This is specific to this C3 build with heap poisoning/task tracking off.
    for s in snapshots:
        s['inferred_heap_bytes'] = s['allocated_payload_bytes'] + TLSF_HEADER_BYTES*s['unique_blocks']
    result['inferred_allocator_header_bytes'] = TLSF_HEADER_BYTES
    result['owner_phases'] = {}
    windows = [(label, b['started_at'], b['ended_at'])
               for label, b in zip(('idle-before', 'idle-after'), idle_batches)]
    steady_start = start+WARMUP_SECONDS
    windows += [('load', steady_start, end), ('first-minute', steady_start, min(steady_start+60, end)),
                ('last-minute', max(steady_start, end-60), end)]
    cursor = steady_start
    while cursor < end:
        stop = min(cursor+SUBWINDOW_SECONDS, end)
        windows.append((f'load-{round(cursor-start)}-{round(stop-start)}s', cursor, stop))
        cursor = stop
    for label, begin, finish in windows:
        selected = [s for s in snapshots if begin <= s['at'] < finish]
        times = [begin]+[s['at'] for s in selected]+[finish]
        gaps = [b-a for a, b in zip(times, times[1:])]
        result['owner_phases'][label] = dict(start=begin, end=finish, snapshots=len(selected),
            coverage_complete=bool(selected) and all(0 <= gap <= MAX_SAMPLE_GAP_SECONDS for gap in gaps),
            maximum_sample_gap_seconds=max(gaps),
            ranges=ranges(selected, ('live', 'allocated_payload_bytes', 'inferred_heap_bytes',
                                     'walk_us', 'unmatched')))
    result['ownership']['load_coverage_complete'] = result['owner_phases']['load']['coverage_complete']
    # Aged TCP snapshots must be assigned by their estimated collection time,
    # not by when the UART reader received them five seconds later.
    try:
        net = [s for r in records if (s := parse_snapshot(r)) is not None]
        credit = [s for r in records if (s := parse_receive_snapshot(r)) is not None]
    except ValueError as error:
        result['network'] = dict(complete=False, reason=str(error))
        return result
    result['network'] = dict(note='Host receive time minus age_ms; transport delay remains. '
                            'Uncredited/refused bytes are not allocated RAM and must not be added to RX storage.',
                            windows={})
    for label, begin, finish in windows:
        selected = [s for s in net if begin <= s['sample_at'] < finish]
        rx = [s for s in credit if begin <= s['sample_at'] < finish]
        times = [begin]+[s['sample_at'] for s in selected]+[finish]
        complete = bool(selected) and all(0 <= b-a <= MAX_SAMPLE_GAP_SECONDS for a, b in zip(times, times[1:]))
        complete &= all(b['seq'] == a['seq']+1 and b['missed'] == a['missed']
                        for a, b in zip(selected, selected[1:]))
        complete &= all(s['age_ms'] <= MAX_SAMPLE_GAP_SECONDS*1000 for s in selected)
        complete &= [s['seq'] for s in selected] == [s['seq'] for s in rx]
        result['network']['windows'][label] = dict(samples=len(selected), coverage_complete=complete,
            heap=ranges(selected, ('heap', 'largest', 'blocks', 'free_blocks', 'age_ms', 'missed')),
            receive_credit=ranges(rx, ('window', 'maximum', 'uncredited', 'refused')))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = summarize(args.folder)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k in
                     ('requested_seconds', 'observed_seconds', 'ownership', 'owner_phases', 'idle')}, indent=2))
