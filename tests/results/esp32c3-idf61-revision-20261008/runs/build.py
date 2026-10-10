import argparse, hashlib, json, subprocess
from pathlib import Path
root=Path('.build/c3-idf-head-20261008');mode='head'
with (root/f'build-{mode}.log').open('xb') as log:
    code=subprocess.run(['pwsh.exe','-NoProfile','-File',str(root/'build.ps1')],stdout=log,stderr=subprocess.STDOUT).returncode
if code:raise SystemExit(code)
folder=Path(f'firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-dynamic')
manifest=json.loads((folder/'manifest.json').read_text())
ca=Path('.build/c3-tls-records-20261007/trust/ca.pem')
manifest.update(laboratory_only=True,extra_trust_ca_sha256=hashlib.sha256(ca.read_bytes()).hexdigest(),
    restoration_image='esp32c3-idf-6.1-compact-icy-quiet',
    restoration_elf_sha256='da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0',
    qualification='Build/AAC audit only; laboratory trust root; Pinned release/v6.1 9a97f6c54ec6; dynamic TLS RX; physical qualification pending')
paths=['idf/esp32c3-oled-native/main/'+s for s in ('audio_service.c','CMakeLists.txt','stream_http_reader.c','stream_http_reader.h','tls_stream_eof.c','Kconfig.projbuild')]
paths+=['idf/esp32c3-oled-native/sdkconfig.tcp-rx-six-segments.defaults','idf/esp32c3-oled-native/idf-revision.txt','tools/patch_httpd_content_length.py']
manifest['source_overlay_sha256']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
(folder/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
print('WINDOW_BUILD_COMPLETE',mode,flush=True)
