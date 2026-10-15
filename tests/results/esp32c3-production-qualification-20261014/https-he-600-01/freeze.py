"""Freeze a finished exact-image quiet campaign and replay its public gates."""
import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import check_playback,check_recovery_heap,require
from production_health import check_health,check_decoder_health
from sustained_output import check_memory,check_output
run,controller=sys.argv[1:]
base=Path('.build/c3-production-qualification-20261014');src=base/run
dst=Path('tests/results/esp32c3-production-qualification-20261014')/run
r=json.loads((src/'report.json').read_text())
require(any(c['name']=='all-decoder-health' for c in r['cases']), 'Campaign not finished')
require(not dst.exists(), 'Preserve archived evidence');shutil.copytree(src,dst)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((dst.parent/'network-ws-02/test-source-reference.json').read_text());mapping={}
for name,digest in r['test_sources_sha256'].items():
    saved=Path(old[name]['path']) if name in old else Path(name)
    if not saved.is_file() or sha(saved)!=digest:
        p=Path(name);require(sha(p)==digest,'Changed test source: '+name)
        saved=dst/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
(dst/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
shutil.copyfile(base/controller,dst/'controller.py');shutil.copyfile(base/'freeze-quiet.py',dst/'freeze.py')
shutil.copyfile('firmware/development/esp32c3-idf61-production-20261013/manifest.json',dst/'firmware-manifest.json')
health=json.loads((src/'health.json').read_text())
states=json.loads((src/'status.json').read_text())
phases=[json.loads(l) for l in (src/'request-phases.jsonl').read_text().splitlines()]
summary=dict(image=r['image'],counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
    failures=[c for c in r['cases'] if c['result']!='PASS'],idle=r['idle'],
    failed_request_phases=[p for p in phases if p['result']!='PASS'],scope=r['scope'])
for key,check in [('health',check_health),('decoder_health',check_decoder_health)]:
    try:summary[key]=dict(result='PASS',**check(health))
    except Exception as e:summary[key]=dict(result='FAIL',reason=str(e))
summary['public_replay']=[]
for name,reference in r.get('references',{}).items():
    replay=dict(name=name,result='FAIL')
    try:
        batches=[s for s in states if s['case']=='https:'+name]
        require(len(batches)==1,'Missing unique public observation')
        b=batches[0];rows=b['samples'];duration=r['public_seconds']
        require(rows[-1]['seconds']>=duration-1,'Incomplete observation')
        replay['playback']=check_playback(rows,reference['spec'],minimum=int((duration-15)*.6),warmup=15)
        first=next(s['seconds'] for s in rows if s['audio']);require(first<=15,'Late first PCM')
        replay['first_pcm_seconds']=first
        measured=[h for h in health if b['started_at']+15<=h['at']<=b['ended_at']]
        replay['memory']=check_memory(measured);replay['output']=check_output(measured)
        replay['maximum_status_health_ms']=max(s['request_ms'] for s in rows)
        require(replay['maximum_status_health_ms']<2000,'Slow WebUI response')
        replay['result']='PASS'
    except Exception as e:replay['reason']=str(e)
    summary['public_replay'].append(replay)
summary['recovery_replay']=[]
for name,rows in r['idle'].items():
    if name=='initial':continue
    result=dict(name=name,result='FAIL')
    try:check_recovery_heap(r['idle']['initial'],rows);result['result']='PASS'
    except Exception as e:result['reason']=str(e)
    summary['recovery_replay'].append(result)
(dst/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
checks={p.relative_to(dst).as_posix():sha(p) for p in sorted(dst.rglob('*')) if p.is_file()}
(dst/'sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('idle','failed_request_phases')}))
