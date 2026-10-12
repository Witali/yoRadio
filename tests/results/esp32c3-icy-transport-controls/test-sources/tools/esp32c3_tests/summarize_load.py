"""Summarize CPU/heap for load cases, including failures; never change outcomes.

Uses the memory survey's fixed 5..35 s window after the first PCM checkpoint.
This diagnostic window is distinct from the load suite's acceptance window.
"""
import argparse
import json
from pathlib import Path

from summarize_memory import summarize


def summarize_load(report, status, rows):
    prefix = 'cpu-under-http-load:'
    mapped = dict(report, cases=[dict(case, name='memory-playback:'+case['name'][len(prefix):])
                  for case in report['cases'] if case['name'].startswith(prefix)])
    mapped_status = [dict(batch, case=batch['case'].removeprefix('load:')) for batch in status]
    result = summarize(mapped, mapped_status, rows)
    result['note'] = ('Diagnostic window only; original load PASS/FAIL outcomes are retained. '
                      'Do not use these samples to replace the stricter acceptance checks.')
    for case in result['cases']:
        case['name'] = prefix+case['name'].removeprefix('memory-playback:')
        case['peak_busy'] = max(sample['busy'] for sample in case['samples'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = summarize_load(*(json.loads((args.input/name).read_text())
                             for name in ('report.json', 'status.json', 'performance.json')))
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print('Saved', args.output)
