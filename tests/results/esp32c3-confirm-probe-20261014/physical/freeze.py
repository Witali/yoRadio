"""Freeze a finished exact-image quiet campaign and replay its public gates."""
import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import check_playback,check_recovery_heap,check_transitions,fixtures,require,matches
from production_health import check_health,check_decoder_health,output_window
from sustained_output import check_memory,check_output
run,controller='public-radio','run-radio.py'
base=Path('.build/c3-confirm-probe-20261014');src=base/'https-radio'/run
dst=Path('tests/results/esp32c3-confirm-probe-20261014/physical')
r=json.loads((src/'report.json').read_text())
require(any(c['name']=='all-decoder-health' for c in r['cases']), 'Campaign not finished')
deployment=json.loads((base/'https-radio/controller.json').read_text())
require(deployment['restored']['stopped'] and 'restoration_failure' not in deployment, 'Missing restoration')
require(deployment['restored']['identity']['app_elf_sha256']==deployment['original']['app_elf_sha256'], 'Wrong restored image')
require(all(deployment['restored']['settings'].values()), 'Settings changed')
require(not dst.exists(), 'Preserve archived evidence');shutil.copytree(src,dst)
shutil.copyfile(base/'https-radio/controller.json',dst/'deployment.json')
shutil.copyfile(base/'deploy.py',dst/'deployment.py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
require(sha(dst/'deployment.py')==deployment['controller_sha256'], 'Changed deployment source')
old=json.loads((Path('tests/results/esp32c3-production-qualification-20261014/network-ws-02/test-source-reference.json')).read_text());mapping={}
for name,digest in r['test_sources_sha256'].items():
    saved=Path(old[name]['path']) if name in old else Path(name)
    if name not in old or not saved.is_file() or sha(saved)!=digest:
        p=Path(name);require(sha(p)==digest,'Changed test source: '+name)
        saved=dst/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
(dst/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
shutil.copyfile(base/controller,dst/'controller.py');shutil.copyfile(base/'freeze.py',dst/'freeze.py')
shutil.copyfile('firmware/development/esp32c3-idf61-confirm-probe/manifest.json',dst/'firmware-manifest.json')
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
        first=next(s['seconds'] for s in rows if matches(s,reference['spec']));require(first<=15,'Late first decoded format')
        replay['first_pcm_seconds']=first
        measured=[h for h in health if b['started_at']+15<=h['at']<=b['ended_at']]
        replay['memory']=check_memory(measured)
        replay['measured_output_counters']=output_window(measured)
        replay['output_increments']=[dict(from_seconds=a['at']-b['started_at'],to_seconds=c['at']-b['started_at'],
            heap=c['heap'],largest=c['largest'],**output_window([a,c]))
            for a,c in zip(measured,measured[1:])
            if a['output']!=c['output']]
        replay['output']=check_output(measured)
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
if 'transitions' in r['suites']:
    import audio_test_server.fixtures as fixture_module
    fixture_module.ROOT=Path('C:/Work/yoRadio')
    specs=fixtures();summary['transition_replay']=[]
    for name,sequence in fixture_module.SEQUENCES.items():
        result=dict(name=name,expected_sequence=sequence,result='FAIL')
        try:
            batches=[b for b in states if b['case']==name]
            require(len(batches)==1,'Missing unique transition observation')
            rows=batches[0]['samples']
            result['observed_formats']=sorted({s['format'] for s in rows if s['audio']})
            result['observations']=len(rows)
            result['stopped_samples']=sum(s['audio'] is False for s in rows)
            check_transitions(rows,[specs[n] for n in sequence]);result['result']='PASS'
        except Exception as e:result['reason']=str(e)
        summary['transition_replay'].append(result)
(dst/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
checks={p.relative_to(dst).as_posix():sha(p) for p in sorted(dst.rglob('*')) if p.is_file()}
(dst/'sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('idle','failed_request_phases')}))
