"""Describe short EOF test windows without replacing their original verdicts.

Decoder timing records describe completed profiling windows, not every sample
or physical DMA continuity. A short run is not sustained CPU qualification.
"""
import argparse
import json
from pathlib import Path
import re
from summarize_sustained import read, gate
from public_streams import no_runtime_faults


def summarize(folder):
    report, status, rows = (read(folder,n) for n in ('report.json','status.json','performance.json'))
    cases = {c['name']:c for c in report['cases']}
    streams = []
    for index, batch in enumerate(status):
        if not batch['case'].endswith(':playing'):
            continue
        prefix = batch['case'][:-len('playing')]
        # Include its EOF observation when present. On HTTP failure there may
        # be no EOF batch; leave that shorter interval and the FAIL intact.
        end = batch['ended_at']
        if index + 1 < len(status) and status[index + 1]['case'] == prefix+'eof':
            end = status[index + 1]['ended_at']
        records = [r for r in rows if batch['started_at'] <= r['at'] <= end]
        timing = []
        for row in records:
            match = re.search(r'PERF FLAC: window (\d+) ms, audio (\d+) ms, decode (\d+) ms.*max (\d+) us',row['line'])
            if match:
                timing.append(tuple(map(int,match.groups())))
        item = dict(name=prefix[:-1],original=cases[prefix+'play-to-eof'],
                    start=batch['started_at'],end=end,
                    runtime=gate(lambda:no_runtime_faults(records)),
                    decoder_windows=len(timing),
                    timing_records=[r for r in records if 'PERF FLAC:' in r['line']])
        if timing:
            item['diagnostic'] = dict(decode_percent=100*sum(t[2] for t in timing)/sum(t[1] for t in timing),
                audio_wall_ratio=sum(t[1] for t in timing)/sum(t[0] for t in timing),
                maximum_decode_call_us=max(t[3] for t in timing))
        streams.append(item)
    return dict(board=report['board'],streams=streams,
                runtime=gate(lambda:no_runtime_faults(rows)),
                note='Short-window diagnostics only. Original failures retained; no acoustic or sustained-load qualification.')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=summarize(args.input)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    for row in result['streams']:
        print(row['name'],row['original']['result'],row.get('diagnostic',{}))
