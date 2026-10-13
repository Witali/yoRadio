"""Summarize CPU only inside each recorded public-playback window.

The older checkpoint-only summarizer can include the next station when a test
ends early. Retain it for historical reports; use this runner for new evidence.
"""
import argparse
import json
from pathlib import Path
import re
import statistics
from common import sha


def summarize(report, status, rows):
    result = dict(board=report['board'], cases=[],
        metric='FreeRTOS CPU samples 5..35 s after first PCM, clipped to the recorded playback window',
        note='Failed playback stays failed. Fewer than four in-window CPU samples give no aggregate.')
    previous_end = float('-inf')
    for case in report['cases']:
        if not case['name'].startswith(('http:', 'https:')):
            continue
        protocol, name = case['name'].split(':', 1)
        window = report.get('windows', {}).get(name)
        item = dict(name=name, transport=protocol, acceptance=case, metrics_available=False,
            observed_formats=sorted({s['format'] for batch in status if batch['case'] == name
                                      for s in batch['samples'] if s.get('audio')}),
            samples=[], busy_mean=None, decode_mean=None, minimum_free=None, minimum_largest=None)
        result['cases'].append(item)
        if not window or 'end' not in window:
            item['metrics_reason'] = 'Missing completed playback window'
            continue
        if not previous_end <= window['start'] <= window['end']:
            raise ValueError('Overlapping or reversed playback windows')
        previous_end = window['end']
        subset = [r for r in rows if window['start'] <= r['at'] < window['end']]
        item['window'] = window
        item['allocation_failures'] = [r for r in subset if 'allocation failed' in r['line']]
        starts = [r['at'] for r in subset if 'Memory after first ' in r['line']]
        if len(starts) != 1:
            item['metrics_reason'] = 'Expected one in-window first-PCM checkpoint'
            continue
        start = starts[0]
        for row in subset:
            if not start + 5 <= row['at'] <= start + 35:
                continue
            m = re.search(r'PERF CPU: busy=([\d.]+)%.*decode=([\d.]+)%.*heap=(\d+) largest=(\d+)', row['line'])
            if m:
                value = dict(at=row['at'], busy=float(m[1]), decode=float(m[2]),
                             heap=int(m[3]), largest=int(m[4]))
                if not 0 <= value['decode'] <= value['busy'] <= 100 or not 0 <= value['largest'] <= value['heap']:
                    raise ValueError('Invalid CPU/heap sample')
                item['samples'].append(value)
        samples = item['samples']
        if len(samples) < 4:
            item['metrics_reason'] = 'Fewer than four in-window CPU samples'
            continue
        item.update(metrics_available=True,
            busy_mean=round(statistics.mean(s['busy'] for s in samples), 3),
            decode_mean=round(statistics.mean(s['decode'] for s in samples), 3),
            minimum_free=min(s['heap'] for s in samples), minimum_largest=min(s['largest'] for s in samples))
    if any(c['acceptance']['result'] == 'PASS' and not c['metrics_available'] for c in result['cases']):
        raise ValueError('Passing playback lacks bounded CPU evidence')
    result['panic_or_capture_errors'] = [r for r in rows if re.search(
        r'assert failed|Guru Meditation|CORRUPT HEAP|PANIC registers:|serial capture interrupted', r['line'])]
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
    result = inspect(args.input)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    for c in result['cases']:
        print(c['name'], c['acceptance']['result'], c['busy_mean'], c['minimum_free'], c['minimum_largest'])
