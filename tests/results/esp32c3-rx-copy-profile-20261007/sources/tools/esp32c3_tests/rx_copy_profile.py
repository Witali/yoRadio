"""Validate copied RX buffer accounting before using it to size a fixed pool.

Bytes are heap allocation capacity (pbuf plus frame/alignment), excluding heap
headers. Peaks include all activity since boot, not just the selected window.
Class peaks occur independently; their sum is not the simultaneous total peak.
UART receive timestamps include transport delay. No physical audio qualification.
"""
import argparse
import json
import math
from pathlib import Path
import re
import struct
import zlib

from network_memory import MAX_SAMPLE_GAP_SECONDS, ranges

FIELDS = 'sequence allocations releases live peak bytes peak_bytes failed lost rejected max_frame pbuf_bytes capacity'.split()
CLASS_NAMES = ('0-128', '129-512', '513-1152', '1153-1600', '1601-65535')
CLASS_FIELDS = ('allocations', 'live', 'peak')
WIRE_FIELDS = FIELDS + [f'class{i}_{key}' for i in range(5) for key in CLASS_FIELDS]
MARKER = 'PERF RX_COPY:'
MONOTONIC = ('allocations', 'releases', 'peak', 'peak_bytes', 'failed', 'lost', 'rejected', 'max_frame')


def parse(row):
    line = row['line']
    if 'serial capture interrupted' in line:
        raise ValueError('Interrupted telemetry capture')
    if 'PERF RX_COPY' not in line:
        return None
    if line.count('PERF ') != 1 or MARKER not in line:
        raise ValueError('Merged or damaged RX copy row')
    tail = re.sub(r'\x1b\[[0-9;]*m', '', line.split(MARKER, 1)[1]).strip()
    tokens = tail.split(',')
    if len(tokens) != len(WIRE_FIELDS)+1 or not re.fullmatch(r'[0-9a-f]{8}', tokens[-1]):
        raise ValueError('Incomplete RX copy row')
    if any(not re.fullmatch(r'[0-9]+', token) for token in tokens[:-1]):
        raise ValueError('Invalid RX copy integer')
    values = [int(token) for token in tokens[:-1]]
    if any(value > 0xffffffff for value in values):
        raise ValueError('RX copy integer outside uint32')
    if zlib.crc32(struct.pack('<28I', *values)) != int(tokens[-1], 16):
        raise ValueError('RX copy checksum mismatch')
    result = dict(zip(WIRE_FIELDS, values))
    result['at'] = float(row['at'])
    if not math.isfinite(result['at']):
        raise ValueError('Invalid RX copy timestamp')
    return result


def analyze(rows):
    snapshots = [snapshot for row in rows if (snapshot := parse(row)) is not None]
    if not snapshots:
        raise ValueError('Missing RX copy telemetry')
    previous = None
    for s in snapshots:
        if not s['sequence'] or not s['pbuf_bytes'] or s['capacity'] != 64 or s['max_frame'] > 65535:
            raise ValueError('Invalid RX copy layout or sequence')
        if s['lost']:
            raise ValueError('Lost RX allocation tracking; pool sizing is invalid')
        if s['allocations']-s['releases'] != s['live']:
            raise ValueError('RX allocation/free balance mismatch')
        if not s['live'] <= s['peak'] <= min(s['capacity'], s['allocations']):
            raise ValueError('Invalid RX total peak')
        if not s['bytes'] <= s['peak_bytes'] or s['bytes'] < s['live']*s['pbuf_bytes']:
            raise ValueError('Invalid RX allocated byte count')
        if (s['live'] == 0) != (s['bytes'] == 0):
            raise ValueError('Empty RX byte/owner mismatch')
        for key in ('allocations', 'live'):
            if sum(s[f'class{i}_{key}'] for i in range(5)) != s[key]:
                raise ValueError('RX class total mismatch')
        for i in range(5):
            if not s[f'class{i}_live'] <= s[f'class{i}_peak'] <= min(s['peak'], s[f'class{i}_allocations']):
                raise ValueError('Invalid RX class peak')
        if s['rejected'] > s['allocations']:
            raise ValueError('Invalid RX input rejection count')
        if previous:
            if s['sequence'] != previous['sequence']+1 or s['at'] < previous['at']:
                raise ValueError('Missing, duplicate, reset or reordered RX copy row')
            if any(s[k] < previous[k] for k in MONOTONIC):
                raise ValueError('Regressing RX copy counter')
            if s['pbuf_bytes'] != previous['pbuf_bytes']:
                raise ValueError('RX pbuf layout changed')
            if any(s[f'class{i}_{k}'] < previous[f'class{i}_{k}']
                   for i in range(5) for k in ('allocations', 'peak')):
                raise ValueError('Regressing RX class counter')
        previous = s
    final = snapshots[-1]
    return dict(note=__doc__.strip(), snapshots=snapshots, accounting_complete=True,
                sizing_valid=not (final['failed'] or final['rejected']),
                faults={k: final[k] for k in ('failed', 'lost', 'rejected')},
                cumulative_at_last_snapshot={k: final[k] for k in FIELDS if k != 'sequence'},
                classes=[dict(frame_bytes=name, **{key: final[f'class{i}_{key}'] for key in CLASS_FIELDS})
                         for i, name in enumerate(CLASS_NAMES)])


def window(snapshots, start, end):
    if not math.isfinite(start) or not math.isfinite(end) or start >= end:
        raise ValueError('Invalid measurement window')
    selected = [s for s in snapshots if start <= s['at'] < end]
    times = [start]+[s['at'] for s in selected]+[end]
    max_gap = max(b-a for a, b in zip(times, times[1:]))
    result = dict(start=start, end=end, snapshots=len(selected), maximum_gap_seconds=max_gap,
                  coverage_complete=bool(selected) and max_gap <= MAX_SAMPLE_GAP_SECONDS,
                  sampled=ranges(selected, ('live', 'bytes')))
    if len(selected) >= 2:
        first, last = selected[0], selected[-1]
        result['delta'] = {k: last[k]-first[k] for k in ('allocations', 'releases', 'failed', 'rejected')}
        result['delta']['seconds'] = last['at']-first['at']
        result['classes'] = [dict(frame_bytes=name,
            arrivals=last[f'class{i}_allocations']-first[f'class{i}_allocations'],
            sampled=ranges(selected, (f'class{i}_live',)), peak_since_boot=last[f'class{i}_peak'])
            for i, name in enumerate(CLASS_NAMES)]
        result['peak_since_boot'] = {k: last[k] for k in ('peak', 'peak_bytes', 'max_frame')}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('performance', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--status', type=Path, help='Add completed idle/playback window summaries')
    args = parser.parse_args()
    result = analyze(json.loads(args.performance.read_bytes()))
    if args.status:
        batches = json.loads(args.status.read_bytes())
        if any(b.get('in_progress') or b.get('interrupted') for b in batches):
            raise ValueError('Incomplete measurement window')
        result['windows'] = [dict(case=b['case'], **window(result['snapshots'], b['started_at'], b['ended_at']))
                             for b in batches if 'started_at' in b and 'ended_at' in b]
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'snapshots'}, indent=2))


if __name__ == '__main__':
    main()
