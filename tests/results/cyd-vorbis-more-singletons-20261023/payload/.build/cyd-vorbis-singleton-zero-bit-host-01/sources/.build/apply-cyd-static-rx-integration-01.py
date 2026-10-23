"""Apply only the eight reviewed production files; no compiler or Git writes."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent.parent
prep = root / '.build/cyd-tls-reserve-registry-target-prep-01'
source = prep / 'repository'
receipt = root / '.build/cyd-static-rx-integration-applied-01.json'
assert not receipt.exists()
relative = [
    'idf/esp32-cyd2usb-native/main/CMakeLists.txt',
    'idf/esp32-cyd2usb-native/main/Kconfig.projbuild',
    'idf/esp32-cyd2usb-native/main/audio_service.c',
    'idf/esp32-cyd2usb-native/main/native_tls_rx_reserve.c',
    'idf/esp32-cyd2usb-native/main/native_tls_rx_reserve.h',
    'idf/esp32-cyd2usb-native/main/compat/tls_static_rx/enable.cmake',
    'idf/esp32-cyd2usb-native/main/compat/tls_static_rx/sdk-source-guards.json',
    'tools/patch_cyd_tls_static_rx.py',
]
expected = json.loads((prep / 'preparation.json').read_bytes())['files']
digest = lambda raw: hashlib.sha256(raw).hexdigest()
payloads = {name: (source / name).read_bytes() for name in relative}
assert all(digest(raw) == expected[name] for name, raw in payloads.items())
existing = set(relative[:3])
assert all((root / name).is_file() if name in existing else not (root / name).exists()
           for name in relative)
before = {name: digest((root / name).read_bytes()) if name in existing else None
          for name in relative}
for name, raw in payloads.items():
    target = root / name
    assert target.resolve().is_relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
assert all((root / name).read_bytes() == raw for name, raw in payloads.items())
receipt.write_text(json.dumps({
    'applied': True, 'compiled': False, 'source_proposal': str(source),
    'files': {name: {'before_sha256': before[name], 'after_sha256': digest(raw)}
              for name, raw in payloads.items()},
    'scope': 'Eight reviewed production files only; default remains off; qualification pending',
}, indent=2) + '\n', encoding='utf-8')
print('Applied eight reviewed production files; build/tests not yet run')
