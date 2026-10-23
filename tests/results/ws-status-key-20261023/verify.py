"""Verify retained WS regression bytes; does not execute test/SDK code."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--manifest-sha256', required=True)
a = p.parse_args()
root = Path(__file__).resolve().parent
manifest = root / 'manifest.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == a.manifest_sha256
data = json.loads(manifest.read_bytes())
actual = {x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file() and x != manifest}
assert actual == set(data['files'])
for name, row in data['files'].items():
    path = (root / name).resolve()
    assert path.is_relative_to(root) and not (root / name).is_symlink()
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
c3 = json.loads((root / 'c3-after/report.json').read_bytes())
cyd = json.loads((root / 'cyd-after/report.json').read_bytes())
target = json.loads((root / 'target-4/report.json').read_bytes())
assert c3['passed'] and c3['full_suite'] and len(c3['cases']) == 42 and len(c3['negative_controls']) == 7
assert cyd['passed'] and cyd['status_key_comparison']['padding_ignored'] and cyd['status_key_comparison']['string_tails_ignored']
assert target['passed'] and not target['full_app_configured_or_built']
print('PASS retained WS evidence integrity; CYD59/C342+7; focused targets only, no physical qualification')
