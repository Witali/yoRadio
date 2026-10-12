"""Replay physical diagnostics using frozen sources; never turn gaps into proof."""
import json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'physical'
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from common import Failure,sha,check_playback,check_recovery_heap
from production_health import check_health
from sustained_output import sustained_window,check_memory,check_output
from web_tcp import parse,window
from heap_receive_correlation import paired_metrics
load=lambda name:json.loads((OUT/name).read_text(encoding='utf-8'))
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except (Failure,ValueError) as error:return dict(result='FAIL',reason=str(error))
initial=load('initial.json');assert initial['controller_sha256']==sha((ROOT/'physical.py').read_bytes())
for name,digest in initial['test_sources'].items():assert sha((ROOT/'test-sources'/name).read_bytes())==digest,name
rows=load('performance.json');batches=load('status.json');health=load('health.json');results=load('results.json')
specs=json.loads((ROOT/'fixture-specs.json').read_text())
assert set(results)=={prefix+str(c) for c in range(1,6) for prefix in ('opus:','hev2-eof:')}
frames=[];invalid=[]
for row in rows:
    try:
        value=parse(row)
        if value is not None:frames.append(value)
    except ValueError as error:invalid.append(dict(at=row['at'],reason=str(error)))
phase_reviews={};correlations={}
for batch in batches:
    start,end=batch['started_at'],batch['ended_at'];name=batch['case']
    framed=evaluate(lambda:window(rows,start,end))
    if framed['result']=='PASS':
        evidence=framed['evidence'];phase_reviews[name]=dict(result='PASS',start=evidence['start'],end=evidence['end'],events=len(evidence['events']),wifi=evidence['wifi'],listeners=len(evidence['listeners']),first_edge_seconds=evidence['first_edge_seconds'],last_edge_seconds=evidence['last_edge_seconds'])
    else:phase_reviews[name]=framed
    if name.startswith('opus:'):
        states=batch['samples'];paired=[h for h in health if start<=h['at']<=end];assert len(states)==len(paired)
        steady=[h for s,h in zip(states,paired) if s['seconds']>=15]
        collected=evaluate(lambda:sustained_window(states,paired,60))
        assert results[name]['collection']==dict(result=collected['result'],reason=collected.get('reason'))
        assert results[name]['output']==evaluate(lambda:check_output(steady))
        assert results[name]['memory']==evaluate(lambda:check_memory(steady))
        assert results[name]['format']==evaluate(lambda:check_playback(states,specs['stress-opus-48000-2ch-16bit-90s'],minimum=27,warmup=15))
        # Correlation is descriptive, does not change the memory decision.
        correlations[name]=evaluate(lambda:paired_metrics(rows,start+15,end))
    if name in results:
        assert results[name]['transport']==dict(result='FAIL' if batch['errors'] else 'PASS',errors=batch['errors'])
    if name.startswith('hev2-eof:'):
        states=batch['samples'];paired=[h for h in health if start<=h['at']<=end];assert len(states)==len(paired)
        assert results[name]['format']==evaluate(lambda:check_playback([s for s in states if s['seconds']<=8],specs['hev2-44100-stereo']))
        active=[h for s,h in zip(states,paired) if 3<=s['seconds']<=8 and s['audio']]
        assert results[name]['output']==evaluate(lambda:check_output(active))
        assert results[name]['health']==check_health(paired)
        if results[name]['terminal']['result']=='PASS':
            assert len(states)>=15 and all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate'] and not s['pcm_channels'] for s in states[-5:])
connects=[json.loads(line) for line in (OUT/'request-phases.jsonl').read_text().splitlines()]
failures=[]
for request in connects:
    if request.get('phase')!='connect' or request.get('result')!='FAIL':continue
    start=request['at'];end=start+request['ms']/1000
    bracket=evaluate(lambda:window(rows,start-2,end+2))
    ports=[a.get('local_port') for a in request.get('socket_attempts',[]) if a.get('local_port')]
    item=dict(request=request,ports=ports,trace_result=bracket['result'])
    if bracket['result']=='PASS':
        e=bracket['evidence'];covered=e['start']<=start and e['end']>=end
        item.update(complete_timeout_bracket=covered,events=[r for r in e['events'] if r['port'] in ports],wifi=e['wifi'],listeners=e['listeners'],bounds=[e['start'],e['end']])
    else:item['trace_reason']=bracket['reason']
    failures.append(item)
recovery=load('recovery.json');assert recovery['check']==evaluate(lambda:check_recovery_heap(recovery['initial'],recovery['final']))
for cycle in range(1,6):
    idle=next(b for b in batches if b['case']=='idle:cycle:'+str(cycle))
    settled=[h for h in health if idle['started_at']<=h['at']<=idle['ended_at']][-3:]
    assert results['hev2-eof:'+str(cycle)]['recovery']==evaluate(lambda:check_recovery_heap(recovery['initial'],settled))
restored=load('restoration.json');assert restored['identity']['app_elf_sha256']==initial['baseline']['app_elf_sha256']
assert restored['same_station'] and all(restored['persistence'].values())
assert all(s['audio']==initial['original']['audio'] for s in restored['states'][-3:])
assert not initial['original']['audio'] or all(s['pcm_sample_rate']>0 for s in restored['states'][-3:])
startup_wifi=[f for f in frames if f['kind']=='wifi']
result=dict(review='PASS',scope='Evidence replay; each failed/missing trace remains unqualified',image=initial['candidate'],cases=results,health=check_health(health),recovery=recovery['check'],restoration=True,
    frame_count=len(frames),invalid_frames=invalid,wifi_events=startup_wifi,phase_traces=phase_reviews,failed_connects=failures,correlations=correlations)
(ROOT/'review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(review='PASS',cases=len(results),frames=len(frames),invalid_frames=len(invalid),wifi=startup_wifi,failed_connects=failures,recovery=recovery['check'],restoration=True),indent=2))
