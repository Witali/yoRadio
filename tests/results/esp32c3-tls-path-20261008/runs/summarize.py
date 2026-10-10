"""Compare complete recorded windows; keep original gates and missing evidence."""
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
sys.path.insert(0, str(Path('tools/esp32c3_tests').resolve()))
from summarize_radio_flac import cpu_intervals, cpu_summary
from staged_dma import summarize as dma_summary

root = Path('.build/c3-tls-path-20261008')
cases = []
for variant, base in (('baseline', Path('.build/c3-staged-dma-profile-20261008/physical')),
                      ('tlspath', root/'physical'), ('tlspath-repeat', root/'physical-aac-repeat')):
    for case in ('flac-https-60', 'aac-alternate-90'):
        paths = {name:base/case/(name+'.json') for name in ('report','status','performance')}
        if not all(p.exists() for p in paths.values()):
            continue
        data = {name:json.loads(p.read_text()) for name,p in paths.items()}
        batch = next(b for b in data['status'] if b['case'].startswith(('load:', 'tls-record:')))
        start, end = batch['started_at']+10, batch['ended_at']
        rows = data['performance']
        cpu, malformed, gaps = cpu_intervals(rows, start, end)
        decoder = []
        for row in rows:
            match = re.search(r'PERF (?:AAC|FLAC): window (\d+) ms, audio (\d+) ms, decode (\d+) ms', row['line'])
            if match:
                wall, audio, decode = map(int,match.groups())
                if start <= row['at']-wall/1000 and row['at'] <= end:
                    decoder.append(dict(wall=wall,audio=audio,decode=decode))
        heap = []
        for row in rows:
            if start <= row['at'] <= end and 'PERF CPU:' in row['line']:
                values = {key:int(value) for key,value in re.findall(r'\b(heap|largest)=(\d+)',row['line'])}
                assert set(values)=={'heap','largest'}
                heap.append(values)
        dma = dma_summary(rows,start,end)
        # The native PDM path writes stereo s16 at fixed 48 kHz.
        dma['written_audio_wall_ratio'] = dma['delta']['written_bytes']/(48000*2*2*dma['observed_seconds'])
        dma['overruns_per_second'] = dma['delta']['q_overruns']/dma['observed_seconds']
        watchdog = [row for row in rows if 'Runtime watchdog timeout: task_watchdog=true' in row['line']]
        item = dict(variant=variant,case=case,board=data['report']['board'],
            original_acceptance=data['report']['cases'],interrupted=batch.get('interrupted',False),
            duration_seconds=end-batch['started_at'],warmup_seconds=10,
            cpu=cpu_summary(cpu),cpu_malformed=malformed,cpu_gaps=gaps,decoder_windows=len(decoder),
            decoded_audio_wall_ratio=sum(d['audio'] for d in decoder)/sum(d['wall'] for d in decoder),
            dma=dma,heap={k:dict(min=min(r[k] for r in heap),median=statistics.median(r[k] for r in heap))
                         for k in ('heap','largest')},
            # The capture appends one synthetic line for each newly observed watchdog counter update.
            # Keep the exact rows too; absolute counters can carry over from the preceding case.
            watchdog_new_fault_rows=len(watchdog),watchdog_rows=watchdog,
            minimum_rssi=min(s['rssi'] for s in batch['samples']),
            median_rssi=statistics.median(s['rssi'] for s in batch['samples']),
            maximum_http_ms=max(s['request_ms'] for s in batch['samples']),
            allocation_fault_rows=[r for r in rows if re.search(r'alloc(?:ation)? failed|memory lack|CORRUPT HEAP',r['line'],re.I)],
            hashes={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in paths.items()})
        stack = {}
        for row in rows:
            m = re.search(r'PERF STACK: name=(\S+) minimum_free=(\d+)', row['line'])
            if m:
                stack[m[1]] = min(stack.get(m[1], 1<<30), int(m[2]))
        item['minimum_free_stack_bytes'] = stack
        cases.append(item)
        print(variant,case,'busy',round(item['cpu']['busy_mean_percent'],3),
            'decoded',round(item['decoded_audio_wall_ratio'],6),
            'written',round(dma['written_audio_wall_ratio'],6),
            'overruns',dma['delta']['q_overruns'],'seconds',round(dma['observed_seconds'],3),
            'watchdog rows',len(watchdog),flush=True)
result = dict(complete=len(cases)==5,cases=cases,note=(
    'Optional inclusive TLS path wall-time instrumentation; unchanged 1 ms tick. Original runtime/heap gates retained. '
    'CPU and decoder results use complete intervals after warmup. DMA ratios use '
    'actual written bytes between selected counter samples, not audible-gap counts. '
    'Watchdog rows count newly observed fault updates, not an assumption that absolute counters reset.'))
(root/'summary.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
