import hashlib
import json
from pathlib import Path
import subprocess

root=Path('.build/c3-tls-path-20261008')
base=Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof')
template=Path('.build/c3-staged-dma-profile-20261008/build.ps1').read_text()
variant='r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-tlspath'
recipe=template.replace('r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof',variant)
recipe=recipe.replace('idf61-9a97-dmaprof','idf61-9a97-tlspath')
recipe=recipe.replace("'sdkconfig.staged-dma-profile.defaults')",
    "'sdkconfig.staged-dma-profile.defaults','sdkconfig.tls-path-profile.defaults')")
recipe=recipe.replace('.build/c3-staged-dma-profile-20261008/',root.as_posix()+'/')
(root/'build.ps1').write_text(recipe)
with (root/'build.log').open('xb') as log:
    status=subprocess.run(['pwsh.exe','-NoProfile','-File',str(root/'build.ps1')],
        stdout=log,stderr=subprocess.STDOUT).returncode
if status:raise SystemExit(status)
image=Path('firmware/development')/('esp32c3-idf-6.1-'+variant)
manifest=json.loads((image/'manifest.json').read_text())
control=json.loads((base/'manifest.json').read_text())
def values(path):
    return dict(l.split('=',1) for l in path.read_text().splitlines() if l.startswith('CONFIG_') and '=' in l)
before,after=values(base/'sdkconfig'),values(image/'sdkconfig')
changed={k:dict(control=before.get(k),candidate=after.get(k)) for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
assert set(changed)=={'CONFIG_YORADIO_TLS_PATH_PROFILE'},changed
for key in ('laboratory_only','extra_trust_ca_sha256','restoration_image','restoration_elf_sha256'):
    manifest[key]=control[key]
sources=list(control['source_overlay_sha256'])+[
    'idf/esp32c3-oled-native/main/tls_path_profile.c', 'idf/esp32c3-oled-native/main/tls_path_profile.h',
    'idf/esp32c3-oled-native/sdkconfig.tls-path-profile.defaults','idf/esp32c3-oled-native/main/tls_stream_eof.c', 'idf/esp32c3-oled-native/main/stream_http_reader.c']
manifest['source_overlay_sha256']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources}
manifest['control_configuration_diff']=changed
manifest['qualification']='Optional TLS path wall-time counters; host seam tests only; physical tests pending. NOT_QUALIFIED.'
(image/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
(image/'qualification.json').write_bytes((json.dumps(dict(result='NOT_QUALIFIED',laboratory_only=True,
    physical_tests=False,image=manifest['image'],reference=base.as_posix()),indent=2)+'\n').encode())
print('BUILD_COMPLETE',manifest['image'],flush=True)
