"""Summarize inclusive HTTP/TLS/poll/AES wall times, never CPU attribution.

Counters are charged when each call returns. Nested stages overlap and a call
can cross a sampling boundary. Do not add their times or infer exact exclusive
CPU time by subtraction. max_us is the lifetime maximum, not a window maximum.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

STAGES = ('http', 'tls', 'poll', 'gcm', 'ctr')
COUNTERS = ('calls', 'elapsed_us', 'max_us', 'requested', 'completed',
            'ok', 'zero', 'retry', 'errors', 'le1024', 'le4096', 'le16384', 'larger')
FIELDS = ('seq', 'at_us', 'stage') + COUNTERS


def snapshots(rows):
    groups = []
    current = None
    for row in rows:
        line = re.sub(r'\x1b\[[0-9;]*m', '', row['line'])
        if 'serial capture interrupted' in line:
            raise ValueError('Interrupted telemetry capture')
        if 'PERF TLS_PATH' not in line:
            continue
        marker = 'PERF TLS_PATH:'
        if marker not in line or line.count('PERF ') != 1:
            raise ValueError('Damaged/merged TLS path sample')
        tokens = line.split(marker, 1)[1].strip().split()
        if len(tokens) != len(FIELDS):
            raise ValueError('Incomplete TLS path sample')
        values = {}
        for token, key in zip(tokens, FIELDS):
            match = re.fullmatch(key + r'=(\w+)', token)
            if not match:
                raise ValueError('Invalid TLS path field')
            value = match[1]
            if key != 'stage':
                if not value.isdecimal():
                    raise ValueError('Non-numeric TLS path counter')
                value = int(value)
                width = 64 if key in ('at_us', 'elapsed_us', 'requested', 'completed') else 32
                if value >= 1 << width:
                    raise ValueError('TLS path counter out of range')
            values[key] = value
        at = float(row['at'])
        if not math.isfinite(at):
            raise ValueError('Invalid capture time')
        if values['stage'] not in STAGES:
            raise ValueError('Unknown TLS path stage')
        if values['calls'] != sum(values[k] for k in ('ok', 'zero', 'retry', 'errors')):
            raise ValueError('Inconsistent outcome counts')
        if values['calls'] != sum(values[k] for k in ('le1024', 'le4096', 'le16384', 'larger')):
            raise ValueError('Inconsistent size bins')
        if values['max_us'] > values['elapsed_us'] or values['completed'] > values['requested']:
            raise ValueError('Inconsistent elapsed time/bytes')
        if current is None or current['seq'] != values['seq']:
            if current is not None and set(current['stages']) != set(STAGES):
                raise ValueError('Incomplete TLS path snapshot')
            if current is not None and (values['seq'] != current['seq'] + 1 or
                                        values['at_us'] <= current['at_us']):
                raise ValueError('TLS path sequence gap/reset')
            current = dict(seq=values['seq'], at_us=values['at_us'], first_at=at, last_at=at, stages={})
            groups.append(current)
        if values['at_us'] != current['at_us'] or values['stage'] in current['stages'] or at < current['last_at']:
            raise ValueError('Duplicate/inconsistent TLS path snapshot')
        current['last_at'] = at
        current['stages'][values['stage']] = {k: values[k] for k in COUNTERS}
    if current is None or set(current['stages']) != set(STAGES):
        raise ValueError('Missing/incomplete TLS path snapshot')
    for previous, current in zip(groups, groups[1:]):
        for stage in STAGES:
            if any(current['stages'][stage][key] < previous['stages'][stage][key] for key in COUNTERS):
                raise ValueError('TLS path counter reset/wrap')
    return groups


def summarize(rows, start, end):
    if not math.isfinite(start) or not math.isfinite(end) or start >= end:
        raise ValueError('Invalid playback window')
    selected = [g for g in snapshots(rows) if start <= g['first_at'] and g['last_at'] <= end]
    if len(selected) < 3:
        raise ValueError('At least three complete TLS path snapshots are required')
    first, last = selected[0], selected[-1]
    observed_us = last['at_us'] - first['at_us']
    times = [start] + [s['first_at'] for s in selected] + [end]
    gap = max(b - a for a, b in zip(times, times[1:]))
    stages = {}
    for stage in STAGES:
        delta = {k: last['stages'][stage][k] - first['stages'][stage][k] for k in COUNTERS if k != 'max_us'}
        stages[stage] = dict(delta=delta, inclusive_wall_percent=100 * delta['elapsed_us'] / observed_us,
                             mean_call_us=delta['elapsed_us'] / delta['calls'] if delta['calls'] else None,
                             max_us_since_boot=last['stages'][stage]['max_us'])
    return dict(snapshots=len(selected), observed_seconds=observed_us / 1e6,
                first_sequence=first['seq'], last_sequence=last['seq'],
                coverage_complete=gap <= 11, maximum_sample_gap_seconds=gap,
                stages=stages, note=__doc__.strip())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    paths = {name: args.input / (name + '.json') for name in ('performance', 'status', 'report')}
    data = {name: json.loads(path.read_text()) for name, path in paths.items()}
    cases = []
    for batch in data['status']:
        if batch['case'].startswith(('load:', 'tls-record:', 'soak:')):
            if batch.get('interrupted', False):
                raise ValueError('Interrupted playback window')
            cases.append(dict(name=batch['case'], **summarize(data['performance'], batch['started_at'] + 10, batch['ended_at'])))
    if not cases:
        raise ValueError('No sustained playback window')
    result = dict(cases=cases, original_acceptance=data['report']['cases'],
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  input_sha256={name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()})
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
