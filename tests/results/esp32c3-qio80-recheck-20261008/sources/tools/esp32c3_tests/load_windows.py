"""Describe load telemetry inside recorded observation windows; never change gates.

No reconstruction from the next codec's first PCM is allowed. Missing or corrupt
telemetry remains visible. TCP receive credit is logical bytes, not RAM usage.
"""
import argparse
import json
import math
from pathlib import Path
import re

from common import sha
from network_memory import parse_snapshot, parse_receive_snapshot, ranges

LOAD_PREFIX = 'cpu-under-http-load:'
BIN_SECONDS = 30
CPU_KEYS = ('busy', 'idle', 'heap', 'largest')
NET_KEYS = ('heap', 'largest', 'blocks', 'active', 'tx_bytes', 'rx_bytes')
RX_KEYS = ('window', 'maximum', 'uncredited', 'refused')


def cpu_snapshot(row):
    if 'PERF CPU:' not in row['line']:
        return None
    fields = re.findall(r'\b(busy|idle|heap|largest)=([\d.]+)', row['line'])
    if len(fields) != len(CPU_KEYS) or {k for k, _ in fields} != set(CPU_KEYS):
        raise ValueError('Incomplete or duplicate CPU/heap fields')
    value = {k: float(v) for k, v in fields}
    if abs(value['busy']+value['idle']-100) >= .3 or value['largest'] > value['heap']:
        raise ValueError('Invalid CPU/heap counters')
    return dict(sample_at=float(row['at']), **value)


def summarize(report, status, rows):
    result = dict(cases=[], note=__doc__.strip())
    previous_end = float('-inf')
    for acceptance in report['cases']:
        if not acceptance['name'].startswith(LOAD_PREFIX):
            continue
        name = acceptance['name'][len(LOAD_PREFIX):]
        item = dict(name=name, acceptance=acceptance, issues=[])
        result['cases'].append(item)
        batches = [b for b in status if b['case'] == 'load:'+name]
        if len(batches) != 1 or not {'started_at', 'ended_at'} <= batches[0].keys():
            item['issues'].append('Missing unique explicit observation window')
            continue
        batch = batches[0]
        start, end = batch['started_at'], batch['ended_at']
        if not math.isfinite(start) or not math.isfinite(end) or not previous_end <= start < end:
            raise ValueError('Overlapping, reversed or invalid load windows')
        previous_end = end
        item['window'] = dict(start=start, end=end, seconds=end-start)
        for label, parser, keys in (('cpu', cpu_snapshot, CPU_KEYS),
                                    ('network', parse_snapshot, NET_KEYS),
                                    ('receive', parse_receive_snapshot, RX_KEYS)):
            samples = []
            for index, row in enumerate(rows):
                try:
                    value = parser(row)
                except ValueError as error:
                    if start <= row['at'] < end:
                        item['issues'].append(f'{label}: row {index}: {error}')
                    continue
                if value is not None and start <= value['sample_at'] < end:
                    samples.append(value)
            if any(b['sample_at'] < a['sample_at'] for a, b in zip(samples, samples[1:])):
                item['issues'].append(label+': unordered samples')
            item[label] = dict(samples=samples, available=bool(samples),
                               ranges=ranges(samples, keys), bins=[])
            for offset in range(0, math.ceil(end-start), BIN_SECONDS):
                subset = [s for s in samples if start+offset <= s['sample_at'] < min(start+offset+BIN_SECONDS, end)]
                item[label]['bins'].append(dict(start=offset, end=min(offset+BIN_SECONDS, end-start),
                                                count=len(subset), ranges=ranges(subset, keys)))
        # Both TCP lines come from one copied snapshot. Match by sequence, not
        # host arrival time; absence in older firmware is not a zero backlog.
        heap_by_seq = {s['seq']: s for s in item['network']['samples']}
        for sample in item['receive']['samples']:
            match = heap_by_seq.get(sample['seq'])
            if match is None or match['age_ms'] != sample['age_ms']:
                item['issues'].append(f"receive: unmatched snapshot {sample['seq']}")
        states = batch['samples']
        item['webui'] = dict(samples=len(states), audio_active=sum(s.get('audio') is True for s in states),
                            ranges=ranges(states, ('request_ms', 'rssi')) if states else {})
    return result


def inspect(folder):
    paths = [folder/name for name in ('report.json', 'status.json', 'performance.json')]
    result = summarize(*(json.loads(p.read_text(encoding='utf-8')) for p in paths))
    result['input_sha256'] = {p.name: sha(p.read_bytes()) for p in paths}
    result['source_sha256'] = {p.name: sha(p.read_bytes()) for p in
                             (Path(__file__), Path(__file__).with_name('network_memory.py'))}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.input)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    for case in result['cases']:
        print(case['name'], case['acceptance']['result'], 'issues=', case['issues'])
