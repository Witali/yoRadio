import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require,check_recovery_heap
from production_health import check_health,check_decoder_health,output_window
base=Path('.build/c3-input-tail-quiet-20261015');src=base/'network'
dest=Path('tests/results/esp32c3-input-tail-quiet-20261015/network')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
control=json.loads((src/'controller.json').read_text())
require(control['restored']['stopped'] and 'restoration_failure' not in control,'Restoration incomplete')
require(all(control['restored']['settings'].values()),'Settings changed')
require(control['restored']['identity']['app_elf_sha256']==control['original']['app_elf_sha256'],'Wrong restored image')
require(not dest.exists(),'Preserve archive');shutil.copytree(src,dest)
old=json.loads(Path('tests/results/esp32c3-input-tail-quiet-20261015/physical/http/test-source-reference.json').read_text())
summary=[]
for item in control['tests']:
    suite=item['suite'];folder=dest/suite
    r=json.loads((folder/'report.json').read_text());hs=json.loads((folder/'health.json').read_text())
    require(any(c['name']=='all-decoder-health' for c in r['cases']),'Incomplete suite')
    mapping={}
    for name,digest in r['test_sources_sha256'].items():
        p=Path(name);require(sha(p)==digest,'Source changed during test: '+name)
        saved=Path(old[name]['path']) if name in old else folder/'sources'/name
        if not saved.is_file() or sha(saved)!=digest:
            saved=folder/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
        mapping[name]=dict(path=saved.as_posix(),sha256=digest)
    (folder/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
    row=dict(suite=suite,counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
        failures=[c for c in r['cases'] if c['result']!='PASS'],output_windows=[],idle=r['idle'])
    for name,fn in (('health',check_health),('decoder',check_decoder_health)):
        try:row[name]=dict(result='PASS',evidence=fn(hs))
        except Exception as e:row[name]=dict(result='FAIL',reason=str(e))
    for name,rs in r['idle'].items():
        if name=='initial':continue
        try:check_recovery_heap(r['idle']['initial'],rs);row['recovery']='PASS'
        except Exception as e:row['recovery']=str(e)
    for batch in json.loads((folder/'status.json').read_text()):
        name=batch['case']
        if not (suite=='transitions' and not name.startswith('idle:') or name.startswith('recovered:') or name=='ws-warmup'):continue
        measured=[h for h in hs if batch['started_at']<=h['at']<=batch['ended_at']]
        states=batch['samples'];window=dict(case=name)
        try:
            require(len(states)==len(measured),'Unpaired observations')
            pairs=[(s,h) for s,h in zip(states,measured) if s['seconds']>=2]
            require(len(pairs)>=5 and all(s['audio'] and s['pcm_sample_rate']>0 for s,h in pairs),'Missing continuous decoded state')
            window['measurement']=output_window([h for s,h in pairs])
        except Exception as e:window['unavailable']=str(e)
        row['output_windows'].append(window)
    row['failed_requests']=[json.loads(line) for line in (folder/'request-phases.jsonl').read_text().splitlines() if json.loads(line)['result']!='PASS']
    summary.append(row)
(dest/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
for name in ('deploy-network.py','run-network.py','freeze-network.py'):shutil.copyfile(base/name,dest/name)
require(sha(base/'deploy-network.py')==control['controller_sha256'],'Controller changed')
shutil.copyfile('firmware/development/esp32c3-idf61-input-tail-quiet/manifest.json',dest/'firmware-manifest.json')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print(json.dumps(summary))
