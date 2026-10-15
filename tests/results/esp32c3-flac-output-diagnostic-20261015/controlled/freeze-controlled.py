import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-flac-output-diagnostic-20261015');src=base/'controlled'
dest=Path('tests/results/esp32c3-flac-output-diagnostic-20261015/controlled')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
control=json.loads((src/'controller.json').read_text())
assert control['restored']['stopped'] and 'restoration_failure' not in control
assert all(control['restored']['settings'].values())
assert control['restored']['identity']['app_elf_sha256']==control['original']['app_elf_sha256']
audit=json.loads((src/'pipeline-audit.json').read_text())
assert not dest.exists();shutil.copytree(src,dest)
old=json.loads(Path('tests/results/esp32c3-flac-output-diagnostic-20261015/physical/flac-1/test-source-reference.json').read_text())
for item in control['tests']:
    folder=dest/item['suite'];r=json.loads((folder/'report.json').read_text());mapping={}
    assert any(c['name']=='decoder' for c in r['cases'])
    assert sha(base/'run-controlled.py')==r['runner_sha256']
    for name,digest in r['test_sources_sha256'].items():
        saved=Path(old[name]['path']) if name in old else folder/'sources'/name
        if not saved.is_file() or sha(saved)!=digest:
            assert sha(Path(name))==digest,name
            saved=folder/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,saved)
        mapping[name]=dict(path=saved.as_posix(),sha256=digest)
    (folder/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
for name in ('deploy-controlled.py','run-controlled.py','analyze-controlled.py','freeze-controlled.py'):shutil.copyfile(base/name,dest/name)
assert sha(base/'deploy-controlled.py')==control['controller_sha256']
artifact=Path('firmware/development/esp32c3-idf61-flac-output-diagnostic')
m=json.loads((artifact/'manifest.json').read_text())
m['qualification']='Diagnostic public FLAC 24/24. Local unpaced control 8/8; imposed 0.25/0.5-second pauses cause 4/26 completion drops with input starvation. Original quiet HTTPS cause remains unproven.'
m['controlled_evidence']=dest.as_posix()
(artifact/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
shutil.copyfile(artifact/'manifest.json',dest/'firmware-manifest.json')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved baseline and failed controlled-pause evidence, including restoration')
