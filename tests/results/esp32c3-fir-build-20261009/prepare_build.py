import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('.build/c3-fir-20261009')
BUILD=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-fir32')
ART=Path('firmware/development/esp32c3-idf-6.1-r9a97-fir32')
assert not BUILD.exists() and not ART.exists()
BUILD.mkdir()
baseline=Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-integer4/sdkconfig').read_text()
assert 'CONFIG_YORADIO_PDM_INTEGER_' not in baseline
(BUILD/'sdkconfig').write_text(baseline+'\nCONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION=y\nCONFIG_YORADIO_PDM_INTEGER_FIR=y\n')
sources={}
paths=[*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),
       Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]
for p in paths:
    if not p.is_file(): continue
    sources[p.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    dest=ROOT/'build-sources'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
print('Prepared FIR build and',len(sources),'source snapshots')
