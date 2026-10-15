"""Archive completed evidence and exact sources; retain every failed gate."""
import hashlib,json,shutil,sys
from pathlib import Path
base=Path('.build/c3-flac-input12-20261015');campaign=sys.argv[1]
src=base/campaign;dest=Path('tests/results/esp32c3-flac-input12-20261015')/campaign
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((src/'controller.json').read_text())
assert c['restored']['stopped'] and 'restoration_failure' not in c
assert all(c['restored']['settings'].values())
assert c['restored']['identity']['app_elf_sha256']==c['original']['app_elf_sha256']
assert (src/'summary.json').is_file()
assert not dest.exists();shutil.copytree(src,dest)
old=json.loads(Path('tests/results/esp32c3-flac-output-diagnostic-20261015/physical/flac-1/test-source-reference.json').read_text())
runner='run-matched.py' if campaign=='matched' else 'run-controlled.py'
controller='deploy-matched.py' if campaign=='matched' else 'deploy-controlled.py'
assert sha(base/controller)==c['controller_sha256']
for p in dest.rglob('report.json'):
    r=json.loads(p.read_text());assert sha(base/runner)==r['runner_sha256'];mapping={}
    for name,digest in r['test_sources_sha256'].items():
        saved=Path(old[name]['path']) if name in old else p.parent/'sources'/name
        if not saved.is_file() or sha(saved)!=digest:
            assert sha(Path(name))==digest,name
            saved=p.parent/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,saved)
        mapping[name]=dict(path=saved.as_posix(),sha256=digest)
    (p.parent/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
for name in (runner,controller,'summarize.py','freeze-campaign.py'):
    shutil.copyfile(base/name,dest/name)
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved',campaign,'with verified restoration and exact sources')
