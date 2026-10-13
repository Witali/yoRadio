"""Preserve load failures and compare every idle checkpoint to the first one."""
import argparse
import json
from pathlib import Path
import re
import statistics

from common import Failure, check_cpu, check_recovery_heap


def observed_performance(rows):
    """Keep measurements even when an acceptance gate rejects the window."""
    cpu = []
    decode = []
    for row in rows:
        match = re.search(r'PERF CPU: busy=([\d.]+)', row['line'])
        if match:
            cpu.append(float(match[1]))
        match = re.search(r'PERF (?:AAC|MP3|FLAC|OGG): window (\d+) ms, audio (\d+) ms, decode (\d+) ms', row['line'])
        if match:
            decode.append(tuple(map(int, match.groups())))
    window_ms = sum(r[0] for r in decode)
    return dict(cpu_windows=len(cpu), decoder_windows=len(decode),
                mean_busy=statistics.mean(cpu) if cpu else None,
                peak_busy=max(cpu) if cpu else None,
                audio_wall_ratio=sum(r[1] for r in decode)/window_ms if window_ms else None)


def summarize(report, status, performance):
    cases={c['name']:c for c in report['cases']}
    names=[n.removeprefix('cpu-under-http-load:') for n in cases if n.startswith('cpu-under-http-load:')]
    idle=[b for b in status if b['case']=='settled-idle']
    if len(idle)!=2*len(names) or not names:raise ValueError('Missing idle observation windows')
    checkpoints=[]
    for window in idle:
        rows=[]
        for row in performance:
            if not window['started_at']<=row['at']<=window['ended_at']:continue
            match=re.search(r'PERF CPU:.*heap=(\d+) largest=(\d+) tasks=(\d+)',row['line'])
            if match:rows.append(dict(zip(('heap','largest','tasks'),map(int,match.groups()))))
        if len(rows)<2:raise ValueError('Incomplete idle heap telemetry')
        checkpoints.append(rows)
    result=dict(image=report['board']['app_elf_sha256'],cases={})
    for index,name in enumerate(names):
        window=next(b for b in status if b['case']=='load:'+name)
        item=result['cases'][name]=dict(original_acceptance=cases['cpu-under-http-load:'+name],
            maximum_http_ms=max(s['request_ms'] for s in window['samples']),
            minimum_rssi=min(s['rssi'] for s in window['samples']),
            idle_after={key:statistics.median(s[key] for s in checkpoints[index*2+1])
                        for key in ('heap','largest','tasks')})
        for label,baseline in [('recovery_from_previous',checkpoints[index*2]),
                                ('recovery_from_first',checkpoints[0])]:
            try:
                check_recovery_heap(baseline,checkpoints[index*2+1])
                item[label]=dict(result='PASS')
            except Failure as error:item[label]=dict(result='FAIL',reason=str(error))
        # Supplementary settled window; never substitutes for the original
        # 10-second-warmup gate retained above. Same CPU/heap limits.
        start,end=window['started_at']+40,window['ended_at']
        rows=[r for r in performance if start<=r['at']<=end]
        item['observed_after_40_seconds']=observed_performance(rows)
        try:item['after_40_seconds']=dict(result='PASS',**check_cpu(rows,
            max_busy=report.get('cpu_budget_percent',85),start=start,end=end))
        except Failure as error:item['after_40_seconds']=dict(result='FAIL',reason=str(error))
    result['scope']='One paced sequence with per-case Stop; no reboot between codecs; not a 100-switch or 30-minute soak qualification'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=summarize(*(json.loads((args.folder/name).read_text())
                     for name in ('report.json','status.json','performance.json')))
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
