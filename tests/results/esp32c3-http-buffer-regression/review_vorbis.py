import json,statistics,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Failure,sha,check_playback,check_transitions,fixtures
from audio_test_server.fixtures import SEQUENCES
from production_health import check_health
from sustained_output import sustained_window,check_memory,check_output
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'vorbis-physical'
load=lambda name:json.loads((OUT/name).read_text())
initial=load('initial.json')
assert initial['controller_sha256']==sha((ROOT/'vorbis.py').read_bytes())
for name,digest in initial['test_sources'].items():assert sha(Path(name).read_bytes())==digest,name
manifest=json.loads((ROOT/'vorbis-stress/manifest.json').read_text())
assert len(manifest['fixtures'])==1
spec=manifest['fixtures'][0]
assert sha((ROOT/'vorbis-stress'/spec['file']).read_bytes())==spec['sha256']
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Failure as error:return dict(result='FAIL',reason=str(error))
cases={}
for name,result in load('results.json').items():
    variant=result['variant'];batch=next(b for b in load(variant+'/status.json') if b['case']==name)
    rows=[h for h in load(variant+'/health.json') if batch['started_at']<=h['at']<=batch['ended_at']]
    states,health=sustained_window(batch['samples'],rows,60)
    checks=dict(transport=dict(result='FAIL' if batch['errors'] else 'PASS',errors=batch['errors']),
        format=evaluate(lambda:check_playback(batch['samples'],result['spec'],minimum=27,warmup=15)),
        output=evaluate(lambda:check_output(health)),memory=evaluate(lambda:check_memory(health)))
    assert all(checks[k]==result[k] for k in checks)
    cases[name]=dict(checks=checks,health=check_health(health),metrics={k:dict(
        first=statistics.median(r[k] for r in health[:3]),last=statistics.median(r[k] for r in health[-3:]),
        median=statistics.median(r[k] for r in health)) for k in ('heap','largest')})
assert len(cases)==2
restored=load('restoration.json')
assert restored['same_station'] and all(restored['persistence'].values())
assert restored['identity']['app_elf_sha256']==initial['baseline']['app_elf_sha256']
assert all(s['audio']==initial['original']['audio'] and s['pcm_sample_rate']>0 for s in restored['states'][-3:])
repeat=load('transition-repeat.json')
batch=next(b for b in load('released/status.json') if b['case']=='repeat:changing')
specs=fixtures()
assert repeat['format']==evaluate(lambda:check_transitions(batch['samples'],[specs[n] for n in SEQUENCES['changing']]))
assert repeat['transport']==dict(result='FAIL' if batch['errors'] else 'PASS',errors=batch['errors'])
rows=[h for h in load('released/health.json') if batch['started_at']<=h['at']<=batch['ended_at']]
assert repeat['health']==check_health(rows)
review=dict(review='PASS',cases=cases,transition_repeat=repeat,restoration=True)
(ROOT/'vorbis-review.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps(review,indent=2))
