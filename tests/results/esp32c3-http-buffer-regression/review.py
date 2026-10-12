"""Replay saved format, EOF, memory and output evidence without contacting hardware."""
import json,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Failure,sha,check_playback,check_transitions,check_recovery_heap
from production_health import check_health
from sustained_output import check_memory,check_output
from audio_test_server.fixtures import SEQUENCES
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'physical'
load=lambda name:json.loads((OUT/name).read_text())
report=load('report.json');batches=load('status.json');health=load('health.json')
assert report['controller_sha256']==sha((ROOT/'run.py').read_bytes())
for name,digest in report['test_sources_sha256'].items():
    assert sha(Path(name).read_bytes())==digest,name
    assert sha((ROOT/'test-sources'/name).read_bytes())==digest,name
def rows(batch):return [r for r in health if batch['started_at']<=r['at']<=batch['ended_at']]
def get(name):
    found=[b for b in batches if b['case']==name]
    assert len(found)==1,(name,len(found))
    return found[0]
checks={};failures=[]
for case in report['cases']:
    name=case['name']
    if case['result']!='PASS':
        failures.append(dict(name=name,result=case['result'],reason=case.get('reason'),exception_chain=case.get('exception_chain')))
        continue
    if name.startswith('file-eof:'):
        _,fixture,hint=name.split(':');spec=report['fixture_specs'][fixture]
        batch=get(fixture+':'+hint+':playing');samples=batch['samples'];recorded=case['evidence']
        assert check_playback(samples,spec)==recorded['format']
        paired=rows(batch);assert len(samples)==len(paired)
        steady=[h for s,h in zip(samples,paired) if s['seconds']>=4]
        assert check_output(steady)==recorded['output']
        assert check_memory(steady)==recorded['memory']
        tail=get(fixture+':'+hint+':terminal')['samples'];stop=next(i for i,s in enumerate(tail) if not s['audio'])
        assert len(tail)-stop>=2 and len(tail)-stop==recorded['terminal_samples']
        assert all(not s['audio'] and s['format']=='stream ended' and not s['pcm_sample_rate'] and not s['pcm_channels'] for s in tail[stop:])
        assert recorded['websocket_stopped']
        checks[name]='Replayed format, steady output/memory, terminal state; WebSocket assertion recorded by controller'
    elif name.startswith('transition:'):
        sequence=name.split(':')[1]
        check_transitions(get(sequence)['samples'],[report['fixture_specs'][n] for n in SEQUENCES[sequence]])
        checks[name]='Replayed full-rate transitions'
    elif name=='stop-play-generation':
        check_playback(get(name)['samples'],report['fixture_specs']['lc-22050-mono'])
        checks[name]='Replayed restarted format'
    elif name.startswith('network:') and name.split(':')[1] in ('drop','stall','error'):
        mode=name.split(':')[1];assert any(not s['audio'] for s in get('fault:'+mode)['samples'][-3:])
        check_playback(get('recovered:'+mode)['samples'],report['fixture_specs']['lc-22050-mono'])
        checks[name]='Replayed stop and recovery format'
    elif name=='settled-heap':
        evidence=case['evidence'];check_recovery_heap(evidence['initial'],evidence['final'])
        checks[name]='Replayed settled memory/task recovery'
    elif name=='lifetime-health':
        assert check_health(health)==case['evidence'];checks[name]='Replayed lifetime health'
    else:checks[name]='Controller assertion retained with status/server evidence'
expected=len(report['fixture_specs'])*2+len(SEQUENCES)+1+3+2+1+2
assert len(report['cases'])==expected,(len(report['cases']),expected)
restored=load('restoration.json');initial=load('initial.json')
assert restored['identity']['app_elf_sha256']==report['baseline']['app_elf_sha256']
assert restored['same_station'] and all(restored['persistence'].values())
assert all(s['audio']==initial['original']['audio'] for s in restored['states'][-3:])
assert not initial['original']['audio'] or all(s['pcm_sample_rate']>0 for s in restored['states'][-3:])
review=dict(review='PASS',controller_cases=len(report['cases']),passed=len(checks),failures=failures,
    checks=checks,restoration=True,scope='Replay validates recorded checks, not complete protocol/analog coverage.')
(ROOT/'review.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps(dict(review='PASS',cases=len(report['cases']),passed=len(checks),failures=failures,restoration=True),indent=2))
