import hashlib, json, subprocess
from pathlib import Path

root = Path('.build/c3-tls-records-20261007')
ca = (root/'trust/ca.pem').resolve()
(root/'lab-ca.defaults').write_text('CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y\nCONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH="'+ca.as_posix()+'"\nCONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL=y\n')
for mode in ('dynamic','static'):
    print('START_LAB_BUILD',mode,flush=True)
    with (root/f'build-lab-{mode}.log').open('xb') as log:
        code = subprocess.run(['pwsh.exe','-NoProfile','-File',str(root/'build-lab.ps1'),'-Mode',mode], stdout=log, stderr=subprocess.STDOUT).returncode
    if code: raise SystemExit(code)
    path = Path(f'firmware/development/esp32c3-idf-6.1-memory-icy-tlslab-{mode}/manifest.json')
    manifest = json.loads(path.read_text())
    manifest.update(laboratory_only=True, extra_trust_ca_sha256=hashlib.sha256(ca.read_bytes()).hexdigest(),
        restoration_image='esp32c3-idf-6.1-compact-icy-quiet',
        restoration_elf_sha256='da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0',
        qualification='Build/AAC linked audit only; lab-only extra trust root; never use as production firmware')
    path.write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    print('END_LAB_BUILD',mode,flush=True)
