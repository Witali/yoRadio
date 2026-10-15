import hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from production_health import check_health,check_decoder_health
base=Path('.build/c3-raw-tail-quiet-20261015');src=base/'final-deployment-repeat'
out=Path('tests/results/esp32c3-raw-tail-quiet-20261015/final-deployment')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((src/'controller.json').read_text());r=json.loads((src/'smoke/report.json').read_text())
assert 'failure' not in c and c['final']['stopped'] and all(c['final']['settings'].values())
assert c['final']['identity']['app_elf_sha256']==c['candidate']['app_elf_sha256']
assert len(r['cases'])==6 and all(case['result']=='PASS' for case in r['cases'])
assert sha(base/'final-deploy-v2.py')==c['controller_sha256']
assert sha(base/'final-smoke-v2.py')==c['smoke_sha256']
assert not out.exists();shutil.copytree(src,out)
old=json.loads(Path('tests/results/esp32c3-input-tail-quiet-20261015/network/network/test-source-reference.json').read_text())
mapping={}
for name,digest in r['test_sources_sha256'].items():
    p=Path(name);assert sha(p)==digest
    saved=Path(old[name]['path']) if name in old else out/'smoke/sources'/name
    if not saved.is_file() or sha(saved)!=digest:
        saved=out/'smoke/sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
(out/'smoke/test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
health=json.loads((src/'smoke/health.json').read_text())
(out/'audit.json').write_text(json.dumps(dict(checks=6,result='PASS',health=check_health(health),
    decoder=check_decoder_health(health),final=c['final']),indent=2)+'\n')
for name in ('final-deploy-v2.py','final-smoke-v2.py','freeze-final.py','check-guide.ps1'):
    shutil.copyfile(base/name,out/name)
shutil.copyfile('idf/esp32c3-oled-native/build-raw-tail-quiet-20261015/flasher_args.json',out/'build-flasher-args.json')
(out/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(out/'sha256.json').write_text(json.dumps({p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()},indent=2)+'\n')
print((out/'audit.json').read_text())
