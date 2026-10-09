"""Prepare a bounded cross-codec/TLS campaign from the audited OTA guard."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
previous = REPO/'tests/results/esp32c3-delivery-pauses-20261009'
baseline = REPO/'tests/results/esp32c3-flac-integer-20261009'
source = (previous/'physical.py').read_text().split("require(not OUT.exists()", 1)[0]
assert source.count("ROOT = Path('.build/c3-delivery-pauses-20261009')") == 1
source = source.replace("ROOT = Path('.build/c3-delivery-pauses-20261009')",
                        "ROOT = Path('.build/c3-integer-qualification-20261009')")
source = source.replace('time.monotonic()', 'time.perf_counter()')
source += (ROOT/'controller_body.py').read_text()
assert not (ROOT/'physical.py').exists()
(ROOT/'physical.py').write_text(source)
sources = {}
for folder in ('tools/esp32c3_tests', 'tools/audio_test_server'):
    for path in sorted((REPO/folder).glob('*.py')):
        relative = path.relative_to(REPO)
        sources[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        target = ROOT/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
(ROOT/'sources.json').write_text(json.dumps(sources, indent=2)+'\n')
for name in ('ca.pem', 'server.pem'):
    shutil.copyfile(REPO/'.build/c3-switch-owner-20261009/trust'/name, ROOT/name)
shutil.copyfile(baseline/'build-audit.json', ROOT/'build-audit.json')
(ROOT/'firmware-baseline.json').write_text(json.dumps(dict(
    archive=baseline.relative_to(REPO).as_posix(),
    index_sha256=hashlib.sha256((baseline/'index.json').read_bytes()).hexdigest(),
    note='Unchanged integer4 firmware. Current sources describe test helpers, not the firmware build.'), indent=2)+'\n')
shutil.copytree(REPO/'.build/c3-host-clock-20261009', ROOT/'host')
for name in ('test-serial-telemetry.py', 'test-audio-server-pauses.py'):
    shutil.copyfile(REPO/'tests'/name, ROOT/'host'/name)
print('Prepared controller and', len(sources), 'frozen helpers')
