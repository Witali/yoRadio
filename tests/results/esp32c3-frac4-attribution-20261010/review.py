"""Replay owner snapshots and correlate failed TCP connects with validated probe frames."""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from heap_fragment import analyze as owners
from web_tcp import parse,window
from public_streams import no_runtime_faults
from staged_dma import summarize as dma_summary

def verdict(fn):
    try:return dict(result='PASS',evidence=fn())
    except (AssertionError,ValueError,KeyError) as error:return dict(result='FAIL',reason=str(error))
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'review.json');a=p.parse_args()
result=dict(phases={},scope='Attribution with additional probes; not a matched production timing or memory-layout comparison.')
initial=json.loads((ROOT/'physical/initial.json').read_text())
for phase in json.loads((ROOT/'physical/phases.json').read_text()):
    label=phase['name'];folder=ROOT/'physical'/label
    report=json.loads((folder/'report.json').read_text());rows=json.loads((folder/'performance.json').read_text())
    status=json.loads((folder/'status.json').read_text())
    assert report['board']['app_elf_sha256']==initial['candidate']['app_elf_sha256']
    assert report['test_sources_sha256']==initial['test_sources_sha256']
    trace=ROOT/'physical'/(label+'-request-phases.jsonl') if label=='hev2-tls-grow' else folder/'request-phases.jsonl'
    requests=[json.loads(s) for s in trace.read_text().splitlines()]
    conns=[r for r in requests if r['phase']=='connect']
    frames=[];bad=[]
    for row in rows:
        try:
            if (f:=parse(row)) is not None:frames.append(f)
        except ValueError as error:bad.append(dict(at=row['at'],reason=str(error)))
    events=[f for f in frames if f['kind']=='event'];listeners=[f for f in frames if f['kind']=='listener']
    event_gaps=[dict(previous=a['seq'],next=b['seq'],previous_at=a['at'],next_at=b['at']) for a,b in zip(events,events[1:]) if b['seq'] != ((a['seq']+1)&0xffffffff)]
    def qualify(start,end):
        v=window(rows,start,end)
        return {k:v[k] for k in ('start','end','first_edge_seconds','last_edge_seconds')} | dict(events=len(v['events']),listeners=len(v['listeners']),watermarks=len(v['watermarks']))
    failures=[]
    for r in conns:
        if r['result']=='PASS':continue
        start=r['at'];end=start+r['ms']/1000
        ports={s.get('local_port') for s in r.get('socket_attempts',[])}
        q=verdict(lambda:qualify(start-3,end+3))
        spans=q['result']=='PASS' and q['evidence']['start']<=start and q['evidence']['end']>=end
        failures.append(dict(host=r,tcp=q,trace_spans_attempt=spans,
            events=[e for e in events if e['port'] in ports and start-1<=e['at']<=end+1],
            listeners=[s for s in listeners if start-1<=s['at']<=end+1]))
    batches=[]
    for b in status:
        if not b['case'].startswith(('tls-record:','load:')):continue
        start,end=b['started_at'],b['ended_at']
        batches.append(dict(case=b['case'],seconds=end-start,interrupted=b.get('interrupted',False),
            tcp=verdict(lambda:qualify(start,end)),dma=verdict(lambda:dma_summary(rows,start,end)),
            dma_after_10_seconds=verdict(lambda:dma_summary(rows,start+10,end))))
    item=dict(controller=phase,passed=sum(c['result']=='PASS' for c in report['cases']),total=len(report['cases']),
        original_cases=report['cases'],runtime=verdict(lambda:no_runtime_faults(rows)),
        owners=verdict(lambda:owners(rows)),observations=batches,frames=len(frames),malformed=bad,
        event_sequence_gaps=event_gaps,max_ring_drops=max((f.get('dropped',0) for f in frames),default=None),
        tx_errors=[e for e in events if e['dir']==1 and e['result']!=0],
        host_connections=len(conns),max_connect_ms=max((r['ms'] for r in conns),default=None),failed_connections=failures,
        input_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in ('report.json','performance.json','status.json')})
    result['phases'][label]=item
restore=ROOT/'physical/restoration.json';result['restoration']=json.loads(restore.read_text()) if restore.exists() else None
a.output.write_text(json.dumps(result,indent=2)+'\n')
for name,item in result['phases'].items():
    own=item['owners'];snap=own.get('evidence',{}).get('snapshots',[])
    print(json.dumps(dict(phase=name,gates=[item['passed'],item['total']],runtime=item['runtime'],
        observations=item['observations'],malformed=item['malformed'],ring_drops=item['max_ring_drops'],
        tx_errors=item['tx_errors'],connections=item['host_connections'],failures=item['failed_connections'],
        owners_result=own['result'],owners_reason=own.get('reason'),
        owner_endpoints=[snap[0],snap[-1]] if snap else [])),flush=True)
