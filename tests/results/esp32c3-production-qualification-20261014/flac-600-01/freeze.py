import argparse,hashlib,json,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--fixture-manifest',type=Path,required=True);a=p.parse_args()
base=Path('.build/c3-production-qualification-20261014')
src=base/a.run; dst=Path('tests/results/esp32c3-production-qualification-20261014')/a.run
r=json.loads((src/'report.json').read_text())
assert any(c['name']=='stop-and-settings' for c in r['cases']), 'Controller not terminal'
assert any(c['name']=='all-decoder-health' for c in r['cases']), 'Missing final health'
assert not dst.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a.fixture_manifest)==r['fixture_manifest_sha256']
shutil.copytree(src,dst)
shutil.copyfile(a.fixture_manifest,dst/'fixture-manifest.json')
for name,digest in r['test_sources_sha256'].items():
    path=Path(name); assert sha(path)==digest,name
    target=dst/'sources'/name; target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
for name in ('test-sustained-output.py','test-production-health.py'):
    target=dst/'sources/tests'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Path('tests')/name,target)
shutil.copyfile(base/'freeze.py',dst/'freeze.py')
shutil.copyfile(base/'run-flac.py',dst/'controller.py')
shutil.copyfile('firmware/development/esp32c3-idf61-production-20261013/manifest.json',dst/'firmware-manifest.json')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
summary=dict(image=r['image'],counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},cases=r['cases'],idle=r.get('idle'),initial_status=r['initial_status'],scope=r['scope'])
(dst/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
checks={f.relative_to(dst).as_posix():sha(f) for f in sorted(dst.rglob('*')) if f.is_file()}
(dst/'sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(summary))
