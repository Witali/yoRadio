import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
sys.path.insert(0, str(Path('tools/esp32c3_tests').resolve()))
from network_memory import parse_receive_snapshot, ranges, summarize as network_summary
from summarize_radio_flac import cpu_intervals, cpu_summary

root = Path('.build/c3-rxonly-physical-20261008/long')
result = dict(note='Complete CPU/decoder intervals after 10 seconds. Original gates retained. '
                   'TCP credit is logical payload, not allocated RAM; no acoustic qualification.', cases=[])
for name in ('output8-aac-alternate-600', 'rxonly-aac-alternate-600', 'rxonly-flac-https-600'):
    folder = root/name
    paths = {key:folder/(key+'.json') for key in ('report','status','performance')}
    data = {key:json.loads(path.read_text()) for key,path in paths.items()}
    batch = next(b for b in data['status'] if b['case'].startswith(('load:', 'tls-record:')))
    start, end = batch['started_at']+10, batch['ended_at']
    rows = data['performance']
    windows, malformed, gaps = cpu_intervals(rows,start,end)
    decoder = []
    for row in rows:
        match = re.search(r'PERF (?:AAC|FLAC): window (\d+) ms, audio (\d+) ms, decode (\d+) ms', row['line'])
        if match:
            wall, audio, decode = map(int,match.groups())
            if start <= row['at']-wall/1000 and row['at'] <= end:
                decoder.append(dict(wall=wall,audio=audio,decode=decode))
    wall = sum(d['wall'] for d in decoder)
    decoded = sum(d['audio'] for d in decoder)
    heap = []
    for row in rows:
        if start <= row['at'] <= end and 'PERF CPU:' in row['line']:
            values = {key:int(value) for key,value in re.findall(r'\b(heap|largest)=(\d+)',row['line'])}
            assert set(values)=={'heap','largest'}
            heap.append(values)
    original = data['report']['cases']
    network = network_summary(dict(cases=[dict(name='https:'+name,result='DIAGNOSTIC')],
        windows={name:dict(start=batch['started_at'],end=end)}),
        [dict(case=name,samples=batch['samples'])],rows)['cases'][0]
    credit = [s for row in rows if (s:=parse_receive_snapshot(row)) is not None
              and batch['started_at'] <= s['sample_at'] < end]
    requests = [json.loads(line) for line in (root/(name+'-request-phases.jsonl')).read_text().splitlines()]
    item = dict(name=name,image=data['report']['board']['app_elf_sha256'],
        original_acceptance=original,interrupted=batch.get('interrupted',False),
        seconds=end-batch['started_at'],cpu=cpu_summary(windows),cpu_malformed=malformed,cpu_gaps=gaps,
        decoder_windows=len(decoder),audio_wall_ratio=decoded/wall if wall else None,
        elapsed_decode_ms_per_audio_second=sum(d['decode'] for d in decoder)*1000/decoded if decoded else None,
        heap=ranges(heap,('heap','largest')),
        network_metrics_available=network['metrics_available'],network_issues=network['issues'],
        receive_credit=ranges(credit,('uncredited','refused')),
        watchdog_counter_max=max((int(match[1]) for row in rows
            if (match:=re.search(r'Runtime watchdog timeout: task_watchdog=true events=(\d+)',row['line']))), default=0),
        watchdog_fault_rows=sum('task_watchdog=true' in row['line'] for row in rows),
        allocation_fault_rows=[row for row in rows if re.search(r'alloc(?:ation)? failed|memory lack|CORRUPT HEAP',row['line'],re.I)],
        maximum_http_ms=max(s['request_ms'] for s in batch['samples']),
        minimum_rssi=min(s['rssi'] for s in batch['samples']),
        failed_transport_phases=[r for r in requests if r['result']!='PASS'],
        hashes={key:hashlib.sha256(path.read_bytes()).hexdigest() for key,path in paths.items()})
    result['cases'].append(item)
result['restoration']=json.loads((root/'final-board.json').read_text())
(root/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
for item in result['cases']:
    print(item['name'],json.dumps({k:item[k] for k in ('cpu','audio_wall_ratio','heap','watchdog_counter_max','maximum_http_ms','minimum_rssi','network_metrics_available')}))
    print('gates',[(c['name'],c['result'],c.get('reason')) for c in item['original_acceptance']])
print('restore',result['restoration']['result'])
