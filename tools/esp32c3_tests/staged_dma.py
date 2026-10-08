"""Replay staged-output counters inside recorded sustained-playback windows.

Queue overruns indicate delayed descriptor reuse, not an exact acoustic gap
count. Idle/ramp activity also increments the counters. The observed delta
covers only the first through last selected samples, without extrapolation.
Write duration includes copying, waiting and preemption; it is not CPU time.
"""
import argparse
import json
import math
from pathlib import Path
import re

from common import sha

FIELDS = ('q_overruns', 'writes', 'written_bytes', 'write_us', 'max_write_us', 'errors')
WARMUP_SECONDS = 10
MAX_SAMPLE_GAP_SECONDS = 11


def parse(row):
    marker = 'PERF STAGED_DMA:'
    if marker not in row['line']:
        return None
    line = re.sub(r'\x1b\[[0-9;]*m', '', row['line'])
    tokens = line.split(marker, 1)[1].strip().split()
    if len(tokens) != len(FIELDS) or line.count('PERF ') != 1:
        raise ValueError('Incomplete or merged staged-DMA sample')
    result = dict(at=float(row['at']))
    if not math.isfinite(result['at']):
        raise ValueError('Invalid sample time')
    for token, field in zip(tokens, FIELDS):
        match = re.fullmatch(field+r'=(\d+)', token)
        if not match:
            raise ValueError('Invalid staged-DMA field')
        value = int(match[1])
        width = 32 if field in ('q_overruns', 'writes', 'errors') else 64
        if value >= 1 << width:
            raise ValueError('Counter out of range')
        result[field] = value
    if result['errors'] > result['writes'] or result['max_write_us'] > result['write_us']:
        raise ValueError('Inconsistent staged-DMA counters')
    return result


def summarize(rows, start, end):
    if not math.isfinite(start) or not math.isfinite(end) or start >= end:
        raise ValueError('Invalid playback window')
    # Validate every diagnostic row, including malformed rows outside the
    # selected window, instead of silently discarding damaged evidence.
    parsed = [sample for row in rows if (sample := parse(row)) is not None]
    selected = [sample for sample in parsed if start <= sample['at'] <= end]
    if len(selected) < 3:
        raise ValueError('At least three staged-DMA samples are required')
    for previous, current in zip(selected, selected[1:]):
        if current['at'] <= previous['at']:
            raise ValueError('Duplicate or unordered sample time')
        if any(current[field] < previous[field] for field in FIELDS):
            raise ValueError('Counter reset or wrap; do not infer a playback delta')
    first, last = selected[0], selected[-1]
    times = [start] + [sample['at'] for sample in selected] + [end]
    maximum_gap = max(b-a for a, b in zip(times, times[1:]))
    delta = {field:last[field]-first[field] for field in FIELDS if field != 'max_write_us'}
    return dict(samples=len(selected), start=first['at'], end=last['at'],
                observed_seconds=last['at']-first['at'],
                coverage_complete=maximum_gap <= MAX_SAMPLE_GAP_SECONDS,
                maximum_sample_gap_seconds=maximum_gap, delta=delta,
                maximum_write_us_since_boot=last['max_write_us'],
                note=__doc__.strip(), acoustic_continuity_qualified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    paths = {name: args.input/name for name in ('performance.json', 'status.json', 'report.json')}
    data = {name: json.loads(path.read_text()) for name, path in paths.items()}
    result = dict(board=data['report.json']['board'], cases=[],
                  original_acceptance=data['report.json']['cases'],
                  source_sha256=sha(Path(__file__).read_bytes()),
                  input_sha256={name:sha(path.read_bytes()) for name,path in paths.items()})
    for batch in data['status.json']:
        if not batch['case'].startswith(('load:', 'tls-record:', 'soak:')):
            continue
        result['cases'].append(dict(name=batch['case'], interrupted=batch.get('interrupted', False),
            **summarize(data['performance.json'], batch['started_at']+WARMUP_SECONDS, batch['ended_at'])))
    if not result['cases']:
        raise ValueError('No sustained-playback windows')
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
