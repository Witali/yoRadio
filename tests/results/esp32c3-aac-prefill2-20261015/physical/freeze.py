import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-aac-prefill2-20261015')
src=base/'tls-pauses/pauses'
dst=Path('tests/results/esp32c3-aac-prefill2-20261015/physical')
r=json.loads((src/'report.json').read_text())
c=json.loads((base/'tls-pauses/controller.json').read_text())
assert any(x['name']=='all-decoder-health' for x in r['cases'])
assert c['restored']['stopped'] and all(c['restored']['settings'].values())
assert c['restored']['identity']['app_elf_sha256']==c['original']['app_elf_sha256']
assert not dst.exists(),'Preserve evidence'
shutil.copytree(src,dst)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for source,name in [('tls-pauses/controller.json','deployment.json'),('deploy.py','deployment.py'),
                    ('run-pauses.py','controller.py'),('audit.py','audit.py'),('freeze.py','freeze.py')]:
    shutil.copyfile(base/source,dst/name)
assert sha(dst/'deployment.py')==c['controller_sha256']
previous=Path('tests/results/esp32c3-confirm-tls-lab-20261015/physical/test-source-reference.json')
old=json.loads(previous.read_text());mapping={}
for name,digest in r['test_sources_sha256'].items():
    saved=Path(old[name]['path']) if name in old else Path(name)
    if name not in old or not saved.is_file() or sha(saved)!=digest:
        p=Path(name);assert sha(p)==digest,name
        saved=dst/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
(dst/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
shutil.copyfile('firmware/development/esp32c3-idf61-aac-prefill2-lab/manifest.json',dst/'firmware-manifest.json')
fixture=Path('tests/results/esp32c3-aac-pause-ab-20261014/fixtures/aac-lc-44100-128k.aac')
assert sha(fixture)==r['fixture']['sha256']
(dst/'fixture-reference.json').write_text(json.dumps(dict(path=fixture.as_posix(),sha256=sha(fixture)),indent=2)+'\n')
source_manifest=Path('.build/c3-aac-pause-ab-20261014/fixtures/manifest.json')
assert sha(source_manifest)==r['fixture_manifest_sha256']
shutil.copyfile(source_manifest,dst/'fixture-manifest.json')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dst/'sha256.json').write_text(json.dumps({p.relative_to(dst).as_posix():sha(p) for p in sorted(dst.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Frozen TLS pause result')
