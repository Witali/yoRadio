"""Prepare ignored isolated configs from the immutable preceding six images."""
from pathlib import Path
import hashlib
import json
import re

root = Path.cwd()
rows = []
for custom in (False, True):
    for backend in ('pdm', 'continuous', 'legacy'):
        suffix = ('custom-flac-' if custom else '') + backend
        previous = root / 'firmware/development' / ('esp32-cyd2usb-native-output-telemetry-' + suffix)
        receipt = json.loads((previous / 'manifest.json').read_text())
        rows.append(dict(name=suffix, backend=backend, custom_flac=custom, enabled=True,
                         variant='esp32-cyd2usb-native-tls-input-reclaim-' + suffix,
                         build_directory=receipt['build_directory'], baseline=str(previous)))
previous = root / 'firmware/development/esp32-cyd2usb-native-output-telemetry-pdm'
rows.append(dict(name='disabled-pdm', backend='pdm', custom_flac=False, enabled=False,
                 variant='esp32-cyd2usb-native-tls-input-reclaim-disabled-pdm',
                 build_directory=str(root / 'idf/esp32-cyd2usb-native/build-input-reclaim-disabled-pdm'),
                 baseline=str(previous)))
for row in rows:
    folder = Path(row['build_directory']).resolve()
    assert folder.is_relative_to(root)
    folder.mkdir(parents=True, exist_ok=True)
    source = Path(row['baseline']) / 'sdkconfig'
    raw = source.read_bytes()
    seed = raw.decode().splitlines()
    seed = [line for line in seed if not re.match(r'^(?:# )?CONFIG_YORADIO_TLS_INPUT_RECLAIM(?:=| )', line)]
    seed.append('CONFIG_YORADIO_TLS_INPUT_RECLAIM=y' if row['enabled'] else '# CONFIG_YORADIO_TLS_INPUT_RECLAIM is not set')
    target = folder / 'sdkconfig'
    target.write_bytes(('\n'.join(seed) + '\n').encode())
    row.update(sdkconfig=str(target), baseline_sdkconfig_sha256=hashlib.sha256(raw).hexdigest(),
               prepared_sdkconfig_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
out = root / '.build/input-reclaim-production-profiles.json'
assert not out.exists()
out.write_text(json.dumps(rows, indent=2) + '\n')
print(json.dumps({'prepared': len(rows), 'profiles': str(out)}, indent=2))
