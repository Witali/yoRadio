"""Replay sustained gates from preserved technical samples, including failures."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from common import Failure,check_playback,check_recovery_heap,require
from production_health import check_health,output_window,OUTPUT_COUNTERS,COUNTER_MASK
from sustained_output import sustained_window,check_output,check_memory
P=ROOT/'physical'
report=json.loads((P/'files/report.json').read_text())
health=json.loads((P/'files/health.json').read_text())
batches=json.loads((P/'files/status.json').read_text())
offset=0;target=None
for batch in batches:
    rows=batch['samples'];paired=health[offset:offset+len(rows)];offset+=len(rows)
    if batch['case'].startswith('https:'):
        assert target is None
        target=(batch,rows,paired)
assert target is not None
batch,states,paired=target
assert 'interrupted' not in batch,batch.get('exception_chain')
steady,measured=sustained_window(states,paired,report['seconds'])
metrics=output_window(measured)
assert metrics==report['output_window']
assert check_health(measured)==report['steady_health']
first_pcm=next(s['seconds'] for s in states if s['audio'])
assert first_pcm<=15,'Late startup'
cases={c['name']:c['result'] for c in report['cases']}
replayed={}
def replay(name,fn):
    try:fn();result='PASS'
    except Failure:result='FAIL'
    assert result==cases[name],(name,result,cases[name])
    replayed[name]=result
replay('format',lambda:check_playback(states,report['reference']['spec'],minimum=int((report['seconds']-15)*.6),warmup=15))
replay('output',lambda:check_output(measured))
replay('memory',lambda:check_memory(measured))
replay('response-time',lambda:require(max(s['request_ms'] for s in states)<2000,'Slow response'))
replay('lifetime-health',lambda:check_health(health))
replay('recovery',lambda:check_recovery_heap(report['idle']['initial'],report['idle']['final']))
events=[]
for index,(a,b) in enumerate(zip(measured,measured[1:]),1):
    changes={key:(b['output'][key]-a['output'][key])&COUNTER_MASK for key in OUTPUT_COUNTERS}
    if any(changes.values()):
        events.append(dict(from_seconds=steady[index-1]['seconds'],to_seconds=steady[index]['seconds'],
                           changes=changes,request_ms=steady[index]['request_ms'],rssi=steady[index].get('rssi'),
                           heap=b['heap'],largest=b['largest']))
restore=json.loads((P/'restoration.json').read_text())
assert restore['identity']['app_elf_sha256']=='76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b'
assert all(restore['persistence'].values())
assert len(restore['states'])==3 and all(not s['audio'] for s in restore['states'])
phase=json.loads((P/'phase.json').read_text())
failures=[c['name'] for c in report['cases'] if c['result']!='PASS']
assert phase['code']==(1 if failures else 0)
result=dict(replay='PASS',physical_failed_cases=failures,replayed=replayed,
    counts=dict(passed=sum(c['result']=='PASS' for c in report['cases']),total=len(cases)),
    seconds=report['seconds'],sustained_output=metrics,first_pcm_seconds=first_pcm,
    lifetime_health=check_health(health),steady_health=check_health(measured),
    maximum_status_health_ms=max(s['request_ms'] for s in states),
    rssi_min=min(s['rssi'] for s in states),rssi_max=max(s['rssi'] for s in states),
    output_events=events,exact_listened_image_restored=True)
if (ROOT/'review.json').exists():
    assert json.loads((ROOT/'review.json').read_text())==result,'Saved review changed'
else:
    (ROOT/'review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
