import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
review=json.loads((root/'review.json').read_text())
assert review['review']=='PASS' and review['restoration']
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-http-txrelease')
manifest=json.loads((art/'manifest.json').read_text())
assert hashlib.sha256((art/'app.bin').read_bytes()).hexdigest()==manifest['image']['sha256']
manifest.update(ota_soak_report='tests/results/esp32c3-http-buffer-ota-soak/review.json',
    ota_regression=review['ota'],https_he_aac_600s=review['soak'],production_qualified=False,
    reproduction_command='idf/esp32c3-oled-native/build-production.ps1 -TestedRadioProfile',
    reproduction_profile_commit='3be3d5c9',
    qualification='Measured opt-in configuration: 15/15 OTA checks and 600-second public HE-AAC HTTPS gates passed, following codec regression and targeted controls. Earlier public MP3 interruption/WebUI timeout remain unresolved. Original production restored; complete production goal not qualified.')
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Saved OTA/soak qualification and reproduction command')
