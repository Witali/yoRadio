"""Check saved image/source identities and reproduce all original and stricter verdicts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
output = a.output.resolve()
assert not output.is_relative_to(ROOT), 'Preserve evidence'
output.mkdir(parents=True, exist_ok=False)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
index = json.loads((ROOT/'index.json').read_text())
for name, expected in index['files'].items():
    path = (ROOT/name).resolve(); assert path.is_relative_to(ROOT)
    assert path.stat().st_size == expected['bytes'] and sha(path) == expected['sha256'], name
audit = json.loads((ROOT/'build-audit.json').read_text())
baseline = json.loads((ROOT/'firmware-baseline.json').read_text())
old = REPO/baseline['archive']
assert sha(old/'index.json') == baseline['index_sha256']
for name, expected in json.loads((old/'index.json').read_text())['files'].items():
    assert sha(old/name) == expected['sha256'], name
for slots in (0, 4):
    artifact = REPO/f'firmware/development/esp32c3-idf-6.1-r9a97-flac-integer{slots}'
    manifest = json.loads((artifact/'manifest.json').read_text())
    assert audit[str(slots)]['result'] == 'PASS' and audit[str(slots)]['image'] == manifest['image']
    assert sha(artifact/'app.bin') == manifest['image']['sha256']
    assert (artifact/'app.bin').read_bytes()[176:208].hex() == manifest['image']['app_elf_sha256']
    assert sha(artifact/'sdkconfig') == manifest['sdkconfig_sha256']
    assert sha(artifact/'bootloader.bin') == manifest['bootloader_sha256']
    for name, digest in manifest['source_overlay_sha256'].items():
        assert sha(old/'sources'/name) == digest, name
initial = json.loads((ROOT/'physical/initial.json').read_text())
for name, digest in initial['test_sources_sha256'].items():
    assert sha(ROOT/'sources'/name) == digest, name
restore = json.loads((ROOT/'physical/restoration.json').read_text())
assert restore['identity']['app_elf_sha256'] == initial['quiet']['app_elf_sha256']
assert all(restore['persistence'].values())
assert len(restore['states']) == 3 and all(s['audio'] == initial['status']['audio'] for s in restore['states'])
for label in ('control-before', 'expanded', 'control-after'):
    assert json.loads((ROOT/'physical'/(label+'-flash.json')).read_text())['result'] == 'PASS'
    clock = json.loads((ROOT/'physical'/(label+'-clock.json')).read_text())
    assert clock['parsed'] and len(clock['clocks']) == 1 and not clock['clocks'][0]['exact_nominal_48khz']
with (output/'review.log').open('xb') as log:
    subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'review.py'), '--output', str(output/'review.json')], stdout=log, stderr=subprocess.STDOUT, check=True)
assert json.loads((output/'review.json').read_text()) == json.loads((ROOT/'review.json').read_text())
with (output/'pauses.log').open('xb') as log:
    subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'pause_review.py'), '--output', str(output/'pauses.json')], stdout=log, stderr=subprocess.STDOUT, check=True)
assert json.loads((output/'pauses.json').read_text()) == json.loads((ROOT/'pauses.json').read_text())
print('PASS:', len(index['files']), 'byte-exact files; image/config/sources, restoration and FLAC/AAC evidence reproduced')
