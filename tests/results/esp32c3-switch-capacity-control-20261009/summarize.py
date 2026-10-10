"""Replay FLAC capacity comparisons without hiding original or extra failures."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
from references import PRIOR, verify_references
verify_references()
sys.path.insert(0,str(PRIOR))
sys.path.insert(0,str(PRIOR/'sources/tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap
from staged_dma import parse as parse_dma
from tls_records import record_evidence
from heap_receive_correlation import paired_metrics
from flow_windows import helper, strict_flow
from eof_replay import verdict, eof_evidence

TRIALS=(('control-1','0'),('expanded-1','4'),('expanded-2','4'),('control-2','0'))
PHASES=tuple(trial+'-'+phase for trial,_ in TRIALS for phase in ('switch','eof','records'))
FAULT=re.compile(r'allocation failed|decode (?:error|failed)|TLS failure:|assert failed|'
    r'Guru Meditation|CORRUPT HEAP|PANIC|serial capture interrupted|'
    r'Runtime watchdog timeout|PERF watchdog: task_timeouts=[1-9][0-9]*\b|'
    r'task_wdt: Task watchdog got triggered|^(?:ESP-ROM:|rst:|waiting for download)')
GROWTH=re.compile(r'PERF FLAC_INPUT: resident=(\d+) minimum=(\d+) limit=(\d+) target=(\d+) capacity=(\d+)$')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'summary.json')
    args=parser.parse_args()
    initial=json.loads((ROOT/'physical/initial.json').read_text())
    completed=json.loads((ROOT/'physical/phases.json').read_text())
    done={p['name']:p for p in completed}
    catalog=json.loads((ROOT/'case-catalog.json').read_text())
    summary=dict(scope='Original verdicts and stricter counter review; no acoustic capture.',
                 initial=initial,phases={},sustained=[],incomplete=[])
    for name in PHASES:
        if name not in done:summary['incomplete'].append(name);continue
        folder=ROOT/'physical'/name
        paths={n:folder/(n+'.json') for n in ('report','status','performance')}
        data={n:json.loads(p.read_text()) for n,p in paths.items()}
        hashes={n:sha(p) for n,p in paths.items()}
        original=data['report']['cases']
        rows=data['performance']
        growth=[];malformed=[]
        for row in rows:
            if 'PERF FLAC_INPUT:' not in row['line']:continue
            m=GROWTH.search(row['line'])
            if not m or row['line'].count('PERF ')!=1:malformed.append(row);continue
            growth.append(dict(at=row['at'],**dict(zip(('resident','minimum','limit','target','capacity'),map(int,m.groups())))))
        issues=[r for r in rows if FAULT.search(r['line'])]
        trace=ROOT/'physical'/(name+'-request-phases.jsonl')
        requests=[json.loads(line) for line in trace.read_text().splitlines()]
        item=dict(controller=done[name],board=data['report']['board'],original_acceptance=original,
            passed=sum(c['result']=='PASS' for c in original),total=len(original),
            failures=[c for c in original if c['result']!='PASS'],input_sha256=hashes,
            growth=growth,malformed_growth=malformed,
            extended_runtime=dict(result='REVIEW_REQUIRED' if issues else 'PASS',rows=issues),
            transport_failures=[r for r in requests if r['result']!='PASS'])
        summary['phases'][name]=item
        if name.endswith('-eof'):
            names=('flac-level8','hev2-44100-stereo')
            item['independent_eof']=[verdict(n,lambda i=i,n=n:eof_evidence(data['status'][2*i],data['status'][2*i+1],n))
                for i,n in enumerate(n for n in names for _ in range(2))]
        if name.endswith('-switch'):
            item['independent_formats']=[verdict(b['case'],lambda b=b:check_playback(b['samples'],catalog[b['case'].split(':')[-1]]))
                for b in data['status'] if b['case'].startswith('switch:')]
        if name.endswith('-switch'):
            switch=json.loads((folder/'switching.json').read_text())
            item['switching']=switch
            item['input_sha256']['switching']=sha(folder/'switching.json')
            checkpoints=switch['checkpoints']
            item['heap_recovery']=[verdict('cycle-'+str(i+1),lambda c=c:check_recovery_heap(checkpoints[0],c))
                for i,c in enumerate(checkpoints)]
        if name.endswith('-records'):
            idle={c['name']:c.get('evidence',{}).get('samples') for c in original if c['name'] in ('idle-before','idle-recovery')}
            item['idle_heap']=idle
            def recover_records():
                assert all(idle.get(k) is not None for k in ('idle-before','idle-recovery')), 'Original idle evidence unavailable; preserve failed gate'
                return check_recovery_heap(idle['idle-before'],idle['idle-recovery'])
            item['heap_recovery']=[verdict('records-recovery',recover_records)]
        item['record_observations']=[verdict(mode,lambda mode=mode,o=o:record_evidence(o['events'],mode))
            for mode,o in data['report'].get('record_observations',{}).items()]
        if name.endswith('-records') and not item['record_observations']:
            item['record_observations']=[dict(name='grow',result='FAIL',
                reason='Runner did not freeze record acceptance evidence; interrupted observations cannot pass.')]
        for batch in data['status']:
            if not batch.get('case','').startswith(('load:','tls-record:')):continue
            measured=helper.summarize_batch(name,folder,batch,data,hashes)
            start,end=measured['measured_start'],measured['measured_end']
            measured['variant']=done[name]['variant']
            measured['flow_decoder']=strict_flow(rows,start,end,'DEC')
            measured['flow_output']=strict_flow(rows,start,end,'STAGED_OUT')
            measured['paired_memory']=paired_metrics(rows,start,end)
            points=[p for r in rows if (p:=parse_dma(r)) is not None and batch['started_at']<=p['at']<=end]
            measured['whole_observed_dma_events']=[dict(start=a['at'],end=b['at'],overruns=b['q_overruns']-a['q_overruns'],errors=b['errors']-a['errors'])
                for a,b in zip(points,points[1:]) if b['q_overruns']!=a['q_overruns'] or b['errors']!=a['errors']]
            before=[r for r in original if r['name'].startswith('load-idle-baseline:')]
            after=[r for r in original if r['name'].startswith('load-idle-recovery:')]
            if before and after:
                measured['heap_replay']=verdict('idle-recovery',lambda:check_recovery_heap(before[0]['evidence']['samples'],after[0]['evidence']['samples']))
            summary['sustained'].append(measured)
    for path in sorted((ROOT/'physical').glob('*.json')):
        if path.stem!='running':summary['controller_'+path.stem]=json.loads(path.read_text())
    args.output.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(incomplete=summary['incomplete'],
        phases={n:dict(passed=p['passed'],total=p['total'],runtime=p['extended_runtime']['result'],growth=p['growth']) for n,p in summary['phases'].items()},
        sustained=[dict(phase=c['mode'],variant=c['variant'],cpu=c['cpu']['busy_mean_percent'],
                   dma=c['dma']['delta']['q_overruns'],whole=sum(e['overruns'] for e in c['whole_observed_dma_events']),
                   heap=c.get('heap'),telemetry=c['telemetry_complete']) for c in summary['sustained']]),indent=2))

if __name__=='__main__':main()
