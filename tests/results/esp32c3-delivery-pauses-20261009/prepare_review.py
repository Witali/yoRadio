"""Reuse measured-window replay and keep baseline firmware provenance distinct."""
from pathlib import Path
root = Path(__file__).resolve().parent
old = Path('tests/results/esp32c3-flac-integer-20261009')
review = (old/'review.py').read_text().replace('Independent replay of FLAC capacity/clock measurements; retain failed gates.', 'Independent replay of matched delivery pauses; retain failed gates.')
review = review.replace('Same-source integer-clock pair; old fractional experiments are not matched controls.', 'Saved integer-clock pair with identical host pause positions and send-buffer request. Host writes are not board arrival times.')
(root/'review.py').write_text(review)
replay = (old/'replay.py').read_text()
replay = replay.replace("audit = json.loads((ROOT/'build-audit.json').read_text())", """audit = json.loads((ROOT/'build-audit.json').read_text())
baseline = json.loads((ROOT/'firmware-baseline.json').read_text())
old = REPO/baseline['archive']
assert sha(old/'index.json') == baseline['index_sha256']
for name, expected in json.loads((old/'index.json').read_text())['files'].items():
    assert sha(old/name) == expected['sha256'], name""")
replay = replay.replace("sha(ROOT/'sources'/name) == digest, name\ninitial", "sha(old/'sources'/name) == digest, name\ninitial")
replay = replay.replace("print('PASS:'", """with (output/'pauses.log').open('xb') as log:
    subprocess.run([sys.executable, '-X', 'utf8', str(ROOT/'pause_review.py'), '--output', str(output/'pauses.json')], stdout=log, stderr=subprocess.STDOUT, check=True)
assert json.loads((output/'pauses.json').read_text()) == json.loads((ROOT/'pauses.json').read_text())
print('PASS:'""")
(root/'replay.py').write_text(replay)
freeze = (old/'freeze.py').read_text().replace('esp32c3-flac-integer-20261009', 'esp32c3-delivery-pauses-20261009')
freeze = freeze.replace("review = json.loads((ROOT/'review.json').read_text())", "assert (ROOT/'pauses.json').is_file()\nreview = json.loads((ROOT/'review.json').read_text())")
(root/'freeze.py').write_text(freeze)
