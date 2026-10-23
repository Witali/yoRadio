"""Verify the reviewed frozen preparation and install its new canonical tests."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent.parent
prep = root / '.build/cyd-tls-reserve-registry-target-prep-01'
digest = lambda raw: hashlib.sha256(raw).hexdigest()
assert digest((prep / 'manifest.json').read_bytes()) == '8690b77ea44e23ab71ad30190ef9cc5764080f5609009adac4519582f5c70606'
assert digest((prep / 'readiness.json').read_bytes()) == '5b355b3732430a1dd57e51bb85b3b3162da9279114c50d8dce3fe73fdc373a07'
manifest = json.loads((prep / 'manifest.json').read_bytes())['files']
assert len(manifest) == 554
for relative, row in manifest.items():
    path = (prep / relative).resolve()
    assert path.is_relative_to(prep)
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], relative
source = prep / 'repository'
payloads = {path.relative_to(source).as_posix(): path.read_bytes()
            for path in source.rglob('*') if path.is_file()}
assert len(payloads) == 34
existing = set(json.loads((root / '.build/cyd-static-rx-integration-applied-01.json').read_bytes())['files'])
assert len(existing) == 8 and existing.issubset(payloads)
receipt = root / '.build/cyd-static-rx-tests-applied-01.json'
assert not receipt.exists()
for name, raw in payloads.items():
    target = (root / name).resolve()
    assert target.is_relative_to(root)
    assert digest(raw) == manifest['repository/' + name]['sha256']
    if name in existing:
        assert target.read_bytes() == raw, name
    else:
        assert not target.exists(), name
        assert name.startswith('tests/') or name == 'idf/esp32-cyd2usb-native/main/compat/tls_static_rx/.gitattributes'
for name, raw in payloads.items():
    if name not in existing:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
assert all((root / name).read_bytes() == raw for name, raw in payloads.items())
receipt.write_text(json.dumps({
    'applied': True, 'compiled': False, 'verified_preparation_files': len(manifest),
    'source_files': {name: digest(raw) for name, raw in payloads.items()},
    'new_files': sorted(set(payloads) - existing),
}, indent=2) + '\n', encoding='utf-8')
print('Verified 554 frozen preparation files; installed 25 test files and scoped Git attribute')
