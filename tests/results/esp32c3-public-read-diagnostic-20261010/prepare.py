"""Prepare normal-trust diagnostic firmware without altering playback policy."""
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path('.build/c3-public-read-diagnostic-20261010')
OLD = Path('.build/c3-prefill1000-quiet-20261010')
TARGET = 'quiet-read-diag'
BASE = 'quiet-prefill1000'
BUILD = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-' + TARGET)
assert not ROOT.exists() and not BUILD.exists()
ROOT.mkdir(); BUILD.mkdir()
config = Path('firmware/development/esp32c3-idf-6.1-r9a97-' + BASE, 'sdkconfig').read_text()
config, count = re.subn(r'^# CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC is not set$',
    'CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC=y', config, flags=re.M)
assert count == 1
(BUILD / 'sdkconfig').write_text(config)
sources = {}
for file in [*Path('idf/esp32c3-oled-native/main').glob('*'),
             Path('idf/esp32c3-oled-native/CMakeLists.txt'),
             Path('tools/patch_i2s_pdm_clock.py'), Path('tests/native/flash_mode/boot_probe.c')]:
    if not file.is_file(): continue
    raw = file.read_bytes(); sources[file.as_posix()] = hashlib.sha256(raw).hexdigest()
    dest = ROOT / 'build-sources' / file
    dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(raw)
(ROOT / 'source-hashes.json').write_text(json.dumps(sources, indent=2) + '\n')
(ROOT / 'source-head.txt').write_bytes(subprocess.check_output(['git', 'rev-parse', 'HEAD']))
audit = (OLD / 'audit.py').read_text().replace("choices=['quiet-prefill1000']", "choices=['" + TARGET + "']")
audit = audit.replace(OLD.name, ROOT.name).replace("baseline='quiet-mpi-health'", "baseline='" + BASE + "'")
audit = audit.replace("{'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':['250','1000'],'CONFIG_YORADIO_INPUT_PREFILL_MS':['500','1000']}",
                      "{'CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC':[None,'y']}")
audit = audit.replace("for name in ('s_audio_pipeline_probe','s_pcm_fir'", "assert symbols['s_audio_pipeline_probe']['st_size']==540\n    for name in ('s_pcm_fir'")
audit = audit.replace('laboratory_only=lab,production_profile=not lab', 'laboratory_only=True,production_profile=False')
audit = audit.replace('pipeline_diagnostic=False', 'pipeline_diagnostic=True')
audit = audit.replace("source_note='Quiet candidate with early MPI initialization and on-demand health; lifetime OOM/WDT counters; inactive CLZ excluded.'",
                      "source_note='Normal public trust; one-second prefill; diagnostic DMA checkpoints and numeric HTTP/TLS failure snapshot.'")
(ROOT / 'audit.py').write_text(audit)
(ROOT / 'build.ps1').write_text((OLD / 'build.ps1').read_text().replace(OLD.name, ROOT.name)
    .replace("$target = 'quiet-prefill1000'", "$target = '" + TARGET + "'"))
shutil.copyfile(OLD / 'export-used.py', ROOT / 'export-used.py')
shutil.copyfile(__file__, ROOT / 'prepare.py')
for name in ('c3-read-diagnostic-off', 'c3-read-diagnostic-on', 'production-health-native'):
    for file in Path('.build', name).glob('*'):
        if file.is_file() and file.suffix in ('.json', '.log', '.c', '.h'):
            dest = ROOT / 'host-tests' / name / file.name
            dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(file.read_bytes())
print('Prepared normal-trust diagnostics; exact codec arithmetic remains audited')
