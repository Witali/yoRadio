"""Replay full load/soak windows and five-minute subwindows; preserve every FAIL.

Unlike an early 30-second diagnostic average, this summarizes all steady-state
samples. It never replaces the original physical suite acceptance outcome.
"""
import argparse
import gzip
import json
from pathlib import Path
import re
import statistics
from common import check_cpu
from public_streams import no_runtime_faults


def read(folder,name):
    path=folder/name
    data=path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes())
    return json.loads(data)


def gate(function):
    try:
        value=function()
        return dict(result='PASS',evidence=value)
    except AssertionError as error:
        return dict(result='FAIL',reason=str(error))


def window(rows,start,end,max_busy=85):
    subset=[r for r in rows if start <= r['at'] <= end]
    cpu=[];decode=[];malformed=[]
    for row in subset:
        if 'PERF CPU:' in row['line']:
            fields={k:float(v) for k,v in re.findall(r'(busy|idle|heap|largest)=([\d.]+)',row['line'])}
            if set(fields)!={'busy','idle','heap','largest'}:
                malformed.append(row);continue
            cpu.append(fields)
        match=re.search(r'PERF (?:AAC|MP3|FLAC|OGG): window (\d+) ms, audio (\d+) ms, decode (\d+) ms',row['line'])
        if match:decode.append(tuple(map(int,match.groups())))
    result=dict(start=start,end=end,seconds=end-start,strict=gate(lambda:check_cpu(subset,max_busy=max_busy,start=start,end=end)),
        cpu_samples=len(cpu),decoder_windows=len(decode),malformed=malformed)
    if cpu and decode:
        result['diagnostic']=dict(mean_busy=statistics.mean(c['busy'] for c in cpu),
            peak_busy=max(c['busy'] for c in cpu),minimum_heap=min(c['heap'] for c in cpu),
            minimum_largest=min(c['largest'] for c in cpu),
            first_heap=statistics.median(c['heap'] for c in cpu[:3]),last_heap=statistics.median(c['heap'] for c in cpu[-3:]),
            first_largest=statistics.median(c['largest'] for c in cpu[:3]),last_largest=statistics.median(c['largest'] for c in cpu[-3:]),
            audio_wall_ratio=sum(d[1] for d in decode)/sum(d[0] for d in decode),
            decode_percent=sum(d[2] for d in decode)*100/sum(d[1] for d in decode))
    return result


def summarize(folder):
    report,status,rows=(read(folder,n) for n in ('report.json','status.json','performance.json'))
    budget=report.get('cpu_budget_percent',85)
    result=dict(board=report['board'],cases=[],note='Original outcomes retained. Diagnostic means do not override failed gates.')
    for batch in status:
        if not batch['case'].startswith(('load:','soak:')):continue
        kind,name=batch['case'].split(':',1)
        case_name=('cpu-under-http-load:' if kind=='load' else 'soak:')+name
        original=next(c for c in report['cases'] if c['name']==case_name)
        start,end=batch['started_at'],batch['ended_at']
        item=dict(name=name,original=original,full_window=window(rows,start+10,end,budget),
            runtime=gate(lambda:no_runtime_faults([r for r in rows if start <= r['at'] <= end])),subwindows=[],
            status_samples=len(batch['samples']),max_http_ms=max(s['request_ms'] for s in batch['samples']),
            minimum_rssi=min(s['rssi'] for s in batch['samples']))
        result['cases'].append(item)
        cursor=start+10
        while end-cursor>=30:
            stop=min(cursor+300,end)
            item['subwindows'].append(window(rows,cursor,stop,budget));cursor=stop
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=summarize(args.input)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    for case in result['cases']:print(case['name'],case['original']['result'],case['full_window'])
