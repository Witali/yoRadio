"""Check complete raw archive bytes against manifests and the staged Git blobs."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path.cwd()
for name in sys.argv[1:]:
    folder = (root / name).resolve()
    assert folder.is_relative_to(root / 'tests/results')
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    rows = manifest['files']
    records = rows if isinstance(rows, dict) else {row['path']: row for row in rows}
    assert len(records) == len(rows)
    actual = sorted(path for path in folder.rglob('*') if path.is_file())
    assert {path.relative_to(folder).as_posix() for path in actual} == set(records) | {'manifest.json'}
    for relative, row in records.items():
        path = (folder / relative).resolve()
        assert path.is_relative_to(folder)
        data = path.read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    query = ''.join(':' + path.relative_to(root).as_posix() + '\n' for path in actual)
    data = subprocess.check_output(['git', '-c', 'core.longpaths=true', 'cat-file', '--batch'], input=query.encode())
    offset = 0
    for path in actual:
        end = data.index(b'\n', offset)
        header = data[offset:end].split()
        assert len(header) == 3 and header[1] == b'blob', (path, header)
        size = int(header[2]); offset = end + 1
        blob = data[offset:offset + size]; offset += size + 1
        assert blob == path.read_bytes(), path
    assert offset == len(data)
    print('Verified staged raw archive', name, len(actual), 'files')
