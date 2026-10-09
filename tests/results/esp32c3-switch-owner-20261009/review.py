"""Replay owner snapshots and correlate them with captured test boundaries."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from statistics import median
import sys
from references import verify_references

verify_references()

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
PRIOR=REPO/'tests/results/esp32c3-flac-input-growth-20261009'
sys.path.insert(0,str(PRIOR/'sources/tools/esp32c3_tests'))
from heap_fragment import analyze
from common import check_playback, check_recovery_heap
sys.path.insert(0,str(PRIOR))
from eof_replay import verdict, eof_evidence
from tls_records import record_evidence
from flow_windows import helper, strict_flow
from staged_dma import parse as parse_dma
from public_streams import no_runtime_faults

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'review.json')
p.add_argument('--fixed',action='store_true',help='Review old/fixed images with corrected server lifetime')
p.add_argument('--confirmed',action='store_true',help='Review fixed image with bounded serial shutdown and post-close gate')
a=p.parse_args()
catalog=json.loads((ROOT/'case-catalog.json').read_text())
result=dict(scope='Owner metadata in one initially free region; original failures retained. Diagnostic timing is not a production benchmark.',trials={},incomplete=[])

def medians(rows):
    return {k:median(s[k] for s in rows) for k in ('heap','largest','tasks')}

labels = ('original-growth','retained-growth') if a.fixed else ('expanded-owner','control-owner')
physical = 'physical-fixed' if a.fixed else 'physical'
if a.confirmed: labels,physical=('retained-confirmed',),'physical-confirmed'
for label in labels:
    folder=ROOT/physical/label
    if not (folder/'report.json').exists():result['incomplete'].append(label);continue
    report=json.loads((folder/'report.json').read_text())
    records=json.loads((folder/'performance.json').read_text())
    status=json.loads((folder/'status.json').read_text())
    try:owners=analyze(records)
    except ValueError as error:owners=dict(complete=False,reason=str(error))
    if (folder/'owners.json').exists():
        assert owners == json.loads((folder/'owners.json').read_text()), 'Stored owner analysis differs'
    item=dict(board=report['board'],original_cases=report['cases'],
        passed=sum(c['result']=='PASS' for c in report['cases']),total=len(report['cases']),
        failures=[c for c in report['cases'] if c['result']!='PASS'],
        owner_analysis=owners,actions=report.get('actions',[]),
        idle_checkpoints={n:medians(rows) for n,rows in report.get('idle_checkpoints',{}).items()},
        quiet_window=report.get('quiet_window'),
        independent_formats=[verdict(b['case'],lambda b=b:check_playback(b['samples'],catalog[b['case'].split(':')[-1]]))
                             for b in status if b['case'].startswith('switch:')])
    item['full_capture_runtime']=verdict('full-capture-runtime',lambda:no_runtime_faults(records))
    terminal=[b for b in status if b['case'].endswith((':playing',':terminal'))]
    item['independent_eof']=[verdict(terminal[i]['case'],lambda i=i:eof_evidence(terminal[i],terminal[i+1],terminal[i]['case'].removesuffix(':playing')))
                             for i in range(0,len(terminal),2)]
    if 'record_observation' in report:
        item['independent_records']=verdict('grow',lambda:record_evidence(report['record_observation']['events'],'grow'))
    else:item['independent_records']=dict(name='grow',result='FAIL',reason='No frozen record acceptance snapshot')
    if (folder/'switching.json').exists():
        switching=json.loads((folder/'switching.json').read_text())
        item['switching']=switching
        item['cross_phase']={n:verdict(n,lambda rows=rows:check_recovery_heap(switching['checkpoints'][0],rows))
                for n,rows in report.get('idle_checkpoints',{}).items() if n!='initial'}
    if owners['complete']:
        snapshots=owners['snapshots']
        for s in snapshots:
            s['action']=next((x['name'] for x in item['actions'] if x['started_at']<=s['at']<=x['ended_at']),None)
        item['nonfree_snapshots']=[s for s in snapshots if s['live']]
        item['initial_raw_free']=snapshots[0]['largest_raw_free']
        item['minimum_raw_free']=min(s['largest_raw_free'] for s in snapshots)
        item['final_raw_free']=snapshots[-1]['largest_raw_free']
        item['peak_live']=max(s['peak'] for s in snapshots)
        item['max_walk_us']=max(s['walk_us'] for s in snapshots)
        identities={}
        for s in snapshots:
            for b in s['blocks']:
                if not b['id']:continue
                record=identities.setdefault(str(b['id']),dict(**b,first_seen=s['at'],last_seen=s['at'],snapshots=0,actions=[]))
                record['last_seen']=s['at'];record['snapshots']+=1
                if s['action'] not in record['actions']:record['actions'].append(s['action'])
        item['live_identities']=identities
    trace=folder/'request-phases.jsonl'
    item['transport_failures']=[r for line in trace.read_text().splitlines() if (r:=json.loads(line))['result']!='PASS']
    item['input_sha256']={n:hashlib.sha256((folder/n).read_bytes()).hexdigest() for n in ('report.json','status.json','performance.json','request-phases.jsonl')}
    item['record_metrics']=[]
    for batch in status:
        if not batch['case'].startswith('tls-record:'):continue
        measured=helper.summarize_batch(label,folder,batch,dict(report=report,status=status,performance=records),item['input_sha256'])
        start,end=measured['measured_start'],measured['measured_end']
        measured['flow_decoder']=strict_flow(records,start,end,'DEC')
        measured['flow_output']=strict_flow(records,start,end,'STAGED_OUT')
        points=[];dma_issues=[]
        for row in records:
            try:point=parse_dma(row)
            except ValueError as error:
                dma_issues.append(dict(reason=str(error),row=row));continue
            if point is not None and batch['started_at']<=point['at']<=end:points.append(point)
        measured['whole_observed_dma_review']=dict(result='FAIL' if dma_issues else 'PASS',issues=dma_issues)
        measured['whole_observed_dma_events']=[dict(start=x['at'],end=y['at'],overruns=y['q_overruns']-x['q_overruns'],errors=y['errors']-x['errors'])
                for x,y in zip(points,points[1:]) if y['q_overruns']!=x['q_overruns'] or y['errors']!=x['errors']]
        item['record_metrics'].append(measured)
    result['trials'][label]=item
    if not any(c['name']=='owners-complete' for c in report['cases']):result['incomplete'].append(label)
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(incomplete=result['incomplete'],trials={n:{k:v for k,v in t.items() if k in ('passed','total','failures','idle_checkpoints','initial_raw_free','minimum_raw_free','final_raw_free','peak_live','max_walk_us','live_identities','transport_failures')} for n,t in result['trials'].items()}),indent=2))
