import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import check_natural_eof,check_playback,check_recovery_heap,fixtures,require
from production_health import check_health,check_decoder_health
from run import check_file_output
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
base=Path('.build/c3-input-tail-quiet-20261015');src=base/'physical/http'
dst=Path('tests/results/esp32c3-input-tail-quiet-20261015/physical/http')
r=json.loads((src/'report.json').read_text());assert any(c['name']=='all-decoder-health' for c in r['cases'])
assert not dst.exists();shutil.copytree(src,dst)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reference=Path('tests/results/esp32c3-production-qualification-20261014/flac-600-01');mapping={}
for name,digest in r['test_sources_sha256'].items():
    p=Path(name);assert sha(p)==digest,name
    saved=reference/'sources'/name
    if not saved.is_file() or sha(saved)!=digest:
        saved=dst/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
for name in ('test-quiet-file-gates.py','test-production-health.py','test-sustained-output.py'):
    saved=dst/'sources/tests'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Path('tests')/name,saved)
(dst/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
shutil.copyfile(base/'run-candidate.py',dst/'controller.py');shutil.copyfile(base/'freeze-http.py',dst/'freeze.py')
shutil.copyfile('firmware/development/esp32c3-idf61-input-tail-quiet/manifest.json',dst/'firmware-manifest.json')
specs=fixtures();expected=[f'http:{name}:{hint}' for name,spec in specs.items() if name not in fixture_module.SEQUENCES for hint in ('auto',spec['codec'])]
states=json.loads((src/'status.json').read_text());health=json.loads((src/'health.json').read_text());cases={c['name']:c for c in r['cases']};actions={a['name']:a for a in r['actions']}
audits=[]
for i,name in enumerate(expected):
    result=dict(name=name,result='FAIL')
    try:
        require(cases[name]['result']=='PASS','Original file case failed')
        a=actions[name];fixture=name.split(':')[1]
        batches=[s for s in states if a['started_at']<=s['started_at'] and s['ended_at']<=a['ended_at']]
        require(len(batches)==2,'Missing playback/EOF batches')
        rows=[h for h in health if a['started_at']<=h['at']<=a['ended_at']]
        result['format']=check_playback(batches[0]['samples'],specs[fixture])
        result['eof']=check_natural_eof(batches[1]['samples'])
        result['decoder']=check_decoder_health(rows)
        play_rows=[h for h in rows if batches[0]['started_at']<=h['at']<=batches[0]['ended_at']]
        result['output']=check_file_output(batches[0]['samples'],play_rows)
        event=r['server_events'][i]
        require(event['fixture']==fixture and event['complete'] and event['sent']==len(specs[fixture]['data']),'Incomplete or wrong server delivery')
        result['terminal_health']=rows[-3:]
        result['result']='PASS'
        try:
            check_recovery_heap(r['idle']['initial'],rows[-3:]);result['natural_eof_recovery']='PASS'
        except Exception as e:
            result['natural_eof_recovery']='FAIL';result['natural_eof_recovery_reason']=str(e)
    except Exception as e:
        result['reason']=str(e)
    audits.append(result)
summary=dict(image=r['image'],counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},expected_file_cases=len(expected),audits=audits,idle=r['idle'],scope=r['scope'])
summary['health']=check_health(health);summary['decoder_health']=check_decoder_health(health)
summary['failed_requests']=[json.loads(line) for line in (src/'request-phases.jsonl').read_text().splitlines() if json.loads(line)['result']!='PASS']
summary['server_event_count']=len(r['server_events'])
summary['natural_eof_recovery_failures']=sum(a.get('natural_eof_recovery')!='PASS' for a in audits)
(dst/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
checks={p.relative_to(dst).as_posix():sha(p) for p in sorted(dst.rglob('*')) if p.is_file()}
(dst/'sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('audits','idle')}))
