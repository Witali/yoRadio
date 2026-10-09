"""Verify archived identities and reproduce original failures as well as passes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
assert not output.is_relative_to(ROOT), 'Preserve evidence'
output.mkdir(parents=True, exist_ok=False)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
index = json.loads((ROOT/'index.json').read_text())
for name, expected in index['files'].items():
    path = (ROOT/name).resolve()
    assert path.is_relative_to(ROOT)
    assert path.stat().st_size == expected['bytes'] and sha(path) == expected['sha256'], name
baseline = json.loads((ROOT/'firmware-baseline.json').read_text())
old = REPO/baseline['archive']
assert sha(old/'index.json') == baseline['index_sha256']
for name, expected in json.loads((old/'index.json').read_text())['files'].items():
    assert sha(old/name) == expected['sha256'], name
artifact = REPO/'firmware/development/esp32c3-idf-6.1-r9a97-flac-integer4'
manifest = json.loads((artifact/'manifest.json').read_text())
audit = json.loads((ROOT/'build-audit.json').read_text())['4']
assert audit['result'] == 'PASS' and audit['image'] == manifest['image']
assert sha(artifact/'app.bin') == manifest['image']['sha256']
assert (artifact/'app.bin').read_bytes()[176:208].hex() == manifest['image']['app_elf_sha256']
assert sha(artifact/'sdkconfig') == manifest['sdkconfig_sha256']
assert sha(artifact/'bootloader.bin') == manifest['bootloader_sha256']
for name, digest in manifest['source_overlay_sha256'].items():
    assert sha(old/'sources'/name) == digest, name
initial = json.loads((ROOT/'physical/initial.json').read_text())
assert initial['candidate'] == manifest['image']
assert initial['host_clock']['api'] == 'time.perf_counter'
assert initial['host_clock']['monotonic'] and initial['host_clock']['resolution'] <= 1e-6
for name, digest in initial['test_sources_sha256'].items():
    assert sha(ROOT/'sources'/name) == digest, name
restore = json.loads((ROOT/'physical/restoration.json').read_text())
assert restore['identity']['app_elf_sha256'] == initial['quiet']['app_elf_sha256']
assert all(restore['persistence'].values())
assert len(restore['states']) == 3 and all(s['audio'] == initial['status']['audio'] for s in restore['states'])
assert json.loads((ROOT/'physical/candidate-flash.json').read_text())['result'] == 'PASS'
clock = json.loads((ROOT/'physical/candidate-clock.json').read_text())
assert clock['parsed'] and len(clock['clocks']) == 1 and not clock['clocks'][0]['exact_nominal_48khz']
for script, name in (('review.py','review'), ('event_review.py','events')):
    with (output/(name+'.log')).open('xb') as log:
        subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/script), '--output', str(output/(name+'.json'))],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    assert json.loads((output/(name+'.json')).read_text()) == json.loads((ROOT/(name+'.json')).read_text())
print('PASS:', len(index['files']), 'byte-exact files; firmware/helpers/restoration and all recorded verdicts reproduced')
