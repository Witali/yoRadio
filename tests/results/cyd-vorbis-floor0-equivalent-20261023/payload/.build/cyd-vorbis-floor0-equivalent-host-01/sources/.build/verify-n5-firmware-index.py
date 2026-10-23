import hashlib
import json
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
variants = ['esp32-cyd2usb-native-network-settings-' + prefix + backend
            for prefix in ['', 'custom-flac-'] for backend in ['pdm', 'continuous', 'legacy']]
names = []
for variant in variants:
    relative = 'firmware/development/' + variant
    manifest = json.loads((root / relative / 'manifest.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((root / relative / 'app.bin').read_bytes()).hexdigest() == manifest['app_sha256']
    names.extend(path.decode() for path in subprocess.check_output(
        ['git', '-c', 'core.longpaths=true', 'ls-files', '-z', '--', relative], cwd=root).split(b'\0') if path)
payload = subprocess.check_output(['git', 'cat-file', '--batch'],
    input=''.join(':' + name + '\n' for name in names).encode(), cwd=root)
common = Path(subprocess.check_output(['git', 'rev-parse', '--git-common-dir'], cwd=root, text=True).strip())
if not common.is_absolute():
    common = root / common
position = total = lfs = 0
oids = set()
for name in names:
    end = payload.index(b'\n', position)
    header = payload[position:end].split()
    assert header[1] == b'blob', name
    size = int(header[2])
    blob = payload[end + 1:end + 1 + size]
    position = end + size + 2
    data = (root / name).read_bytes()
    if blob.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
        match = re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n', blob)
        assert match, name
        oid = match[1].decode()
        assert hashlib.sha256(data).hexdigest() == oid and len(data) == int(match[2]), name
        assert (common / 'lfs/objects' / oid[:2] / oid[2:4] / oid).read_bytes() == data, name
        oids.add(oid)
        lfs += 1
    else:
        assert blob == data, name
    total += len(data)
assert position == len(payload) and len(names) == 54 and lfs == 12
print(json.dumps(dict(passed=True, firmware_variants=6, files=len(names), bytes=total,
                      verified_lfs_files=lfs, verified_distinct_local_lfs_objects=len(oids),
                      worktree_matches_git_or_lfs_oid=True)))
