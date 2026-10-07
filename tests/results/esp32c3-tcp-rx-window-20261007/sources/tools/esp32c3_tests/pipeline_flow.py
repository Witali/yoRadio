"""Summarize complete queue-wait windows; never add overlapping task times."""
import argparse
import json
from pathlib import Path
import re

from summarize_radio_flac import cpu_intervals, cpu_summary, decode_summary

FIELDS = {
    'DEC': ('input', 'pcm'),
    'OUT': ('empty', 'submit', 'dma'),
}


def flow_summary(rows, start, end, kind):
    windows, malformed = [], []
    for row in rows:
        if f'PERF FLOW_{kind}:' not in row['line']:
            continue
        values = {key: int(value) for key, value in re.findall(r'(\w+)=(\d+)\b', row['line'])}
        required = ['gen', 'window_us']
        for field in FIELDS[kind]:
            required += [field+'_us', field+'_n', field+'_max']
            if field != 'submit':
                required += [field+'_timeouts']
        if kind == 'OUT':
            required += ['overruns']
        if not all(k in values for k in required) or not values.get('window_us'):
            if start <= row['at'] <= end:
                malformed.append(row)
            continue
        duration = values['window_us']/1e6
        if row['at']-duration < start or row['at'] > end:
            continue
        if any(values[f+'_us'] > values['window_us'] or
               values[f+'_max'] > values[f+'_us'] or
               values.get(f+'_timeouts', 0) > values[f+'_n'] for f in FIELDS[kind]):
            malformed.append(row)
            continue
        windows.append(values)
    total = sum(w['window_us'] for w in windows)
    result = dict(windows=windows, malformed=malformed, observed_seconds=total/1e6)
    if not total:
        return result
    for field in FIELDS[kind]:
        us = sum(w[field+'_us'] for w in windows)
        count = sum(w[field+'_n'] for w in windows)
        result[field] = dict(us=us, count=count, wall_percent=100*us/total,
            mean_us=us/count if count else 0,
            max_us=max(w[field+'_max'] for w in windows),
            timeouts=sum(w.get(field+'_timeouts', 0) for w in windows))
    if kind == 'OUT':
        result['overruns'] = sum(w['overruns'] for w in windows)
        result['overruns_per_second'] = result['overruns']/(total/1e6)
    return result


def summarize(directory):
    rows = json.loads((directory/'performance.json').read_text())
    cases = []
    for batch in json.loads((directory/'status.json').read_text()):
        if not batch['case'].startswith(('load:', 'input-jitter:')):
            continue
        start, end = batch['started_at']+10, batch['ended_at']
        cpu, malformed, gaps = cpu_intervals(rows, start, end)
        cases.append(dict(name=batch['case'],
            cpu=cpu_summary(cpu), cpu_malformed=malformed, cpu_gaps=gaps,
            decoder=decode_summary(rows, start, end),
            flow_decoder=flow_summary(rows, start, end, 'DEC'),
            flow_output=flow_summary(rows, start, end, 'OUT')))
    return dict(cases=cases, warmup_seconds=10,
        note='Wall time includes scheduling. Task windows overlap; do not sum waits as CPU load. '
             'DMA overruns are discarded completion notifications, not an exact count of audible gaps.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = summarize(args.results)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    for case in result['cases']:
        print(case['name'], json.dumps({
            'cpu': case['cpu'].get('busy_mean_percent'),
            'audio_wall': case['decoder']['audio_wall_ratio'],
            'input': case['flow_decoder'].get('input'),
            'pcm_full': case['flow_decoder'].get('pcm'),
            'pcm_empty': case['flow_output'].get('empty'),
            'dma_wait': case['flow_output'].get('dma'),
            'dma_overruns': case['flow_output'].get('overruns')}))


if __name__ == '__main__':
    main()
