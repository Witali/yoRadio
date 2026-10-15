import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-input-tail-quiet-20261015');src=base/'https-radio/public-radio'
dst=Path('tests/results/esp32c3-input-tail-quiet-20261015/public-radio')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((src/'report.json').read_text());c=json.loads((base/'https-radio/controller.json').read_text())
assert any(x['name']=='all-decoder-health' for x in r['cases'])
assert c['restored']['stopped'] and all(c['restored']['settings'].values())
assert c['restored']['identity']['app_elf_sha256']==c['original']['app_elf_sha256']
assert not dst.exists();shutil.copytree(src,dst)
for name,target in [('deploy-radio.py','deployment.py'),('run-radio.py','runner.py'),('audit-radio.py','audit-radio.py'),('freeze-radio.py','freeze-radio.py'),('https-radio/controller.json','deployment.json')]:
    shutil.copyfile(base/name,dst/target)
assert sha(dst/'deployment.py')==c['controller_sha256']
old=json.loads(Path('tests/results/esp32c3-input-tail-quiet-20261015/physical/http/test-source-reference.json').read_text());mapping={}
for name,digest in r['test_sources_sha256'].items():
    saved=Path(old[name]['path']) if name in old else Path(name)
    if name not in old or not saved.exists() or sha(saved)!=digest:
        p=Path(name);assert sha(p)==digest,name
        saved=dst/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
(dst/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
shutil.copyfile('firmware/development/esp32c3-idf61-input-tail-quiet/manifest.json',dst/'firmware-manifest.json')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dst/'sha256.json').write_text(json.dumps({p.relative_to(dst).as_posix():sha(p) for p in sorted(dst.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Public result and original restoration archived')
