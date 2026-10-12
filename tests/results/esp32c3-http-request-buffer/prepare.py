import hashlib
import json
import shutil
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=Path('.build/c3-production-20261010')
target='quiet-http-txrelease'
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+target)
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-'+target)
assert not build.exists() and not art.exists()
build.mkdir()
config=Path('firmware/development/esp32c3-idf-6.1-r9a97-production-prefill1000/sdkconfig').read_text()
assert 'CONFIG_YORADIO_HTTP_RELEASE_REQUEST_BUFFER=y' not in config
(build/'sdkconfig').write_text(config+'\nCONFIG_YORADIO_HTTP_RELEASE_REQUEST_BUFFER=y\n')
sources={}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_http_request_buffer.py'),Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():continue
    raw=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(raw).hexdigest()
    dest=ROOT/'build-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
audit=(OLD/'audit.py').read_text().replace("choices=['production-prefill1000']","choices=['"+target+"']").replace(OLD.name,ROOT.name)
audit=audit.replace("baseline='quiet-prefill1000'","baseline='production-prefill1000'")
audit=audit.replace('assert changes=={},changes',"assert changes=={'CONFIG_YORADIO_HTTP_RELEASE_REQUEST_BUFFER':[None,'y']},changes")
audit=audit.replace("assert symbols['s_tls_large_storage']['st_size']==17058","assert symbols['s_tls_large_storage']['st_size']==17058\n    assert 'yoradio_http_client_release_request_buffer' in symbols")
audit=audit.replace('798f8c312bfcea37206908ee7ae13f88d8d821f9642fd3fb0846186f3411ccde','8f086f439e00d9e4baf4fe603b1b64935c7ddd188bd6f5ea380a7202075bd664')
audit=audit.replace("source_note='Quiet candidate", "http_request_buffer_release=True,source_note='Experimental HTTP TX release; quiet candidate")
(ROOT/'audit.py').write_text(audit)
script=(OLD/'build.ps1').read_text().replace(OLD.name,ROOT.name).replace("$target = 'production-prefill1000'","$target = '"+target+"'")
(ROOT/'build.ps1').write_text(script)
shutil.copyfile(OLD/'export-used.py',ROOT/'export-used.py')
print('Prepared',target,len(sources),'sources')
