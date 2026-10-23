"""Check seven saved exports and staged raw/LFS bytes; no build or deployment."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

root = Path.cwd().resolve()
plan = json.loads((root / '.build/cyd-tls-static-rx-production-prep-01/plan02/plan.json').read_bytes())
fields = {'app.bin': 'app_sha256', 'sdkconfig': 'sdkconfig_sha256',
          'sdkconfig.json': 'sdkconfig_json_sha256', 'partition-table.bin': 'partition_table_sha256',
          'project_description.json': 'project_description_sha256', 'flasher_args.json': 'flasher_args_sha256'}
files = []
for row in plan['rows']:
    folder = Path(row['output']).resolve()
    assert folder.is_relative_to(root / 'firmware/development')
    assert folder.name == row['variant'] and folder.name.startswith('esp32-cyd2usb-native-static-rx-')
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    assert manifest['build_check'] == 'PASS' and manifest['target'] == 'esp32'
    assert manifest['source_commit'] == '3a563324abdca56144a40d5759def0ccfe708b3c'
    assert not manifest['source_dirty'] and not manifest['source_untracked']
    assert manifest['backend'] == row['backend']
    expected = set(fields) | {'manifest.json'} | {x['file'] for x in manifest['build_logs']}
    assert {p.name for p in folder.iterdir() if p.is_file()} == expected
    for name, field in fields.items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == manifest[field]
    for log in manifest['build_logs']:
        assert hashlib.sha256((folder / log['file']).read_bytes()).hexdigest() == log['sha256']
    assert (folder / 'app.bin').stat().st_size == manifest['app_bytes']
    files.extend(folder / name for name in sorted(expected))
assert len(plan['rows']) == 7 and len(files) == 63
query = ''.join(':' + p.relative_to(root).as_posix() + '\n' for p in files)
data = subprocess.check_output(['git', '-c', 'core.longpaths=true', 'cat-file', '--batch'], input=query.encode())
offset = 0
lfs = 0
for path in files:
    end = data.index(b'\n', offset)
    header = data[offset:end].split()
    assert len(header) == 3 and header[1] == b'blob', (path, header)
    size = int(header[2])
    offset = end + 1
    blob = data[offset:offset + size]
    offset += size + 1
    raw = path.read_bytes()
    if blob.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
        match = re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n', blob)
        assert match and hashlib.sha256(raw).hexdigest().encode() == match[1] and len(raw) == int(match[2]), path
        lfs += 1
    else:
        assert blob == raw, path
assert offset == len(data)
print(json.dumps({'passed': True, 'exports': 7, 'files': len(files), 'verified_lfs_pointers': lfs,
                  'scope': 'Saved export metadata and staged raw/LFS bytes only'}, indent=2))
