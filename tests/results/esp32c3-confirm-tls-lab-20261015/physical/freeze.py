"""Freeze completed TLS-record evidence and replay independent gates."""
import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require,fixtures,matches,check_recovery_heap
from production_health import check_health,check_decoder_health
from sustained_output import sustained_window,check_memory,check_output
from quiet_tls_records import check_record_window,check_format,check_response
from pipeline_probe import analyze_pipeline
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')

base=Path('.build/c3-confirm-tls-lab-20261015')
src=base/'controlled-tls/records'
root=Path('tests/results/esp32c3-confirm-tls-lab-20261015')
dst=root/'physical'
r=json.loads((src/'report.json').read_text());c=json.loads((base/'controlled-tls/controller.json').read_text())
require(any(x['name']=='lifetime-health' for x in r['cases']),'Unfinished campaign')
require(c['restored']['stopped'] and all(c['restored']['settings'].values()),'Missing restoration')
require(c['restored']['identity']['app_elf_sha256']==c['original']['app_elf_sha256'],'Wrong restored image')
require(not dst.exists(),'Preserve evidence')
shutil.copytree(src,dst)
for source,name in [('controlled-tls/controller.json','deployment.json'),('deploy.py','deployment.py'),
                    ('run-records.py','controller.py'),('freeze.py','freeze.py')]:
    shutil.copyfile(base/source,dst/name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
require(sha(dst/'deployment.py')==c['controller_sha256'],'Changed controller')
old=json.loads(Path('tests/results/esp32c3-confirm-quiet-long-20261014/physical/test-source-reference.json').read_text())
mapping={}
for name,digest in r['test_sources_sha256'].items():
    saved=Path(old[name]['path']) if name in old else Path(name)
    if name not in old or not saved.is_file() or sha(saved)!=digest:
        p=Path(name);require(sha(p)==digest,'Changed source: '+name)
        saved=dst/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
(dst/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
shutil.copyfile('firmware/development/esp32c3-idf61-confirm-tls-lab/manifest.json',dst/'firmware-manifest.json')
states=json.loads((src/'status.json').read_text());health=json.loads((src/'health.json').read_text())
specs=fixtures();summary=dict(image=r['image'],diagnostic_only=True,
    counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
    failures=[c for c in r['cases'] if c['result']!='PASS'],windows={},recovery={})
def evaluate(fn):
    try:return dict(result='PASS',evidence=fn())
    except Exception as error:return dict(result='FAIL',reason=str(error))
summary['health']=evaluate(lambda:check_health(health))
summary['decoder']=evaluate(lambda:check_decoder_health(health))
for batch in states:
    if batch['case'].startswith('idle:'):continue
    key=batch['case'];name,mode=key.split(':');spec=specs[name]
    rows=[x for x in health if batch['started_at']<=x['at']<=batch['ended_at']]
    steady,measured=sustained_window(batch['samples'],rows,r['seconds'])
    window=dict(last_seconds=batch['samples'][-1]['seconds'])
    observation=r['record_observations'][key]
    first=next((batch['started_at']+s['seconds'] for s in batch['samples'] if matches(s,spec)),float('inf'))
    for check,fn in [('format',lambda:check_format(batch['samples'],spec,r['seconds'])),
        ('records',lambda:check_record_window(observation,mode,spec,first,observation['captured_at'])),
        ('output',lambda:check_output(measured)),('memory',lambda:check_memory(measured)),
        ('response',lambda:check_response(batch['samples'])),('pipeline',lambda:analyze_pipeline(measured))]:
        window[check]=evaluate(fn)
    summary['windows'][key]=window
for key,rows in r['idle'].items():
    if key!='initial':summary['recovery'][key]=evaluate(lambda:check_recovery_heap(r['idle']['initial'],rows))
summary['failed_request_phases']=[json.loads(line) for line in (src/'request-phases.jsonl').read_text().splitlines()
    if json.loads(line)['result']!='PASS']
(dst/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dst/'sha256.json').write_text(json.dumps({p.relative_to(dst).as_posix():sha(p) for p in sorted(dst.rglob('*')) if p.is_file()},indent=2)+'\n')
print(json.dumps(dict(counts=summary['counts'],failures=summary['failures'],
    windows={key:{k:v for k,v in value.items() if k!='pipeline'} for key,value in summary['windows'].items()})))
