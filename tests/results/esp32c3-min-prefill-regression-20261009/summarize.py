"""Replay minimum-prefill regression, retaining original and extended verdicts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
SOURCES=ROOT/'sources'
sys.path.insert(0,str(SOURCES/'tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap, check_transitions
from audio_test_server.fixtures import SEQUENCES
from staged_dma import parse as parse_dma
from flow_windows import helper, strict_flow
from short_summary import summarize as short_summary

PHASES=('short-pcm-tails','matrix-http','matrix-https','heavy-flac',
        'transitions-faults-websocket','switch-all','eof-http')
FAULT=re.compile(r'allocation failed|decode (?:error|failed)|TLS failure:|assert failed|'
    r'Guru Meditation|CORRUPT HEAP|PANIC|serial capture interrupted|'
    r'Runtime watchdog timeout|PERF watchdog: task_timeouts=[1-9][0-9]*\b|'
    r'task_wdt: Task watchdog got triggered|^(?:ESP-ROM:|rst:|waiting for download)')
PREFILL=re.compile(r'PERF INPUT_PREFILL: generation=(\d+) elapsed_ms=(\d+) full=([01]) cancelled=([01])$')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def verdict(name, check):
    try:
        evidence=check()
        return dict(name=name,result='PASS',evidence=evidence)
    except (AssertionError,ValueError,IndexError,KeyError,StopIteration) as error:
        return dict(name=name,result='FAIL',reason=str(error))


def eof_evidence(playing, tail, name):
    assert playing['case']==name+':playing' and tail['case']==name+':terminal','Unexpected EOF observation order'
    assert not playing.get('interrupted') and not tail.get('interrupted'),'Interrupted EOF observation; retain the original failure'
    assert any(s['audio'] and s.get('pcm_sample_rate') for s in playing['samples']),'No decoded playback'
    samples=tail['samples']
    stopped=next(i for i,s in enumerate(samples) if not s['audio'])
    assert len(samples)-stopped>=2,'No confirmed stopped state'
    assert all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate']
               and not s['pcm_channels'] for s in samples[stopped:]),'Stale or failed terminal state'
    return dict(terminal_samples=len(samples)-stopped,
                scope='REST samples replayed; WebSocket verdict is original evidence only.')


def switching_evidence(data, folder, catalog):
    stored=json.loads((folder/'switching.json').read_text())
    batches=[b for b in data['status'] if b['case'].startswith('switch:')]
    expected=[f'switch:{cycle}:{name}' for cycle in range(3) for name in catalog]
    assert [b['case'] for b in batches]==expected,'Incomplete switching order'
    results=[verdict(b['case'],lambda b=b:check_playback(b['samples'],catalog[b['case'].split(':',2)[2]])) for b in batches]
    idle=[b for b in data['status'] if b['case']=='settled-idle']
    assert len(idle)==3 and len(stored['checkpoints'])==3
    recovered=[]
    for batch in idle:
        recovered.append([dict(zip(('heap','largest','tasks'),map(int,m.groups())))
            for r in data['performance'] if batch['started_at']<=r['at']<=batch['ended_at']
            and (m:=re.search(r'PERF CPU:.*heap=(\d+) largest=(\d+) tasks=(\d+)',r['line']))])
    assert recovered==stored['checkpoints'],'Idle heap samples differ from serial evidence'
    recovery=verdict('settled-heap-recovery',lambda:check_recovery_heap(recovered[0],recovered[-1]))
    return dict(stations=results,heap=recovery,checkpoints=recovered,original_failures=stored['failures'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'summary.json')
    args=parser.parse_args()
    initial=json.loads((ROOT/'physical/initial.json').read_text())
    path=ROOT/'physical/phases.json'
    completed=json.loads(path.read_text()) if path.is_file() else []
    done={p['name']:p for p in completed}
    catalog=json.loads((ROOT/'case-catalog.json').read_text())
    summary=dict(scope='Original gates plus independent format/EOF/runtime replay. No acoustic capture.',
                 initial=initial,phases={},sustained=[],incomplete=[])
    for name in PHASES:
        if name not in done:
            summary['incomplete'].append(name);continue
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
        item=dict(controller=done[name],board=data['report']['board'],original_acceptance=original,
                  passed=sum(c['result']=='PASS' for c in original),total=len(original),
                  failures=[c for c in original if c['result']!='PASS'],
                  input_sha256=hashes,prefill=prefill,malformed_prefill=malformed,
                  extended_runtime=dict(result='REVIEW_REQUIRED' if issues else 'PASS',rows=issues,
                    note='Does not silently exempt injected faults or intentional Stop; review their context.'))
        cpu_heap=[tuple(map(int,m.groups())) for row in data['performance']
            if (m:=re.search(r'PERF CPU:.*heap=(\d+) largest=(\d+) tasks=(\d+)',row['line']))]
        low_water=[int(m[1]) for row in data['performance']
            if (m:=re.search(r'Memory .*minimum=(\d+)',row['line']))]
        item['whole_phase_memory']=dict(cpu_log_minimum_free=min((r[0] for r in cpu_heap),default=None),
            cpu_log_minimum_largest=min((r[1] for r in cpu_heap),default=None),
            historical_low_water=min(low_water,default=None),
            note='CPU logs include transitions. Low water is since boot, not necessarily a new minimum in this phase.')
        summary['phases'][name]=item
        trace=ROOT/'physical'/(name+'-request-phases.jsonl')
        if trace.is_file():
            records=[json.loads(line) for line in trace.read_text().splitlines()]
            item['transport']=dict(sha256=sha(trace),failures=[r for r in records if r['result']!='PASS'],
                                   failed_requests=sorted({r['request'] for r in records if r['result']!='PASS'}),
                                   connection_instances=max((r['request'] for r in records),default=0))
        if name=='short-pcm-tails':
            item['submission_replay']=short_summary()
        elif name.startswith('matrix-'):
            protocol=name.removeprefix('matrix-')
            expected=[f'{protocol}:{n}:{hint}' for n,s in catalog.items() for hint in ('auto',s['codec'])]+['restore-board']
            item['expected_cases_match']=[c['name'] for c in original]==expected
            item['fixture_hashes_match']=data['report']['fixture_hashes']=={n:s['sha256'] for n,s in catalog.items()}
            results=[]
            for index,(n,spec) in enumerate((n,s) for n,s in catalog.items() for _ in ('auto','explicit')):
                try:
                    playing,tail=data['status'][index*2:index*2+2]
                    assert playing['case']==n and tail['case']==n+':eof','Unexpected observation order'
                    evidence=check_playback(playing['samples'],spec)
                    assert any(not s['audio'] for s in tail['samples']),'Missing EOF'
                    results.append(dict(name=expected[index],result='PASS',**evidence))
                except (AssertionError,ValueError,IndexError) as error:
                    results.append(dict(name=expected[index],result='FAIL',reason=str(error)))
            item['independent_format_replay']=results
        elif name=='eof-http':
            expected=[f'eof:{n}:{hint}' for n,s in catalog.items() for hint in ('auto',s['codec'])]+['restore-board']
            item['expected_cases_match']=[c['name'] for c in original]==expected
            item['independent_eof_replay']=[verdict(expected[index],lambda i=index,n=n:
                eof_evidence(data['status'][i*2],data['status'][i*2+1],n))
                for index,n in enumerate(n for n in catalog for _ in range(2))]
        elif name=='switch-all':
            item['switch_replay']=verdict('switching',lambda:switching_evidence(data,folder,catalog))
        elif name=='transitions-faults-websocket':
            by_name={b['case']:b for b in data['status']}
            item['transition_replay']=[verdict(n,lambda n=n,seq=seq:
                check_transitions(by_name[n]['samples'],[catalog[f] for f in seq])) for n,seq in SEQUENCES.items()]
            item['recovered_playback_replay']=[verdict(n,lambda n=n:
                check_playback(by_name[n]['samples'],catalog['lc-22050-mono']))
                for n in ('stop-play-generation','recovered:drop','recovered:stall','recovered:error')]
        for batch in data['status']:
            if not batch.get('case','').startswith('load:'):continue
            measured=helper.summarize_batch(name,folder,batch,data,hashes)
            start,end=measured['measured_start'],measured['measured_end']
            measured['flow_decoder']=strict_flow(data['performance'],start,end,'DEC')
            measured['flow_output']=strict_flow(data['performance'],start,end,'STAGED_OUT')
            points=[p for r in data['performance'] if (p:=parse_dma(r)) is not None and batch['started_at']<=p['at']<=end]
            measured['whole_observed_dma_events']=[dict(start=a['at'],end=b['at'],overruns=b['q_overruns']-a['q_overruns'],errors=b['errors']-a['errors']) for a,b in zip(points,points[1:]) if b['q_overruns']!=a['q_overruns'] or b['errors']!=a['errors']]
            measured['continuity_review']=dict(result='REVIEW_REQUIRED' if measured['whole_observed_dma_events'] else 'NO_RECORDED_EVENTS',
                note='Original playback acceptance is retained. Queue events are not an acoustic gap count.')
            summary['sustained'].append(measured)
    for name in ('installed','fractional-clock','phases','settings-after-tests','restoration','controller-failure','restoration-failure'):
        path=ROOT/'physical'/(name+'.json')
        if path.is_file():summary['controller_'+name]=json.loads(path.read_text())
    args.output.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(incomplete=summary['incomplete'],phases={n:dict(passed=p['passed'],total=p['total'],runtime=p['extended_runtime']['result'],failures=[c['name'] for c in p['failures']]) for n,p in summary['phases'].items()},sustained=[dict(cpu=c['cpu'].get('busy_mean_percent'),heap=c.get('heap'),dma=c.get('dma',{}).get('delta'),telemetry=c['telemetry_complete']) for c in summary['sustained']]),indent=2))


if __name__=='__main__':main()
