"""Prepare matched early-MPI-lock candidates without changing defaults."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path('.build/c3-mpi-startup-20261010')
plans = [('mpi-probe', 'web-tcp-v2'), ('mpi-frac4', 'frac4')]
for target, baseline in plans:
    build = Path(f'idf/esp32c3-oled-native/build-idf-6.1-r9a97-{target}')
    artifact = Path(f'firmware/development/esp32c3-idf-6.1-r9a97-{target}')
    assert not build.exists() and not artifact.exists(), target
    before = Path(f'firmware/development/esp32c3-idf-6.1-r9a97-{baseline}/sdkconfig').read_text()
    assert 'CONFIG_YORADIO_TLS_EARLY_MPI_LOCK=' not in before
    before += '\nCONFIG_YORADIO_TLS_EARLY_MPI_LOCK=y\n'
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
