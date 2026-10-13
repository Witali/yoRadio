import json,statistics,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Failure,sha,check_playback,check_recovery_heap
from ota import image_info
from production_health import check_health
from sustained_output import sustained_window,check_output,check_memory
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'physical'
load=lambda name:json.loads((OUT/name).read_text())
initial=load('initial.json')
assert initial['controller_sha256']==sha((ROOT/'physical.py').read_bytes())
for name,digest in initial['test_sources'].items():
    assert sha(Path(name).read_bytes())==digest,name
    assert sha((ROOT/'test-sources'/name).read_bytes())==digest,name
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease/app.bin')
assert image_info(art.read_bytes())==initial['candidate']
ota=load('ota.json')
expected=['ota:'+n for n in ('wrong-chip','wrong-project','corrupt-image','truncated-image','extra-byte','missing-boundary','spiffs-target','oversized-request','disconnect','stall','roundtrip:1','roundtrip:2','while-playing','slow')]+['restore-saved-station']
assert [c['name'] for c in ota['cases']]==expected
assert ota['image']==initial['candidate']
assert ota['play_fixture']['profile']=='HE-AAC' and ota['play_fixture']['rate']==44100
for case in ota['cases']:
    if case['result']!='PASS':continue
    e=case['evidence']
    assert all(e[k] for k in ('wifi_unchanged','playlist_unchanged','settings_unchanged'))
    if 'active_image_unchanged' in e:
        assert e['active_image_unchanged'] and (e['http'] is None if case['name']=='ota:disconnect' else e['http']==400)
    elif 'hash_verified' in e:assert e['hash_verified'] and e['partition'] in ('app0','app1')
assert load('ota-exit.json')['exit_code']==(0 if all(c['result']=='PASS' for c in ota['cases']) else 1)
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
batch=next(b for b in load('status.json') if b['case']=='public-he-https-600s')
rows=[h for h in load('health.json') if batch['started_at']<=h['at']<=batch['ended_at']]
states,health=sustained_window(batch['samples'],rows,600)
spec=load('public-reference.json')['spec']
checks=dict(transport=dict(result='FAIL' if batch['errors'] else 'PASS',errors=batch['errors']),
    format=evaluate(lambda:check_playback(batch['samples'],spec,minimum=351,warmup=15)),
    output=evaluate(lambda:check_output(health)),memory=evaluate(lambda:check_memory(health)))
soak=load('soak.json');assert all(soak[k]==checks[k] for k in checks)
assert soak['health']==check_health(health)
recovery=load('soak-recovery.json')
assert recovery['check']==evaluate(lambda:check_recovery_heap(recovery['initial'],recovery['final']))
restored=load('restoration.json')
assert restored['same_station'] and all(restored['persistence'].values())
assert restored['identity']['app_elf_sha256']==initial['baseline']['app_elf_sha256']
assert all(s['audio']==initial['original']['audio'] for s in restored['states'][-3:])
assert not initial['original']['audio'] or all(s['pcm_sample_rate']>0 for s in restored['states'][-3:])
metrics={k:dict(minimum=min(r[k] for r in health),median=statistics.median(r[k] for r in health),
    first=statistics.median(r[k] for r in health[:3]),last=statistics.median(r[k] for r in health[-3:])) for k in ('heap','largest')}
review=dict(review='PASS',ota=dict(cases=len(ota['cases']),passed=sum(c['result']=='PASS' for c in ota['cases']),
    failures=[c for c in ota['cases'] if c['result']!='PASS']),soak=dict(checks=checks,health=soak['health'],metrics=metrics,
    response_maximum_ms=soak['maximum_response_ms'],lifetime_heap_low_water=min(h['minimum_heap'] for h in rows)),recovery=recovery['check'],restoration=True)
(ROOT/'review.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps(review,indent=2))
