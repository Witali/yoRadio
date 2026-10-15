import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-decode-probe-20261015');src=base/'physical'
dest=Path('tests/results/esp32c3-decode-probe-20261015/physical')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((src/'controller.json').read_text())
assert c['restored']['stopped'] and 'restoration_failure' not in c
assert all(c['restored']['settings'].values())
assert c['restored']['identity']['app_elf_sha256']==c['original']['app_elf_sha256']
assert (src/'work-inspection.json').is_file()
assert not dest.exists();shutil.copytree(src,dest)
old=json.loads(Path('tests/results/esp32c3-read25-20261015/physical/read250/control/test-source-reference.json').read_text())
assert sha(base/'deploy.py')==c['controller_sha256']
for p in dest.rglob('report.json'):
    r=json.loads(p.read_text());assert sha(base/'run.py')==r['runner_sha256'];mapping={}
    for name,digest in r['test_sources_sha256'].items():
        saved=Path(old[name]['path']) if name in old else dest/'sources'/name
        if not saved.is_file() or sha(saved)!=digest:
            assert sha(Path(name))==digest,name
            saved=dest/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,saved)
        mapping[name]=dict(path=saved.as_posix(),sha256=digest)
    (p.parent/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
for name in ('deploy.py','run.py','summarize.py','freeze-physical.py','inspect-work.py'):
    shutil.copyfile(base/name,dest/name)
for name in ('common.py','ota.py'):
    saved=dest/'controller-sources'/name;saved.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(Path('tools/esp32c3_tests')/name,saved)
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved physical trials and restoration evidence')
