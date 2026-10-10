import hashlib
import json
import shutil
import subprocess
from pathlib import Path

root = Path('.build/c3-production-20261010')
old = Path('.build/c3-prefill1000-quiet-20261010')
target = 'production-prefill1000'
build = Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-' + target)
art = Path('firmware/development/esp32c3-idf-6.1-r9a97-' + target)
assert not root.exists() and not build.exists() and not art.exists()
root.mkdir()
build.mkdir()
shutil.copyfile('firmware/development/esp32c3-idf-6.1-r9a97-quiet-prefill1000/sdkconfig', build/'sdkconfig')
sources = {}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'), Path('idf/esp32c3-oled-native/CMakeLists.txt'), Path('tools/patch_i2s_pdm_clock.py'), Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():
        continue
    raw = path.read_bytes()
    sources[path.as_posix()] = hashlib.sha256(raw).hexdigest()
    dest = root/'build-sources'/path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
(root/'source-hashes.json').write_text(json.dumps(sources, indent=2)+'\n')
(root/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
audit = (old/'audit.py').read_text()
audit = audit.replace("choices=['quiet-prefill1000']", "choices=['"+target+"']")
audit = audit.replace(old.name, root.name)
audit = audit.replace("baseline='quiet-mpi-health'", "baseline='quiet-prefill1000'")
audit = audit.replace("{'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':['250','1000'],'CONFIG_YORADIO_INPUT_PREFILL_MS':['500','1000']}", '{}')
(root/'audit.py').write_text(audit)
script = (old/'build.ps1').read_text().replace(old.name, root.name)
script = script.replace("$target = 'quiet-prefill1000'", "$target = '"+target+"'")
(root/'build.ps1').write_text(script)
shutil.copyfile(old/'export-used.py', root/'export-used.py')
shutil.copyfile(__file__, root/'prepare.py')
print('Prepared production build:', len(sources), 'source hashes')
