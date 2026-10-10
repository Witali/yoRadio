"""Replay targeted EOF and matched-code FLAC; keep original and extra verdicts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'sources/tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap
from staged_dma import parse as parse_dma
from flow_windows import helper, strict_flow
from eof_replay import verdict, eof_evidence

PHASES=('eof-http','eof-https','flac-control-before','flac-candidate','flac-control-after')
EOF_NAMES=('he-48000-stereo','hev2-44100-stereo')
FAULT=re.compile(r'allocation failed|decode (?:error|failed)|TLS failure:|assert failed|'
    r'Guru Meditation|CORRUPT HEAP|PANIC|serial capture interrupted|'
    r'Runtime watchdog timeout|PERF watchdog: task_timeouts=[1-9][0-9]*\b|'
    r'task_wdt: Task watchdog got triggered|^(?:ESP-ROM:|rst:|waiting for download)')
PREFILL=re.compile(r'PERF INPUT_PREFILL: generation=(\d+) elapsed_ms=(\d+) full=([01]) cancelled=([01])$')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'summary.json')
    args=parser.parse_args()
    initial=json.loads((ROOT/'physical/initial.json').read_text())
    path=ROOT/'physical/phases.json'
    completed=json.loads(path.read_text()) if path.is_file() else []
    done={p['name']:p for p in completed}
    catalog=json.loads((ROOT/'case-catalog.json').read_text())
    summary=dict(scope='Matched firmware implementation and profiling. Retain failed gates. No acoustic capture.',
        initial=initial,phases={},sustained=[],incomplete=[])
    for name in PHASES:
        if name not in done:summary['incomplete'].append(name);continue
        folder=ROOT/'physical'/name
        paths={n:folder/(n+'.json') for n in ('report','status','performance')}
        data={n:json.loads(p.read_text()) for n,p in paths.items()}
        hashes={n:sha(p) for n,p in paths.items()}
        original=data['report']['cases']
        issues=[r for r in data['performance'] if FAULT.search(r['line'])]
        prefill=[];malformed=[]
        for row in data['performance']:
            if 'PERF INPUT_PREFILL:' not in row['line']:continue
            m=PREFILL.search(row['line'])
            if not m or row['line'].count('PERF ')!=1:malformed.append(row);continue
            prefill.append(dict(at=row['at'],**dict(zip(('generation','elapsed_ms','full','cancelled'),map(int,m.groups())))))
        trace=ROOT/'physical'/(name+'-request-phases.jsonl')
        records=[json.loads(line) for line in trace.read_text().splitlines()]
        item=dict(controller=done[name],board=data['report']['board'],original_acceptance=original,
            passed=sum(c['result']=='PASS' for c in original),total=len(original),
            failures=[c for c in original if c['result']!='PASS'],input_sha256=hashes,
            prefill=prefill,malformed_prefill=malformed,
            extended_runtime=dict(result='REVIEW_REQUIRED' if issues else 'PASS',rows=issues),
            transport=dict(sha256=sha(trace),failures=[r for r in records if r['result']!='PASS'],
                failed_requests=sorted({r['request'] for r in records if r['result']!='PASS'}),
                connection_instances=max((r['request'] for r in records),default=0)))
        summary['phases'][name]=item
        if name.startswith('eof-'):
            protocol=name.removeprefix('eof-');prefix='eof:https:' if protocol=='https' else 'eof:'
            expected=[prefix+n+':'+hint for n in EOF_NAMES for hint in ('auto','aac')]+['restore-board']
            item['expected_cases_match']=[r['name'] for r in original]==expected
            item['protocol_match']=data['report']['eof_protocol']==protocol
            item['fixture_hashes_match']=data['report']['fixture_hashes']=={n:catalog[n]['sha256'] for n in EOF_NAMES}
            item['independent_eof_replay']=[verdict(expected[i],lambda i=i,n=n:
                eof_evidence(data['status'][2*i],data['status'][2*i+1],n))
                for i,n in enumerate(n for n in EOF_NAMES for _ in range(2))]
            item['independent_format_replay']=[verdict(expected[i],lambda i=i,n=n:
                check_playback(data['status'][2*i]['samples'],catalog[n]))
                for i,n in enumerate(n for n in EOF_NAMES for _ in range(2))]
        for batch in data['status']:
            if not batch.get('case','').startswith('load:'):continue
            measured=helper.summarize_batch(name,folder,batch,data,hashes)
            start,end=measured['measured_start'],measured['measured_end']
            measured['variant']=done[name]['variant']
            measured['flow_decoder']=strict_flow(data['performance'],start,end,'DEC')
            measured['flow_output']=strict_flow(data['performance'],start,end,'STAGED_OUT')
            points=[p for r in data['performance'] if (p:=parse_dma(r)) is not None and batch['started_at']<=p['at']<=end]
            events=[dict(start=a['at'],end=b['at'],overruns=b['q_overruns']-a['q_overruns'],errors=b['errors']-a['errors'])
                for a,b in zip(points,points[1:]) if b['q_overruns']!=a['q_overruns'] or b['errors']!=a['errors']]
            measured['whole_observed_dma_events']=events
            measured['continuity_review']=dict(result='REVIEW_REQUIRED' if events else 'NO_RECORDED_EVENTS',
                note='Completion-queue events are not an acoustic gap count.')
            deliveries=[e['delivery'] for e in data['report']['tls_events'] if e['fixture']==batch['case'].removeprefix('load:')]
            assert len(deliveries)==1,'Missing or ambiguous FLAC source delivery'
            delivery=deliveries[0]
            assert not delivery['dropped_windows'],'Incomplete delivery timing'
            measured['dma_event_context']=[]
            for e in events:
                windows=[w for w in delivery['windows'] if w['started_at']<e['end'] and w['ended_at']>e['start']]
                measured['dma_event_context'].append(dict(event=e,host_windows=windows,
                    max_host_write_seconds=max((w['max_write_seconds'] for w in windows),default=None),
                    nearby_input=[r for r in measured['flow_decoder']['intervals'] if e['end']<=r['at']<e['end']+2]))
            before=[r for r in original if r['name'].startswith('load-idle-baseline:')]
            after=[r for r in original if r['name'].startswith('load-idle-recovery:')]
            measured['heap_replay']=verdict('idle-recovery',lambda:check_recovery_heap(before[0]['evidence']['samples'],after[0]['evidence']['samples']))
            summary['sustained'].append(measured)
    for path in sorted((ROOT/'physical').glob('*.json')):
        if path.stem!='running':summary['controller_'+path.stem]=json.loads(path.read_text())
    args.output.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(incomplete=summary['incomplete'],phases={n:dict(passed=p['passed'],total=p['total'],
        runtime=p['extended_runtime']['result'],failed_requests=p['transport']['failed_requests']) for n,p in summary['phases'].items()},
        flac=[dict(phase=c['mode'],minimum=c['variant'],cpu=c['cpu']['busy_mean_percent'],
                   dma=c['dma']['delta']['q_overruns'],whole=sum(e['overruns'] for e in c['whole_observed_dma_events']),
                   telemetry=c['telemetry_complete']) for c in summary['sustained']]),indent=2))


if __name__=='__main__':main()
