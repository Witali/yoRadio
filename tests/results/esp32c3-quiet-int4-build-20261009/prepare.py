import re
from pathlib import Path

root = Path('.build/c3-quiet-int4-20261009')
build = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-int4')
artifact = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-int4')
assert not build.exists() and not artifact.exists(), 'Preserve previous builds'
build.mkdir()
config = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-min250/sdkconfig').read_text()
config = re.sub(r'(?m)^CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK=y$',
                '# CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK is not set', config)
assert 'CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=' not in config
config += '\nCONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=4\n'
(build/'sdkconfig').write_text(config)
audit = Path('.build/c3-quiet-min250-20261009/audit_build.py').read_text()
audit = audit.replace("ROOT=Path('.build/c3-quiet-min250-20261009')", "ROOT=Path('.build/c3-quiet-int4-20261009')")
audit = audit.replace("BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-min250')", "BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-quiet-int4')")
audit = audit.replace("ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-min250')", "ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-int4')")
audit = audit.replace("LAB=Path('firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250')", "LAB=Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-integer4')\nBASE=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-min250')")
audit = audit.replace('(OLD,ART,LAB)', '(BASE,ART,LAB)')
audit = audit.replace("intended=json.loads((ROOT/'configuration-intent.json').read_text())", "intended={'CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK':None, 'CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS':'4'}")
audit = audit.replace("names=list(json.loads((LAB/'manifest.json').read_text())['source_overlay_sha256'])", "names=[n for n in json.loads((LAB/'manifest.json').read_text())['source_overlay_sha256'] if n.startswith('idf/')]")
audit = audit.replace("clock_mode='fractional'", "clock_mode='integer',flac_input_extra_slots=4")
audit = audit.replace('quiet public-station/OTA and analog qualification pending.', 'quiet public-station/OTA qualification pending.')
(root/'audit_build.py').write_text(audit)
print('Prepared quiet integer-clock candidate with four extra FLAC slots')
