"""Freeze and replay the completed A/B/A experiment without dropping failures."""
import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require,check_playback,check_recovery_heap
from local_sustained import check_delivery_pauses
from production_health import check_health,check_decoder_health,output_window
from sustained_output import sustained_window
base=Path('.build/c3-aac-pause-ab-20261014')
dest=Path('tests/results/esp32c3-aac-pause-ab-20261014')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
control=json.loads((base/'controller-02.json').read_text())
require(control['restored']['stopped'] and 'restoration_failure' not in control,'Missing restoration')
require(control['restored']['identity']['app_elf_sha256']==control['images']['baseline']['app_elf_sha256'],'Wrong restored firmware')
require(all(control['restored']['settings'].values()),'Settings changed')
require(not dest.exists(),'Preserve archived evidence');dest.mkdir()
schedule=json.loads((base/'fixtures/schedule.json').read_text())
manifest=json.loads((base/'fixtures/manifest.json').read_text());spec=manifest['fixtures'][0]
require(sha(base/'fixtures'/spec['file'])==spec['sha256'],'Fixture changed')
summary=dict(images=control['images'],schedule=schedule,runs=[],restored=True,
             scope='Controlled HTTP A/B/A with one synthetic AAC-LC file; does not establish the cause of the public HTTPS failure')
reference=json.loads(Path('tests/results/esp32c3-stream-confirm-continuous-20261014/https-radio-01/test-source-reference.json').read_text())
mapping={}
for run in control['runs']:
    name=run['name'];src=base/name
    if not (src/'report.json').exists():continue
    shutil.copytree(src,dest/name)
    r=json.loads((src/'report.json').read_text());health=json.loads((src/'health.json').read_text());states=json.loads((src/'status.json').read_text())
    require(r['fixture']['sha256']==spec['sha256'],'Mismatched fixture')
    expected=control['images']['candidate' if name=='candidate' else 'baseline']
    require(r['image']==expected and r['image']['app_elf_sha256']==run['installation']['identity']['app_elf_sha256'],'Mismatched image')
    row=dict(name=name,counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
             failures=[c for c in r['cases'] if c['result']!='PASS'],replay='FAIL')
    try:
        batch=next(s for s in states if s['case']==spec['name'])
        observed=[h for h in health if batch['started_at']<=h['at']<=batch['ended_at']]
        _,steady=sustained_window(batch['samples'],observed,r['observation_seconds'])
        row['format']=check_playback(batch['samples'],spec,minimum=int((r['observation_seconds']-15)*.6),warmup=15)
        row['output']=output_window(steady)
        row['health']=check_health(health);row['decoder_health']=check_decoder_health(health)
        row['pauses']=check_delivery_pauses(r['server_events'],spec['name'],schedule)
        check_recovery_heap(r['idle']['initial'],r['idle']['final']);row['recovery']='PASS'
        row['output_increments']=[dict(from_seconds=a['at']-batch['started_at'],to_seconds=b['at']-batch['started_at'],
                 **output_window([a,b])) for a,b in zip(steady,steady[1:]) if a['output']!=b['output']]
        row['send_buffer_actual']=r['server_events'][0]['send_buffer_actual']
        row['replay']='PASS' # Replay success does not turn nonzero output counters into acceptance.
    except Exception as e:row['replay_reason']=str(e)
    summary['runs'].append(row)
    for source,digest in r['test_sources_sha256'].items():
        saved=Path(reference[source]['path']) if source in reference else Path(source)
        if source not in reference or not saved.exists() or sha(saved)!=digest:
            require(sha(Path(source))==digest,'Changed source '+source)
            saved=dest/'sources'/source;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,saved)
        mapping[source]=dict(path=saved.as_posix(),sha256=digest)
for name in ('controller.json','controller-02.json','deploy.py','run.py','make-fixture.py','freeze.py'):
    shutil.copyfile(base/name,dest/name)
require(sha(dest/'deploy.py')==control['controller_sha256'],'Controller source changed')
shutil.copytree(base/'fixtures',dest/'fixtures')
for name in ('test-local-sustained-pauses.py','test-audio-server-pauses.py'):
    saved=dest/'sources/tests'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Path('tests')/name,saved)
(dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(dest/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
checks={p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(summary))
