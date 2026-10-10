"""Replay compact TCP integrity, failed connections, DMA and heap recovery."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'sources/tools/esp32c3_tests'))
from web_tcp import parse, window
from public_streams import no_runtime_faults
from staged_dma import summarize as dma_summary
from heap_fragment import analyze as owners

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'review.json')
a=p.parse_args()
folder=ROOT/'physical/web-tcp-v2'
report=json.loads((folder/'report.json').read_text())
rows=json.loads((folder/'performance.json').read_text())
status=json.loads((folder/'status.json').read_text())
requests=[json.loads(line) for line in (folder/'request-phases.jsonl').read_text().splitlines()]
frames=[]; malformed=[]
for row in rows:
    try:
        if (value:=parse(row)) is not None:frames.append(value)
    except ValueError as error:malformed.append(dict(at=row['at'],error=str(error)))
events=[f for f in frames if f['kind']=='event']
listeners=[f for f in frames if f['kind']=='listener']
marks=[f for f in frames if f['kind']=='watermark']

def qualify(start,end):
    try:
        v=window(rows,start,end)
        return dict(result='PASS',start=v['start'],end=v['end'],events=len(v['events']),
                    listeners=len(v['listeners']),watermarks=len(v['watermarks']),
                    first_edge_seconds=v['first_edge_seconds'],last_edge_seconds=v['last_edge_seconds'])
    except ValueError as error:return dict(result='FAIL',reason=str(error))

connections=[r for r in requests if r['phase']=='connect']
failures=[]
for r in connections:
    if r['result']=='PASS':continue
    start,end=r['at'],r['at']+r['ms']/1000
    ports={s.get('local_port') for s in r.get('socket_attempts',[])}
    # Extra anchors bracket both ends; absence of a packet is meaningful only
    # if this local interval passes integrity and actually spans the attempt.
    q=qualify(start-3,end+3)
    spans=q['result']=='PASS' and q['start']<=start and q['end']>=end
    selected=[f for f in events if f['port'] in ports and start-1<=f['at']<=end+1]
    failures.append(dict(host=r,trace=q,trace_spans_attempt=spans,events=selected,
        listener_samples=[s for s in listeners if start-1<=s['at']<=end+1]))
try:no_runtime_faults(rows);runtime=dict(result='PASS')
except AssertionError as error:runtime=dict(result='FAIL',reason=str(error))
region=owners(rows)
result=dict(passed=sum(c['result']=='PASS' for c in report['cases']),total=len(report['cases']),
    original_cases=report['cases'],full_capture_runtime=runtime,crc_frames=len(frames),malformed=malformed,
    event_count=len(events),watermark_count=len(marks),listener_count=len(listeners),
    listener_max_age_ms=max((s['age_ms'] for s in listeners),default=None),
    max_pending=max((s['pending'] for s in listeners),default=None),
    ring_drops=max((s.get('dropped',0) for s in frames),default=None),
    host_connections=len(connections),max_connect_ms=max((r['ms'] for r in connections),default=None),
    failed_connects=failures,tx_errors=[e for e in events if e['dir']==1 and e['result']!=0],
    owner_complete=region['complete'],owner_initial_raw_free=region['snapshots'][0]['largest_raw_free'],
    owner_final_raw_free=region['snapshots'][-1]['largest_raw_free'],owner_final_live=region['snapshots'][-1]['live'],
    records=[],phase_integrity={r['name']:qualify(r['started_at'],r['ended_at']) for r in report['actions']
        if r['ended_at']-r['started_at']>=5},
    input_sha256={n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in
                  ('report.json','performance.json','status.json','request-phases.jsonl')})
for batch in status:
    if not batch['case'].startswith('tls-record:'):continue
    try:delta=dma_summary(rows,batch['started_at']+10,batch['ended_at'])
    except ValueError as error:delta=dict(result='FAIL',reason=str(error))
    result['records'].append(dict(case=batch['case'],interrupted=batch.get('interrupted',False),
        start=batch['started_at'],end=batch['ended_at'],dma=delta,
        tcp=qualify(batch['started_at'],batch['ended_at'])))
if (folder/'tcp-records.json').is_file():
    batch=next(b for b in status if b['case']=='tls-record:grow')
    assert json.loads((folder/'tcp-records.json').read_text())==window(rows,batch['started_at'],batch['ended_at'])
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('original_cases','input_sha256')},indent=2))
