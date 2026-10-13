"""Archive the completed build and hardware deployment without private settings."""
import hashlib
import json
import shutil
from pathlib import Path

src = Path('.build/c3-production-20261013')
dst = Path('tests/results/esp32c3-production-deployment-20261013')
art = Path('firmware/development/esp32c3-idf61-production-20261013')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
play = json.loads((src/'deployment/playback.json').read_text())
final = json.loads((src/'deployment/final.json').read_text())
assert play['result'] == 'PASS'
assert all(final['persistence'].values())
assert all(not s['audio'] for s in final['states'])
manifest = json.loads((art/'manifest.json').read_text())
assert final['identity']['app_elf_sha256'] == manifest['image']['app_elf_sha256']
manifest.update(hardware_tested=True, installed_identity=final['identity'],
    deployment_method='WebUI app-only OTA', settings_preserved=final['persistence'],
    qualification='Build/link audits, OTA identity/settings checks and 60-second local HE-AACv2 smoke passed. Full codec/network/OTA qualification was not rerun.',
    evidence=dst.as_posix(), report='docs/ESP32C3_PRODUCTION_DEPLOYMENT_20261013.md',
    audio_codec_library_sha256=sha(Path('C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec/lib/esp32c3/libesp_audio_codec.a')))
(art/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
(art/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
assert not dst.exists()
shutil.copytree(src, dst)
(dst/'.gitattributes').write_text('# Preserve raw diagnostic output, including tool whitespace.\n* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
logs = Path('idf/esp32c3-oled-native/build-production-20261013/log')
shutil.copytree(logs, dst/'idf-build-logs')
checksums = {p.relative_to(dst).as_posix(): sha(p) for p in sorted(dst.rglob('*')) if p.is_file()}
(dst/'sha256.json').write_text(json.dumps(checksums, indent=2)+'\n')
print(json.dumps(dict(image=manifest['image'], playback=play['evidence'], final_health=final['health'])))
