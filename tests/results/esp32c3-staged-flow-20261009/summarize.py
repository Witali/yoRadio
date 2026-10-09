"""Replay controlled staged-output queue waits, retaining missing/failed evidence."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
SOURCES=ROOT/'sources' if (ROOT/'sources/tools').is_dir() else REPO
sys.path.insert(0,str(SOURCES/'tools/esp32c3_tests'))
from pipeline_flow import FIELDS, flow_summary
from staged_dma import parse as parse_dma
from heap_receive_correlation import paired_metrics
from tls_records import record_evidence

HELPER=SOURCES/'tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py'
spec=importlib.util.spec_from_file_location('sustained',HELPER)
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
PHASES=('control-short','profile-short','profile-long')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def strict_flow(rows,start,end,kind):
    result=flow_summary(rows,start,end,kind)
    selected=[];issues=[]
    marker='PERF FLOW_'+kind+':'
    fields=['gen','window_us']
    for field in FIELDS[kind]:
        fields += [field+'_us',field+'_n',field+'_max']
        if field!='submit': fields += [field+'_timeouts']
    if kind!='DEC': fields+=['overruns']
    for row in rows:
        if marker not in row['line']: continue
        pairs=re.findall(r'(\w+)=(\d+)\b',row['line'])
        values={k:int(v) for k,v in pairs}
        if row['line'].count('PERF ')!=1 or any(sum(k==f for k,v in pairs)!=1 for f in fields):
            issues.append(dict(reason='Missing, duplicate or merged field',row=row));continue
        if not math.isfinite(row['at']) or not values['window_us']:
            issues.append(dict(reason='Invalid time',row=row));continue
        duration=values['window_us']/1e6
        if start<=row['at']-duration and row['at']<=end:
            selected.append(dict(at=row['at'],seconds=duration,**values))
    coverage=helper.interval_coverage(selected,start,end)
    if [dict((k,v) for k,v in w.items() if k not in ('at','seconds')) for w in selected]!=result['windows']:
        issues.append(dict(reason='Strict and canonical field validation disagree'))
    generations={w['gen'] for w in selected}
    if len(generations)!=1: issues.append(dict(reason='Missing or changing generation'))
    result.update(coverage=coverage,issues=issues,intervals=selected,
        complete=not issues and not result['malformed'] and coverage['coverage_complete'])
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'summary.json')
    args=parser.parse_args()
    done=ROOT/'physical/phases.json'
    completed=json.loads(done.read_text()) if done.is_file() else []
    phases={p['name']:p for p in completed}
    summary=dict(phases={},cases=[],incomplete=[],scope='Queue wait wall time is not CPU time; DMA counters are not acoustic capture.')
    for name in PHASES:
        folder=ROOT/'physical'/name
        if name not in phases:
            summary['incomplete'].append(name);continue
        paths={k:folder/(k+'.json') for k in ('report','status','performance')}
        data={k:json.loads(p.read_text()) for k,p in paths.items()}
        hashes={k:sha(p) for k,p in paths.items()}
        original=data['report']['cases']
        record={}
        for mode,observation in data['report'].get('record_observations',{}).items():
            try: record[mode]=dict(result='PASS',**record_evidence(observation['events'],mode))
            except AssertionError as error: record[mode]=dict(result='FAIL',reason=str(error))
        timing=ROOT/'physical'/(name+'-request-phases.jsonl')
        requests=[json.loads(line) for line in timing.read_text().splitlines()]
        summary['phases'][name]=dict(controller=phases[name],board=data['report']['board'],
            original_acceptance=original,passed=sum(c['result']=='PASS' for c in original),total=len(original),
            record_observations=record,pacing_ratio=data['report']['pacing_ratio'],input_sha256=hashes,
            transport_failures=[r for r in requests if r['result']!='PASS'])
        for batch in data['status']:
            if not batch['case'].startswith('tls-record:'): continue
            item=helper.summarize_batch(name,folder,batch,data,hashes)
            start,end=item['measured_start'],item['measured_end']
            stacks={task:[] for task in ('audio_decode','audio_output','radio_stream')}
            for row in data['performance']:
                match=re.search(r'PERF STACK: name=(\w+) minimum_free=(\d+)\b',row['line'])
                if match and match[1] in stacks and start<=row['at']<=end:
                    stacks[match[1]].append(int(match[2]))
            item['stack_minimum_free']={task:min(values) if values else None for task,values in stacks.items()}
            item['prefill_rows']=[r for r in data['performance'] if batch['started_at']-1<=r['at']<=end and 'PERF INPUT_PREFILL:' in r['line']]
            if name.startswith('profile'):
                item['flow_decoder']=strict_flow(data['performance'],start,end,'DEC')
                item['flow_staged_output']=strict_flow(data['performance'],start,end,'STAGED_OUT')
                item['flow_complete']=item['flow_decoder']['complete'] and item['flow_staged_output']['complete'] and not item['interrupted']
                item['flow_event_windows']=[w for w in item['flow_staged_output']['intervals'] if w['overruns']]
            try:
                points=[p for r in data['performance'] if (p:=parse_dma(r)) is not None and batch['started_at']<=p['at']<=end]
                item['whole_observed_dma_events']=[dict(start=a['at'],end=b['at'],overruns=b['q_overruns']-a['q_overruns'],errors=b['errors']-a['errors'])
                    for a,b in zip(points,points[1:]) if b['q_overruns']!=a['q_overruns'] or b['errors']!=a['errors']]
                item['paired_memory']=paired_metrics(data['performance'],start,end)
            except (ValueError,TypeError) as error: item['extra_telemetry_error']=str(error)
            summary['cases'].append(item)
    for name in ('initial','installed-control','installed-profile','control-clock','profile-clock',
                 'phases','settings-after-tests','restoration','controller-failure','restoration-failure'):
        path=ROOT/'physical'/(name+'.json')
        if path.is_file():summary['controller_'+name]=json.loads(path.read_text())
    args.output.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(incomplete=summary['incomplete'],cases=[dict(mode=c['mode'],case=c['observation'],
        accepted=c['acceptance_passed'],telemetry=c['telemetry_complete'],flow_complete=c.get('flow_complete'),
        dma=c.get('dma',{}).get('delta'),input=c.get('flow_decoder',{}).get('input'),
        pcm_full=c.get('flow_decoder',{}).get('pcm'),pcm_empty=c.get('flow_staged_output',{}).get('empty'),
        submit=c.get('flow_staged_output',{}).get('submit')) for c in summary['cases']]),indent=2))

if __name__=='__main__':main()
