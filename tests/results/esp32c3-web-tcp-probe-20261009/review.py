"""Replay TCP metadata and correlate failed host attempts without inferring delivery."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'sources/tools/esp32c3_tests'))
from public_streams import no_runtime_faults
from staged_dma import parse as dma_parse, summarize as dma_summary
from heap_fragment import analyze as owners

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'review.json')
a=p.parse_args()
folder=ROOT/'physical/web-tcp-probe'
report=json.loads((folder/'report.json').read_text())
rows=json.loads((folder/'performance.json').read_text())
status=json.loads((folder/'status.json').read_text())
requests=[json.loads(line) for line in (folder/'request-phases.jsonl').read_text().splitlines()]
fields=('seq','us','dir','port','flags','before','after','result','pending','dropped')
events=[];listeners=[];issues=[]
for row in rows:
    line=re.sub(r'\x1b\[[0-9;]*m','',row['line'])
    if 'PERF WEB_TCP' in line:
        match=re.search('PERF WEB_TCP: '+' '.join(f'{f}=(-?\\d+)' for f in fields)+'$',line)
        if not match or line.count('PERF ')!=1:
            issues.append(dict(at=row['at'],error='Malformed TCP event'));continue
        event=dict(at=row['at'],**dict(zip(fields,map(int,match.groups()))))
        if event['dropped']:issues.append(dict(at=row['at'],error='Dropped TCP event'))
        if events and event['seq'] != (events[-1]['seq']+1) % 2**32:
            issues.append(dict(at=row['at'],error='Missing or reordered TCP event'))
        events.append(event)
    if 'PERF WEB_LISTEN' in line:
        names=('seq','age_ms','syn_rcvd','established','listeners','backlog','pending','backlog_supported')
        match=re.search('PERF WEB_LISTEN: '+' '.join(f'{f}=(\\d+)' for f in names)+'$',line)
        if not match or line.count('PERF ')!=1:
            issues.append(dict(at=row['at'],error='Malformed listener sample'));continue
        listeners.append(dict(at=row['at'],**dict(zip(names,map(int,match.groups())))))
if not events or not listeners:issues.append(dict(error='Missing TCP/listener telemetry'))
failed=[]
for row in requests:
    if row['phase'] != 'connect' or row['result'] != 'FAIL':continue
    attempts=row.get('socket_attempts',[])
    if not attempts or any(not r.get('local_port') for r in attempts):
        issues.append(dict(error='Failed connection lacks local port',request=row['request']))
    start,end=row['at'],row['at']+row['ms']/1000
    ports={r.get('local_port') for r in attempts}
    associated=[e for e in events if e['port'] in ports and start-1<=e['at']<=end+1]
    samples=[s for s in listeners if start-1<=s['at']<=end+1]
    dma=[s for r in rows if (s:=dma_parse(r)) is not None and start-5<=s['at']<=end+5]
    failed.append(dict(host=row,events=associated,listener_samples=samples,dma_samples=dma,
        rx_syn=sum(e['dir']==0 and bool(e['flags']&2) for e in associated),
        tx_syn=sum(e['dir']==1 and bool(e['flags']&2) for e in associated),
        rx_established=sum(e['dir']==0 and e['after']==4 for e in associated)))
try:no_runtime_faults(rows);runtime=dict(result='PASS')
except AssertionError as error:runtime=dict(result='FAIL',reason=str(error))
region=owners(rows)
result=dict(original_cases=report['cases'],passed=sum(c['result']=='PASS' for c in report['cases']),
    total=len(report['cases']),full_capture_runtime=runtime,
    trace_complete=not issues,trace_issues=issues,tcp_event_count=len(events),listener_sample_count=len(listeners),
    listener_max_age_ms=max((s['age_ms'] for s in listeners),default=None),
    failed_connects=failed,rx_syn=sum(e['dir']==0 and bool(e['flags']&2) for e in events),
    tx_syn=sum(e['dir']==1 and bool(e['flags']&2) for e in events),
    established=sum(e['dir']==0 and e['after']==4 for e in events),
    tx_errors=[e for e in events if e['dir']==1 and e['result']!=0],
    host_connections=sum(r['phase']=='connect' for r in requests),
    max_connect_ms=max(r['ms'] for r in requests if r['phase']=='connect'),
    max_listener_pending=max(s['pending'] for s in listeners),
    max_listener_syn_rcvd=max(s['syn_rcvd'] for s in listeners),
    owner_complete=region['complete'],owner_initial_raw_free=region['snapshots'][0]['largest_raw_free'],
    owner_final_raw_free=region['snapshots'][-1]['largest_raw_free'],owner_final_live=region['snapshots'][-1]['live'],
    records=[],input_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
                            for name in ('report.json','performance.json','status.json','request-phases.jsonl')})
for batch in status:
    if not batch['case'].startswith('tls-record:'):continue
    try:delta=dma_summary(rows,batch['started_at']+10,batch['ended_at'])
    except ValueError as error:delta=dict(result='FAIL',reason=str(error))
    result['records'].append(dict(case=batch['case'],interrupted=batch.get('interrupted',False),
        start=batch['started_at'],end=batch['ended_at'],dma=delta,
        tcp_trace_issues=[i for i in issues if 'at' not in i or batch['started_at']<=i['at']<=batch['ended_at']]))
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('original_cases','input_sha256')},indent=2))
