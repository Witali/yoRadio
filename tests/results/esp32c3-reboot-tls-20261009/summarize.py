"""Independently replay completed paired controls, including every TLS message."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'sources/tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap, matches
from reboot_tls import FAULT, review_trial, stopped
from pdm_clock import parse

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'summary.json')
args=p.parse_args()
read=lambda name:json.loads((ROOT/name).read_text())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
initial=read('physical/initial.json')
sources=read('sources.json')
assert all(sha(ROOT/'sources'/name)==digest for name,digest in sources.items())
assert all(sources[name]==digest for name,digest in initial['test_sources_sha256'].items())
manifest=read('artifacts/manifest.json')
assert initial['candidate']==manifest['image']
assert sha(ROOT/'artifacts/sdkconfig')==manifest['sdkconfig_sha256']
report=read('physical/reboot-control/report.json')
rows=read('physical/reboot-control/performance.json')
observations=read('physical/reboot-control/status.json')
assert report['test_sources_sha256']==initial['test_sources_sha256']
assert report['firmware']==initial['candidate']
assert report['board']['app_elf_sha256']==initial['candidate']['app_elf_sha256']
assert report['pacing_ratio']==1.0 and report['transport']=='https'
spec=read('fixture.json')
assert report['fixture_sha256']==spec['sha256']
trials=report['trials']
assert len(trials)==6 and [t['name'] for t in trials]==[
    '1:active','1:stopped','2:stopped','2:active','3:active','3:stopped']
assert [p['code'] for p in read('physical/phases.json')]==[0]
assert all(t['result']=='PASS' for t in trials)
assert not (ROOT/'physical/controller-failure.json').exists()
assert not (ROOT/'physical/restoration-failure.json').exists()
actions={}
for r in report['timeline']: actions.setdefault(r['action'],[]).append(r)
assert all([r['event'] for r in a]==['begin','returned'] for a in actions.values())
assert all(a['at']<=b['at'] for a,b in zip(report['timeline'],report['timeline'][1:]))
result=dict(scope='Paired software-reboot controls, not continuous-playback or analog qualification.',trials=[])
for trial in trials:
    label=trial['name']
    replay=review_trial(trial,rows)
    assert replay==trial['review'] and replay['result']=='PASS'
    batch=next(o for o in observations if o['case']==label+':playback')
    assert not batch.get('interrupted')
    assert check_playback(batch['samples'],spec,warmup=3)==trial['playback']
    assert matches(trial['last_playback_state'],spec)
    assert actions[label+':playback'][1]['at']<=trial['reboot_started_at']
    assert trial['boot']['app_elf_sha256']==report['board']['app_elf_sha256']
    assert trial['boot']['partition']==report['board']['partition']
    events=trial['server_before_control']
    assert len(events)==1 and events[0]['sent']>0 and events[0]['pacing_ratio']==1.0
    assert events[0]['fixture']=='hev2-44100-stereo' and events[0]['tls_version']=='TLSv1.2'
    row=dict(name=label,mode=trial['mode'],replay=replay,
        minimum_rssi=min(s['rssi'] for s in batch['samples']),
        median_rssi=statistics.median(s['rssi'] for s in batch['samples']),
        max_request_ms=max(s['request_ms'] for s in batch['samples']))
    if trial['mode']=='stopped':
        settle=next(o for o in observations if o['case']=='settled-idle' and
                    trial['stop_started_at']<=o['started_at']<trial['reboot_started_at'])
        assert not settle.get('interrupted')
        stopped(settle['samples'])
        check_recovery_heap(trial['baseline'],trial['settled'])
        row['settled']=trial['settled']
    result['trials'].append(row)
for filename in ('installed','restoration'):
    state=read('physical/'+filename+'.json')
    assert state['persistence'] and all(v is True for v in state['persistence'].values())
assert all(v is True for v in report['persistence'].values())
assert all(v is True for v in read('physical/settings-after-tests.json').values())
restored=read('physical/restoration.json')
assert restored['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']
assert len(restored['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restored['states'])
clock=read('physical/fractional-clock.json')
clocks=[p for r in clock['rows'] if (p:=parse(r['line'])) is not None]
assert len(clocks)==1 and clocks[0]['exact_nominal_48khz']
assert any('expected=qio ctrl=0x012c2008 ' in r['line'] and 'actual_mhz=80 ' in r['line'] for r in clock['rows'])
all_resets=[r for r in rows if r['line'].startswith('rst:')]
assert all_resets==[r for t in result['trials'] for r in t['replay']['resets']]
assert not any(FAULT.search(r['line']) for r in rows)
outside_tls=[r for r in rows if r['line'].startswith('TLS failure:') and
             not any(t['started_at']<=r['at']<=t['ended_at'] for t in trials)]
result.update(source_files=len(sources),timed_actions=len(actions),restored=True,outside_trial_tls=outside_tls,
    result='PASS',qualification='TLS errors remain visible; PASS is evidence/operational-gate replay only.')
args.output.write_text(json.dumps(result,indent=2)+'\n')
for t in result['trials']:
    print(t['name'],t['replay']['result'],'TLS',len(t['replay']['tls']),
          [r['phase'] for r in t['replay']['tls']])
print('Verified',len(sources),'sources,',len(actions),'actions, full fixture format and restoration')
