"""Refresh the unbuilt source capture after the paired RX diagnostic commit."""
import hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-rx-owner')
assert {p.name for p in build.iterdir()}=={'sdkconfig'},'Already configured/built'
sources={}
for p in [*Path('idf/esp32c3-oled-native/main').glob('*'),
          Path('idf/esp32c3-oled-native/CMakeLists.txt'),
          Path('tools/patch_http_request_buffer.py'),Path('tools/patch_i2s_pdm_clock.py')]:
    if not p.is_file():continue
    raw=p.read_bytes();sources[p.as_posix()]=hashlib.sha256(raw).hexdigest()
    target=root/'sources'/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
(root/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(root/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
print('Updated source capture for unbuilt RX owner image')
