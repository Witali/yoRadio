"""Filesystem-only content-addressed archive collection; no tool execution."""
import gzip
import hashlib
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hashfile(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def binary(path, prefix):
    return prefix.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')) or Path(path).suffix.lower() in ('.a', '.bin', '.dll', '.elf', '.exe', '.o', '.obj', '.pyc', '.zip')


class Collector:
    def __init__(self):
        self.entries, self.bindings = [], []
        self.keys, self.payloads, self.files, self.observed = {}, {}, {}, {}

    def add(self, path, role, expected=None, original=None, preferred=None):
        path = Path(path).resolve()
        size, digest = path.stat().st_size, hashfile(path)
        require(expected is None or digest == expected, 'Input identity changed: ' + str(path))
        self.observed[str(path)] = {'sha256': digest, 'bytes': size}
        key = (str(original or path), digest)
        if key in self.keys:
            row = self.entries[self.keys[key]]
            if role not in row['roles']:
                row['roles'].append(role)
            return row
        row = {'id': len(self.entries), 'original_path': key[0], 'sha256': digest, 'bytes': size,
               'observed_bytes': True, 'observed_from': str(path), 'roles': [role]}
        with path.open('rb') as source:
            prefix = source.read(16)
        if binary(path, prefix):
            row.update(disposition='omitted', reason='Binary executable/object/archive/firmware/ROM/tool deliberately omitted; identity only')
        else:
            raw = path.read_bytes()
            require(len(raw) == size and sha(raw) == digest, 'Input changed while reading')
            if digest not in self.payloads:
                compressed = preferred is None and (path.suffix.lower() == '.log' or size >= 131072)
                name = preferred or 'raw/' + digest[:2] + '/' + digest + ('.gz' if compressed else '')
                data = gzip.compress(raw, compresslevel=9, mtime=0) if compressed else raw
                self.files[name] = data
                self.payloads[digest] = {'stored_path': name, 'encoding': 'gzip' if compressed else 'raw',
                                         'stored_sha256': sha(data), 'stored_bytes': len(data)}
            row.update(disposition='stored', **self.payloads[digest])
        self.keys[key] = row['id']
        self.entries.append(row)
        return row

    def reported_tool(self, original, digest):
        """Linux tool identity recorded by the original host; never launch WSL."""
        key = (original, digest)
        if key in self.keys:
            return self.entries[self.keys[key]]
        row = {'id': len(self.entries), 'original_path': original, 'sha256': digest, 'bytes': None,
               'observed_bytes': False, 'roles': ['original host-reported Linux tool identity'],
               'disposition': 'omitted', 'reason': 'Linux tool was hashed by the original host gate; no WSL/tool process or binary recopy during packaging'}
        self.keys[key] = row['id']
        self.entries.append(row)
        return row

    def bind(self, container, tokens, target):
        self.bindings.append({'container_id': container['id'], 'hash_tokens': tokens, 'target_id': target['id']})

    def tree(self, folder, role):
        for path in sorted(Path(folder).rglob('*')):
            if path.is_file():
                self.add(path, role)

    def stable(self):
        require(all(Path(path).stat().st_size == row['bytes'] and hashfile(path) == row['sha256'] for path, row in self.observed.items()), 'Selected archival input changed')
