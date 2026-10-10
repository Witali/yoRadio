"""Freeze references to the already-qualified normal-trust candidate."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path('.build/c3-prefill1000-public-20261010')
PREVIOUS = Path('tests/results/esp32c3-prefill1000-quiet-20261010')
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000')
assert not ROOT.exists()
manifest = json.loads((ART / 'manifest.json').read_text())
assert manifest['image']['sha256'] == hashlib.sha256((ART / 'app.bin').read_bytes()).hexdigest()
assert manifest['image']['sha256'] == 'e15c8a37a9c06a069e8146b00e305cb5aa176a52cfa4a1d7381fd8d9dca6754a'
assert manifest['production_profile'] and not manifest['lab_ca']
ROOT.mkdir()
for name in ('quiet-prefill1000/build-audit.json', 'laboratory-comparison.json', 'review.json'):
    source = PREVIOUS / name
    dest = ROOT / 'prior-build' / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(source.read_bytes())
(ROOT / 'prior-build/evidence-reference.json').write_text(json.dumps(dict(
    archive=PREVIOUS.as_posix(), index_sha256=hashlib.sha256((PREVIOUS / 'index.json').read_bytes()).hexdigest(),
    artifact=ART.as_posix(), manifest_sha256=hashlib.sha256((ART / 'manifest.json').read_bytes()).hexdigest()), indent=2) + '\n')
(ROOT / 'firmware-manifest-before.json').write_bytes((ART / 'manifest.json').read_bytes())
shutil.copyfile('.build/c3-quiet-health-20261010/faad-reference-command.json', ROOT / 'faad-reference-command.json')
shutil.copyfile('tools/esp32c3_tests/public_streams.json', ROOT / 'public_streams.json')
reference = Path('C:/Work/yoRadio/.worktree/esp32c3-stream-format/.build/faad2-comparison/probe-float')
assert reference.is_file()
(ROOT / 'reference-tool.json').write_text(json.dumps(dict(path=reference.as_posix(),
    sha256=hashlib.sha256(reference.read_bytes()).hexdigest(), bytes=reference.stat().st_size), indent=2) + '\n')
shutil.copyfile(__file__, ROOT / 'prepare.py')
print('Prepared existing normal-trust image and independent AAC reference identities')
