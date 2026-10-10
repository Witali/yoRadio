"""Summarize opt-in lwIP/heap snapshots without changing playback acceptance.

Sampling happens on the TCPIP thread; the HTTP thread logs the snapshot later.
The host receive timestamp minus age_ms estimates the sample time. Serial and
host scheduling delay still apply. Queue byte counts are logical payload, not
unique allocated RAM; Wi-Fi/TLS/application queues are not counted.
"""
import argparse
import json
import math
from pathlib import Path
import re
import statistics

from common import sha

FIELDS = ('seq', 'age_ms', 'heap', 'largest', 'used', 'blocks', 'free_blocks',
          'active', 'tw', 'bound', 'listen', 'tx_segments', 'tx_bytes',
          'rx_segments', 'rx_bytes', 'missed', 'walk_us')
METRICS = FIELDS[2:15] + ('walk_us',)
BIN_SECONDS = 30
MAX_SAMPLE_GAP_SECONDS = 11  # Two nominal five-second profiler intervals.
RX_FIELDS = ('seq', 'age_ms', 'window', 'maximum', 'refused')


def parse_receive_snapshot(row):
    """Optional receive-credit snapshot; uncredited bytes are not allocated RAM."""
    if 'PERF NET_RX:' not in row['line']:
        return None
    tail = re.sub(r'\x1b\[[0-9;]*m', '', row['line'].split('PERF NET_RX:', 1)[1]).strip()
    tokens = tail.split()
    if len(tokens) != len(RX_FIELDS):
        raise ValueError('Incomplete receive-window snapshot')
    values = {}
    for token, expected in zip(tokens, RX_FIELDS):
        match = re.fullmatch(r'([a-z_]+)=(\d+)', token)
        if not match or match[1] != expected:
            raise ValueError('Invalid receive-window field')
        values[expected] = int(match[2])
    if any(values[k] > 0xffffffff for k in RX_FIELDS if k != 'age_ms'):
        raise ValueError('Receive-window counter outside uint32 range')
    if not values['seq'] or values['window'] > values['maximum']:
        raise ValueError('Invalid receive-window counters')
    logged_at = float(row['at'])
    sample_at = logged_at - values['age_ms']/1000
    if not math.isfinite(logged_at) or not math.isfinite(sample_at):
        raise ValueError('Invalid receive-window timestamp')
    return dict(logged_at=logged_at, sample_at=sample_at,
                uncredited=values['maximum']-values['window'], **values)


def parse_snapshot(row):
    if 'PERF NET_HEAP:' not in row['line']:
        return None
    tail = re.sub(r'\x1b\[[0-9;]*m', '', row['line'].split('PERF NET_HEAP:', 1)[1]).strip()
    tokens = tail.split()
    if len(tokens) != len(FIELDS):
        raise ValueError('Incomplete network heap snapshot')
    values = {}
    for token, expected in zip(tokens, FIELDS):
        match = re.fullmatch(r'([a-z_]+)=(\d+)', token)
        if not match or match[1] != expected:
            raise ValueError('Invalid network heap field')
        values[expected] = int(match[2])
    if any(values[k] > 0xffffffff for k in FIELDS if k != 'age_ms'):
        raise ValueError('Counter outside uint32 range')
    if not values['seq'] or values['largest'] > values['heap']:
        raise ValueError('Invalid network heap counters')
    logged_at = float(row['at'])
    sample_at = logged_at - values['age_ms']/1000
    if not math.isfinite(logged_at) or not math.isfinite(sample_at):
        raise ValueError('Invalid sample timestamp')
    return dict(logged_at=logged_at, sample_at=sample_at, **values)


def ranges(samples, keys):
    return {k: dict(min=min(s[k] for s in samples),
                    median=statistics.median(s[k] for s in samples),
                    max=max(s[k] for s in samples)) for k in keys} if samples else {}


def summarize(report, status, rows):
    snapshots = [s for row in rows if (s := parse_snapshot(row)) is not None]
    result = dict(cases=[], note=__doc__.strip())
    previous_end = float('-inf')
    for case in report['cases']:
        if not case['name'].startswith(('http:', 'https:')):
            continue
        transport, name = case['name'].split(':', 1)
        item = dict(name=name, transport=transport, acceptance=case, metrics_available=False)
        result['cases'].append(item)
        window = report.get('windows', {}).get(name)
        if not window or 'end' not in window:
            item['reason'] = 'Missing completed playback window'
            continue
        start, end = window['start'], window['end']
        if not math.isfinite(start) or not math.isfinite(end) or not previous_end <= start < end:
            raise ValueError('Overlapping, reversed or invalid playback windows')
        previous_end = end
        selected = [s for s in snapshots if start <= s['sample_at'] < end]
        item.update(window=window, samples=selected)
        issues = []
        if len(selected) < 3:
            issues.append('Fewer than three network heap samples')
        if any(s['age_ms'] > MAX_SAMPLE_GAP_SECONDS*1000 for s in selected):
            issues.append('Stale network heap sample')
        if any(b['seq'] != a['seq'] + 1 for a, b in zip(selected, selected[1:])):
            issues.append('Nonconsecutive snapshot sequence')
        if any(b['missed'] != a['missed'] for a, b in zip(selected, selected[1:])):
            issues.append('Missed-callback counter changed')
        times = [start] + [s['sample_at'] for s in selected] + [end]
        if any(b < a or b-a > MAX_SAMPLE_GAP_SECONDS for a, b in zip(times, times[1:])):
            issues.append('Missing or unordered sample interval')
        wait_rows = [r for r in rows if start <= r['at'] < end and 'PERF NET_HEAP_WAIT:' in r['line']]
        if wait_rows:
            issues.append('Callback allocation, queue or pending warning')
        item.update(issues=issues, wait_rows=wait_rows, metrics_available=not issues,
                    ranges=ranges(selected, METRICS), bins=[])
        for offset in range(0, math.ceil(end-start), BIN_SECONDS):
            subset = [s for s in selected if start+offset <= s['sample_at'] < min(start+offset+BIN_SECONDS, end)]
            item['bins'].append(dict(start_seconds=offset, end_seconds=min(offset+BIN_SECONDS, end-start),
                                     count=len(subset), ranges=ranges(subset, METRICS)))
        states = [s for batch in status if batch['case'] == name for s in batch['samples']]
        item['webui'] = dict(samples=len(states),
                            audio_active=sum(s.get('audio') is True for s in states),
                            rssi=ranges([s for s in states if 'rssi' in s], ('rssi',)),
                            latency=ranges([s for s in states if 'request_ms' in s], ('request_ms',)))
    return result


def inspect(folder):
    paths = [folder/name for name in ('report.json', 'status.json', 'performance.json')]
    result = summarize(*(json.loads(p.read_text(encoding='utf-8')) for p in paths))
    result['input_sha256'] = {p.name: sha(p.read_bytes()) for p in paths}
    result['source_sha256'] = sha(Path(__file__).read_bytes())
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    summary = inspect(args.input)
    args.output.write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8', newline='\n')
    for case in summary['cases']:
        print(case['name'], case['acceptance']['result'], 'network_metrics=', case['metrics_available'], case.get('issues'))
