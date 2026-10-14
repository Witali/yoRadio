import argparse,hashlib,json,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--fixture-manifest',type=Path,required=True);p.add_argument('--controller',type=Path,required=True);a=p.parse_args()
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
reference=Path('tests/results/esp32c3-production-qualification-20261014/flac-600-01')
reference_report=json.loads((reference/'report.json').read_text())
assert r['test_sources_sha256']==reference_report['test_sources_sha256'], 'Test source set differs'
for name,digest in r['test_sources_sha256'].items():
    assert sha(Path(name))==digest,name
    assert sha(reference/'sources'/name)==digest,name
reference_info=dict(archive=reference.as_posix(),report_sha256=sha(reference/'report.json'),sources=r['test_sources_sha256'])
(dst/'test-source-reference.json').write_text(json.dumps(reference_info,indent=2)+'\n')
shutil.copyfile(base/'freeze.py',dst/'freeze.py')
shutil.copyfile(a.controller,dst/'controller.py')
shutil.copyfile('firmware/development/esp32c3-idf61-production-20261013/manifest.json',dst/'firmware-manifest.json')
(dst/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
summary=dict(image=r['image'],counts={s:sum(c['result']==s for c in r['cases']) for s in ('PASS','FAIL','BLOCKED')},cases=r['cases'],idle=r.get('idle'),initial_status=r['initial_status'],scope=r['scope'])
(dst/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
checks={f.relative_to(dst).as_posix():sha(f) for f in sorted(dst.rglob('*')) if f.is_file()}
(dst/'sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(summary))
