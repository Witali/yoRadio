import argparse, hashlib, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('mode',choices=['dynamic','static']);args=p.parse_args()
root=Path('.build/c3-rx-window-20261007');mode=args.mode
with (root/f'build-{mode}.log').open('xb') as log:
    code=subprocess.run(['pwsh.exe','-NoProfile','-File',str(root/'build-window.ps1'),'-Mode',mode],stdout=log,stderr=subprocess.STDOUT).returncode
if code:raise SystemExit(code)
folder=Path(f'firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-rx4-{mode}')
manifest=json.loads((folder/'manifest.json').read_text())
ca=Path('.build/c3-tls-records-20261007/trust/ca.pem')
manifest.update(laboratory_only=True,extra_trust_ca_sha256=hashlib.sha256(ca.read_bytes()).hexdigest(),
    restoration_image='esp32c3-idf-6.1-compact-icy-quiet',
    restoration_elf_sha256='da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0',
    qualification='Build/AAC audit only; laboratory trust root; reduced TCP window remains experimental')
(folder/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
print('WINDOW_BUILD_COMPLETE',mode,flush=True)
