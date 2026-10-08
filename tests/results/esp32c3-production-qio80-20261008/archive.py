"""Save the completed production deployment without private board data."""
import hashlib
import json
from pathlib import Path
import re

root = Path('.build/c3-production-qio80-20261008')
target = Path('tests/results/esp32c3-production-qio80-20261008')
artifact = Path('firmware/development/esp32c3-idf-6.1-r9a97-production-qio80')
final = json.loads((root / 'physical/final-board.json').read_text())
assert final['stored_station_resumed'] and final['remaining_checks'] == 'SKIPPED_USER_REQUEST'
skipped = json.loads((root / 'physical/checks-skipped.json').read_text())
assert skipped['reason'] == 'User requested remaining checks to be skipped'
manifest = json.loads((artifact / 'manifest.json').read_text())
manifest.update(hardware_tested=True, production_qualified=False,
    qualification='Installed, readback/settings verified, 12 HTTP/EOF checks passed; remaining checks skipped at user request',
    remaining_checks_skipped=True,
    physical_evidence=target.as_posix(), report='docs/ESP32C3_PRODUCTION_QIO80_20261008.md')
(artifact / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
assert not target.exists(), 'Preserve earlier evidence'
target.mkdir(parents=True)

def copy(source, destination):
    assert source.suffix not in ('.bin', '.elf', '.pcm', '.flac', '.aac', '.key', '.pem', '.pyc')
    data = source.read_bytes()
    assert not re.search(rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', data)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)

for path in root.rglob('*'):
    if path.is_file() and 'private' not in path.relative_to(root).parts and '__pycache__' not in path.parts:
        copy(path, target / path.relative_to(root))
for name in ('sdkconfig', 'manifest.json'):
    copy(artifact / name, target / 'artifact' / name)
sources = set(manifest['source_overlay_sha256'])
sources.update(('idf/esp32c3-oled-native/build-production.ps1',
    'idf/esp32c3-oled-native/build.ps1', 'idf/esp32c3-oled-native/sdkconfig.defaults',
    'idf/esp32c3-oled-native/sdkconfig.production.defaults',
    'tools/codec_benchmark/verify_aac_network_build.py',
    '.agents/skills/flash-reset-esp32c3-oled/scripts/reset_esp32c3_oled.ps1'))
for folder in ('tools/esp32c3_tests', 'tools/audio_test_server'):
    sources.update(p.as_posix() for p in Path(folder).glob('*.py'))
source_hashes = {}
for name in sorted(sources):
    copy(Path(name), target / 'sources' / name)
    source_hashes[name] = hashlib.sha256(Path(name).read_bytes()).hexdigest()
for name, digest in manifest['source_overlay_sha256'].items():
    assert source_hashes[name] == digest
(target / 'source-index.json').write_bytes((json.dumps(source_hashes, indent=2) + '\n').encode())
index = {p.relative_to(target).as_posix(): dict(bytes=p.stat().st_size,
         sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(target.rglob('*')) if p.is_file()}
(target / 'index.json').write_bytes((json.dumps(index, indent=2) + '\n').encode())
print('Archived', len(index), 'files;', sum(v['bytes'] for v in index.values()), 'bytes')
