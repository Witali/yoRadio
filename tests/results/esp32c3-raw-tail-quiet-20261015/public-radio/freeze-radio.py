import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
from production_health import check_health,check_decoder_health
from review_finite_memory import review
base=Path('.build/c3-raw-tail-quiet-20261015');src=base/'https-radio'
dest=Path('tests/results/esp32c3-raw-tail-quiet-20261015/public-radio')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
control=json.loads((src/'controller.json').read_text())
require(control['restored']['stopped'] and 'restoration_failure' not in control,'Restoration incomplete')
require(all(control['restored']['settings'].values()),'Settings changed')
require(control['restored']['identity']['app_elf_sha256']==control['original']['app_elf_sha256'],'Wrong restored image')
require(not dest.exists(),'Preserve archive');shutil.copytree(src,dest)
old=json.loads(Path('tests/results/esp32c3-input-tail-quiet-20261015/network/network/test-source-reference.json').read_text())
summary=[]
for item in control['tests']:
    suite=item['suite'];folder=dest/suite
    r=json.loads((folder/'report.json').read_text())
    mapping={}
    for name,digest in r['test_sources_sha256'].items():
        p=Path(name);require(sha(p)==digest,'Source changed during test: '+name)
        saved=Path(old[name]['path']) if name in old else folder/'sources'/name
        if not saved.is_file() or sha(saved)!=digest:
            saved=folder/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
        mapping[name]=dict(path=saved.as_posix(),sha256=digest)
    (folder/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
    row=dict(suite=suite,counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},
        failures=[c for c in r['cases'] if c['result']!='PASS'])
    if suite=='public-files':
        audited=review(folder);(folder/'review.json').write_text(json.dumps(audited,indent=2)+'\n')
    if (folder/'health.json').exists():
        hs=json.loads((folder/'health.json').read_text())
        for name,fn in (('health',check_health),('decoder',check_decoder_health)):
            try:row[name]=dict(result='PASS',evidence=fn(hs))
            except Exception as e:row[name]=dict(result='FAIL',reason=str(e))
        row['failed_requests']=[json.loads(line) for line in (folder/'request-phases.jsonl').read_text().splitlines() if json.loads(line)['result']!='PASS']
    summary.append(row)
(dest/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
for name in ('deploy-radio.py','run-radio.py','freeze-radio.py'):shutil.copyfile(base/name,dest/name)
require(sha(base/'deploy-radio.py')==control['controller_sha256'],'Controller changed')
shutil.copyfile(Path('.build/c3-input-tail-quiet-20261015/public-references/references.json'),dest/'reference-manifest.json')
manifest=Path('firmware/development/esp32c3-idf61-raw-tail-quiet/manifest.json')
m=json.loads(manifest.read_text());m['hardware_tested']=True
m['public_radio_evidence']=dest.as_posix()
m['qualification']='See retained physical qualification reports. Full goal completion remains subject to all playback, continuity and OTA evidence; previous failures remain recorded.'
manifest.write_text(json.dumps(m,indent=2)+'\n')
shutil.copyfile(manifest,dest/'firmware-manifest.json')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print(json.dumps(summary))
