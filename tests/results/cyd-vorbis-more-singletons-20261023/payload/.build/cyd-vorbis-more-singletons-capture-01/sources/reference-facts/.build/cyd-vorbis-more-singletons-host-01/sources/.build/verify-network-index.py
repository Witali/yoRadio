from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
folder = root / (sys.argv[1] if len(sys.argv) > 1 else 'tests/results/cyd-network-runtime-20261019')
manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
for relative, row in manifest.items():
    data = (folder / relative).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], relative
files = sorted(p for p in folder.rglob('*') if p.is_file())
queries = ''.join(':' + p.relative_to(root).as_posix() + '\n' for p in files)
result = subprocess.run(['git', 'cat-file', '--batch'], input=queries.encode(), stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, check=True, cwd=root)
position = 0
for file in files:
    end = result.stdout.index(b'\n', position)
    header = result.stdout[position:end].split()
    assert len(header) == 3 and header[1] == b'blob', (file, header)
    size = int(header[2]); position = end + 1
    data = result.stdout[position:position+size]; position += size + 1
    assert data == file.read_bytes(), ('Git changed raw evidence bytes', file)
assert position == len(result.stdout)
print('Verified', len(manifest), 'manifest entries and', len(files), 'raw staged Git blobs')
