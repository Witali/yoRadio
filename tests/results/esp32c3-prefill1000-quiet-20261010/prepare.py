"""Prepare normal-trust firmware with the measured one-second prefill."""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path('.build/c3-prefill1000-quiet-20261010')
OLD = Path('.build/c3-quiet-health-20261010')
TARGET = 'quiet-prefill1000'
BUILD = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-' + TARGET)
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-' + TARGET)
assert not ROOT.exists() and not BUILD.exists() and not ART.exists()
config = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-mpi-health/sdkconfig').read_text()
for key, previous in [('YORADIO_INPUT_PREFILL_MIN_MS', 250), ('YORADIO_INPUT_PREFILL_MS', 500)]:
    config, count = re.subn(r'^CONFIG_' + key + '=' + str(previous) + '$',
                            'CONFIG_' + key + '=1000', config, flags=re.M)
    assert count == 1, key
assert 'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y' not in config
ROOT.mkdir()
BUILD.mkdir()
(BUILD / 'sdkconfig').write_text(config)
sources = {}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),
             Path('idf/esp32c3-oled-native/CMakeLists.txt'),
             Path('tools/patch_i2s_pdm_clock.py'), Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():
        continue
    raw = path.read_bytes()
    sources[path.as_posix()] = hashlib.sha256(raw).hexdigest()
    dest = ROOT / 'build-sources' / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
(ROOT / 'source-hashes.json').write_text(json.dumps(sources, indent=2) + '\n')
(ROOT / 'source-head.txt').write_bytes(subprocess.check_output(['git', 'rev-parse', 'HEAD']))

audit = (OLD / 'audit.py').read_text()
audit = audit.replace("choices=['quiet-mpi-health']", "choices=['" + TARGET + "']")
audit = audit.replace('c3-quiet-health-20261010', ROOT.name)
audit = audit.replace("baseline='quiet-frac4'", "baseline='quiet-mpi-health'")
audit = audit.replace("{'CONFIG_YORADIO_TLS_EARLY_MPI_LOCK':[None,'y']}",
    "{'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':['250','1000'],'CONFIG_YORADIO_INPUT_PREFILL_MS':['500','1000']}")
audit = audit.replace("('s_pcm_fir','pcm_fir_coefficients'", "('s_audio_pipeline_probe','s_pcm_fir','pcm_fir_coefficients'")
audit = audit.replace('input_prefill_min_ms=250,input_prefill_ms=500',
                      'input_prefill_min_ms=1000,input_prefill_ms=1000')
audit = audit.replace('production_health=True,source_note=',
                      'production_health=True,output_health=True,pipeline_diagnostic=False,source_note=')
(ROOT / 'audit.py').write_text(audit)
build_script = (OLD / 'build.ps1').read_text().replace('c3-quiet-health-20261010', ROOT.name)
build_script = build_script.replace("$target = 'quiet-mpi-health'", "$target = '" + TARGET + "'")
(ROOT / 'build.ps1').write_text(build_script)
shutil.copyfile(OLD / 'export-used.py', ROOT / 'export-used.py')
shutil.copyfile(__file__, ROOT / 'prepare.py')
print('Prepared normal trust / one-second prefill:', len(sources), 'frozen build sources')
