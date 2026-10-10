"""Prepare matched fractional-clock candidates without changing defaults."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path('.build/c3-frac4-20261010')
plans = [('frac4', 'flac-integer4'), ('quiet-frac4', 'quiet-int4')]
for target, baseline in plans:
    build = Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-{target}')
    artifact = Path(f'firmware/development/esp32c3-idf-6.1-r9a97-{target}')
    assert not build.exists() and not artifact.exists(), target
    before = Path(f'firmware/development/esp32c3-idf-6.1-r9a97-{baseline}/sdkconfig').read_text()
    before, count = re.subn(r'^# CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK is not set$',
                            'CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK=y', before, flags=re.M)
    assert count == 1
    assert not re.search(r'^CONFIG_YORADIO_PDM_INTEGER_.*=y$', before, re.M)
    build.mkdir()
    (build/'sdkconfig').write_text(before)
paths = [*Path('idf/esp32c3-oled-native/main').glob('*'),
         Path('idf/esp32c3-oled-native/CMakeLists.txt'),
         Path('tools/patch_i2s_pdm_clock.py'), Path('tests/native/flash_mode/boot_probe.c')]
sources = {}
for path in paths:
    if not path.is_file(): continue
    data = path.read_bytes()
    sources[path.as_posix()] = hashlib.sha256(data).hexdigest()
    dest = ROOT/'build-sources'/path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
(ROOT/'source-hashes.json').write_text(json.dumps(sources, indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git', 'rev-parse', 'HEAD']))
print('Prepared two candidates and froze', len(sources), 'source files')
