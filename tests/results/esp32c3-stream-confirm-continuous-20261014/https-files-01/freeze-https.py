"""Archive the finished public-file campaign, including its unrepaired failure."""
import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-continuous-confirm-20261014')
src=base/'https';dest=Path('tests/results/esp32c3-stream-confirm-continuous-20261014/https-files-01')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
control=json.loads((src/'controller.json').read_text())
assert control['restored']['stopped'] and 'restoration_failure' not in control
assert control['restored']['identity']['app_elf_sha256']==control['original']['app_elf_sha256']
assert all(control['restored']['settings'].values())
assert not dest.exists();shutil.copytree(src,dest)
r=json.loads((src/'public-files/report.json').read_text())
assert any(c['name']=='all-decoder-health' for c in r['cases'])
old=json.loads(Path('tests/results/esp32c3-stream-confirm-continuous-20261014/physical/http/test-source-reference.json').read_text())
mapping={}
for name,digest in r['test_sources_sha256'].items():
    saved=Path(old[name]['path']) if name in old else Path(name)
    if name not in old or not saved.is_file() or sha(saved)!=digest:
        source=Path(name);assert sha(source)==digest,name
        saved=dest/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,saved)
    mapping[name]=dict(path=saved.as_posix(),sha256=digest)
(dest/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
for name in ('run-https.py','deploy-https-restore.py','audit-https-files.py','freeze-https.py'):
    shutil.copyfile(base/name,dest/name)
assert sha(base/'deploy-https-restore.py')==control['controller_sha256']
shutil.copyfile(base/'public-references/references.json',dest/'reference-manifest.json')
shutil.copyfile('firmware/development/esp32c3-idf61-continuous-confirm/manifest.json',dest/'firmware-manifest.json')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
checks={p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'sha256.json').write_text(json.dumps(checks,indent=2)+'\n')
print('Archived HTTPS campaign and verified original image/settings restoration')
