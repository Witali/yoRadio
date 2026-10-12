import hashlib,json,shutil,subprocess
from pathlib import Path
root=Path('.build/c3-production-radio')
previous=Path('.build/c3-http-request-buffer')
sources={}
paths=[*Path('idf/esp32c3-oled-native/main').glob('*'),*Path('idf/esp32c3-oled-native').glob('*.ps1'),*Path('idf/esp32c3-oled-native').glob('sdkconfig*.defaults'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_http_request_buffer.py'),Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]
for path in paths:
    if not path.is_file():continue
    data=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(data).hexdigest()
    dest=root/'build-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(root/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(root/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
text=(previous/'audit.py').read_text().replace("choices=['quiet-http-txrelease']","choices=['production-radio']").replace('.build/c3-http-request-buffer','.build/c3-production-radio')
(root/'audit.py').write_text(text)
shutil.copyfile(previous/'export-used.py',root/'export-used.py')
print('Captured',len(sources),'source files')
