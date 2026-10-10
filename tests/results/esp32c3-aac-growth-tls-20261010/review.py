"""Replay growth verdicts, TLS delivery and exact listened-image restoration."""
import json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'test-sources/tools/esp32c3_tests'))
from common import Failure,check_recovery_heap,require
from aac_growth import check_tls_delivery
from production_health import check_health,output_window
from public_file_acceptance import check_finite_playback
P=ROOT/'physical'
r=json.loads((P/'files/report.json').read_text())
health=json.loads((P/'files/health.json').read_text())
batches=json.loads((P/'files/status.json').read_text())
cases={c['name']:c['result'] for c in r['cases']}
assert json.loads((P/'phase.json').read_text())['code']==(0 if all(v=='PASS' for v in cases.values()) else 1)
results={}
for batch in batches:
    name=batch['case']
    if name.startswith('idle:'):continue
    assert 'interrupted' not in batch,batch.get('exception_chain')
    source,label=name.rsplit('-',1)
    reference=r['references'][source]
    info=r['fixtures'][source]
    assert reference['baseline']==reference['growth']
    stream=reference['growth']['ffprobe']['streams'][0]
    profile=source.split('-')[0]
    spec=dict(rate=int(stream['sample_rate']),channels=int(stream['channels']),bits=16,
              label={'lc':'AAC PCM','he':'HE-AAC ','hev2':'HE-AACv2 '}[profile],
              container_label='AAC',seconds=info['seconds'])
    playback=check_finite_playback(batch['samples'],spec)
    start=batch['started_at']
    steady=[h for h in health if start+playback['first_playback_seconds']+3<=h['at']<=start+playback['first_stopped_seconds']-1]
    require(len(steady)>=10,'Missing growth health evidence')
    metrics=check_health(steady);output=output_window(steady)
    windows={}
    for window,lo,hi in (('before_growth',8,13),('after_growth',23,30)):
        rows=[h for h in steady if lo<=h['at']-start<=hi]
        require(len(rows)>=5,'Missing growth memory window')
        windows[window]={k:statistics.median(h[k] for h in rows) for k in ('heap','largest','tasks')}
    measured=dict(playback=playback,health=metrics,windows=windows,
                  maximum_status_health_ms=max(s['request_ms'] for s in batch['samples']),output=output)
    assert measured==r['playback_cases'][name],name
    passed=(metrics['minimum_heap']>=16384 and metrics['minimum_largest']>=8192 and
            measured['maximum_status_health_ms']<2000 and not output['completion_queue_drops'] and not output['write_errors'])
    assert cases[name]==('PASS' if passed else 'FAIL')
    results[name]=dict(result=cases[name],**measured)
# Only byte counts are used by the independent TLS-delivery gate.
specs={name:dict(data=bytes(r['fixtures'][name.rsplit('-',1)[0]]['files'][name.rsplit('-',1)[1]]['bytes'])) for name in results}
assert check_tls_delivery(r['server_events'],specs)==dict(transfers=6)
assert cases['tls-delivery']=='PASS'
assert len(results)==6
for key,rows in r['idle'].items():
    check_recovery_heap(r['idle']['initial'],rows)
faults=check_health(health)
restore=json.loads((P/'restoration.json').read_text())
assert restore['identity']['app_elf_sha256']=='76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b'
assert all(restore['persistence'].values())
assert len(restore['states'])==3 and all(not s['audio'] for s in restore['states'])
result=dict(replay='PASS',counts=dict(passed=sum(c=='PASS' for c in cases.values()),total=len(cases)),
            failed_cases=[n for n,v in cases.items() if v!='PASS'],files=results,
            lifetime_health=faults,tls_connections=len(r['server_events']),
            tls_parameters=sorted({(e['tls_version'],e['tls_cipher']) for e in r['server_events']}),
            exact_listened_image_restored=True)
encoded=json.dumps(result,indent=2)+'\n'
if (ROOT/'review.json').exists():assert (ROOT/'review.json').read_text()==encoded
else:(ROOT/'review.json').write_text(encoded)
print(json.dumps({k:v for k,v in result.items() if k!='files'}))
