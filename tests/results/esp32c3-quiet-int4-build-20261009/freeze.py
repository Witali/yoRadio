import hashlib
import json
from pathlib import Path
import re
import shutil

root = Path(__file__).resolve().parent
repo = root.parents[1]
out = repo/'tests/results/esp32c3-quiet-int4-build-20261009'
artifact = repo/'firmware/development/esp32c3-idf-6.1-r9a97-quiet-int4'
assert not out.exists()
audit = json.loads((root/'build-audit.json').read_text())
codecs = json.loads((root/'codec-objects.json').read_text())
assert audit['result'] == codecs['result'] == 'PASS'
manifest = json.loads((artifact/'manifest.json').read_text())
manifest['codec_object_comparison'] = dict(result='PASS', baseline='r9a97-quiet-min250',
    objects=codecs['objects'], text_rodata_sections=codecs['sections'],
    evidence='tests/results/esp32c3-quiet-int4-build-20261009/codec-objects.json')
(artifact/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
out.mkdir()
for path in sorted(root.glob('*')):
    if not path.is_file(): continue
    assert not re.search(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----', path.read_bytes())
    shutil.copyfile(path, out/path.name)
for relative, digest in manifest['source_overlay_sha256'].items():
    path = repo/relative
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    target = out/'sources'/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(path,target)
files = {p.relative_to(out).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
         for p in sorted(out.rglob('*')) if p.is_file()}
(out/'index.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
print(len(files),'files;',sum(v['bytes'] for v in files.values()),'bytes')
