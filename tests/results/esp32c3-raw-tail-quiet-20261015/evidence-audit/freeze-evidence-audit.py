import hashlib,json,shutil,subprocess
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015');source=base/'evidence-audit'
dest=Path('tests/results/esp32c3-raw-tail-quiet-20261015/evidence-audit')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
first=json.loads((source/'report.json').read_text());retry=json.loads((source/'retry-asymmetric.json').read_text())
assert first['same_codec_archive'] and retry['exit_code']==0
for test in first['tests']:
    assert sha(Path(test['path']))==test['sha256']
    if test['exit_code']:
        assert test['path']==retry['test'] and test['sha256']==retry['test_sha256']
assert json.loads((source/'sdk-pcm.json').read_text())['passed']
assert not dest.exists();shutil.copytree(source,dest)
for name in ('audit-evidence.py','retry-evidence.py','compare-aac-sources.py','audit-sdk-pcm.py','freeze-evidence-audit.py'):
    shutil.copyfile(base/name,dest/name)
refs={}
for test in first['tests']:
    saved=dest/'sources'/test['path'];saved.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(test['path'],saved)
    refs[test['path']]=dict(path=saved.as_posix(),sha256=test['sha256'])
(dest/'test-source-reference.json').write_text(json.dumps(refs,indent=2)+'\n')
(dest/'resolution.json').write_text(json.dumps(dict(
    result='PASS after exact LFS artifact hydration',
    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    scope='Four evidence/policy test entrypoints (24 checks), archived pinned-SDK PCM recomputation. Original missing-LFS dependency failure retained. Not a fresh decoder or physical run.'),indent=2)+'\n')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved evidence audit, source differences, retained dependency failure and successful retry')
