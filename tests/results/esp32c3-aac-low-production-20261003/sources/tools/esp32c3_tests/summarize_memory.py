"""Summarize retained FreeRTOS CPU/stack logs without controlling a board."""
import argparse
import json
from pathlib import Path
import re
import statistics


def summarize(report, status, rows):
    all_cases = [x for x in report['cases'] if x['name'].startswith('memory-playback:')]
    observed = {b['case'] for b in status if any(
        s.get('audio') and s.get('pcm_sample_rate') for s in b['samples'])}
    cases = [x for x in all_cases if x['name'].removeprefix('memory-playback:') in observed]
    starts = [x for x in rows if 'Memory after first ' in x['line']]
    if not cases or len(starts) != len(cases):
        raise ValueError('Cannot unambiguously pair PCM checkpoints with observed cases')
    out = dict(board=report['board'],
        metric='FreeRTOS task runtime; mean of samples 5..35 s after first PCM checkpoint',
        cases=[], minimum_stack_free={}, no_pcm=[x['name'] for x in all_cases if x not in cases])
    for case, start in zip(cases, starts):
        samples = []
        for row in rows:
            if not start['at'] + 5 <= row['at'] <= start['at'] + 35:
                continue
            match = re.search(r'PERF CPU: busy=([\d.]+)%.*decode=([\d.]+)%.*heap=(\d+) largest=(\d+)', row['line'])
            if match:
                values = dict(busy=float(match[1]), decode=float(match[2]),
                              heap=int(match[3]), largest=int(match[4]))
                if not 0 <= values['decode'] <= values['busy'] <= 100 or values['largest'] > values['heap']:
                    raise ValueError('Invalid runtime-counter or heap sample')
                samples.append(values)
        if len(samples) < 4:
            raise ValueError('Insufficient CPU samples: ' + case['name'])
        out['cases'].append(dict(name=case['name'], playback_result=case['result'],
            busy_mean=round(statistics.mean(s['busy'] for s in samples), 3),
            decode_mean=round(statistics.mean(s['decode'] for s in samples), 3),
            minimum_free=min(s['heap'] for s in samples),
            minimum_largest=min(s['largest'] for s in samples), samples=samples))
    for row in rows:
        match = re.search(r'PERF STACK: name=(\S+) minimum_free=(\d+)', row['line'])
        if match:
            name, value = match[1], int(match[2])
            out['minimum_stack_free'][name] = min(out['minimum_stack_free'].get(name, value), value)
    if not out['minimum_stack_free']:
        raise ValueError('Missing stack survey')
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = summarize(*(json.loads((args.input/name).read_text())
        for name in ('report.json', 'status.json', 'performance.json')))
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('Saved', args.output)
