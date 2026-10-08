import hashlib
import json
from pathlib import Path
import subprocess

root = Path('.build/c3-staged-dma-profile-20261008')
with (root/'build.log').open('xb') as log:
    result = subprocess.run(['pwsh.exe','-NoProfile','-File',str(root/'build.ps1')],
                            stdout=log,stderr=subprocess.STDOUT)
if result.returncode:
    raise SystemExit(result.returncode)
base = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly')
folder = base.with_name(base.name+'-dmaprof')
manifest = json.loads((folder/'manifest.json').read_text())
baseline = json.loads((base/'manifest.json').read_text())
for key in ('laboratory_only','extra_trust_ca_sha256','restoration_image','restoration_elf_sha256'):
    manifest[key] = baseline[key]
manifest['qualification'] = ('Build/AAC/HTTP/allocator audit only; laboratory CA; '
    'RX-only TLS reserve and optional staged-output DMA diagnostics. Physical tests pending.')
paths = list(baseline['source_overlay_sha256'])
paths += ['idf/esp32c3-oled-native/main/native_audio_output.c',
          'idf/esp32c3-oled-native/main/native_audio_output.h',
          'idf/esp32c3-oled-native/sdkconfig.staged-dma-profile.defaults']
manifest['source_overlay_sha256'] = {p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
(folder/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
qualification = dict(result='NOT_QUALIFIED', image=manifest['image'], laboratory_only=True,
    physical_tests=False, purpose='Measure staged-output DMA overruns without changing PCM or scheduling',
    reference=base.as_posix())
(folder/'qualification.json').write_bytes((json.dumps(qualification,indent=2)+'\n').encode())
print('STAGED_DMA_BUILD_COMPLETE', manifest['image'], flush=True)
