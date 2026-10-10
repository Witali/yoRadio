"""Bracket DMA events using saved host times; never infer acoustic gap counts."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'sources/tools/esp32c3_tests'))
from staged_dma import parse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'events.json')
    args = parser.parse_args()
    folder = ROOT/'physical/tls-record-grow'
    rows = json.loads((folder/'performance.json').read_text())
    batch = next(b for b in json.loads((folder/'status.json').read_text())
                 if b['case'] == 'tls-record:grow')
    start, end = batch['started_at'], batch['ended_at']
    dma = [v for row in rows if (v := parse(row)) and start <= v['at'] <= end]
    events = []
    for previous, current in zip(dma, dma[1:]):
        delta = current['q_overruns'] - previous['q_overruns']
        assert delta >= 0 and current['at'] > previous['at']
        if not delta:
            continue
        # Different task reports have independently aligned ~5 s windows.
        # Include every overlapping complete flow window and keep raw rows.
        overlaps = {}
        for kind in ('DEC', 'STAGED_OUT'):
            selected = []
            for row in rows:
                if 'PERF FLOW_'+kind+':' not in row['line']:
                    continue
                values = {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)\b', row['line'])}
                left = row['at'] - values['window_us']/1e6
                if left < current['at'] and row['at'] > previous['at']:
                    selected.append(dict(start=left-start, end=row['at']-start,
                                         values=values, row=row))
            overlaps[kind] = selected
        events.append(dict(start=previous['at']-start, end=current['at']-start,
                           events=delta, flow=overlaps))
    result = dict(events=events, total=sum(e['events'] for e in events),
        observation_seconds=end-start,
        nominal_clock_extra_audio_seconds=(end-start)/624,
        note='Counter brackets and overlapping task windows are not exact event times or proof of causality. '
             'Integer clock 625000/13 versus resampler target 48000 consumes 1/624 extra audio seconds per second. '
             'No analog continuity, exact network arrival times, or initial buffered duration is measured.')
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    for e in events:
        print(json.dumps(dict(start=round(e['start'],3),end=round(e['end'],3),events=e['events'],
            decoder=[{k:w['values'][k] for k in ('input_us','input_max','input_timeouts')} for w in e['flow']['DEC']],
            output=[{k:w['values'][k] for k in ('empty_us','empty_max','empty_timeouts','overruns')} for w in e['flow']['STAGED_OUT']])))
    print('events:', result['total'])


if __name__ == '__main__':
    main()
