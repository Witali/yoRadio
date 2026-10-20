"""Bounded filesystem-only content addressing, adapted from existing archive_core.

No SDK, Git, subprocess, tests or recipe execution. The collector has no tree()
operation: callers select documents, referenced identities and named artifacts.
"""
import gzip
import hashlib
import json
from pathlib import Path

MAX_TEXT_BYTES = 64 * 1024 * 1024
MAX_UNIQUE_TEXT_BYTES = 512 * 1024 * 1024
MAX_ENTRIES = 20000
BINARY_SUFFIXES = ('.a', '.bin', '.dll', '.elf', '.exe', '.o', '.obj', '.pyc', '.so', '.zip')


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hashfile(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def ident(path):
    path = Path(path).resolve()
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': hashfile(path)}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def load(path):
    return json.loads(Path(path).read_bytes())


def write_new(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as output:
        output.write(raw)


def binary(path, prefix):
    return Path(path).suffix.lower() in BINARY_SUFFIXES or prefix.startswith((b'\x7fELF', b'MZ', b'!<arch>\n'))


def text(raw):
    raw.decode('utf-8')
    require(b'\0' not in raw, 'Unknown binary/NUL input must not be silently stored as text')


def identity_references(value, tokens=()):
    if isinstance(value, dict):
        if {'path', 'bytes', 'sha256'} <= value.keys():
            require(isinstance(value['path'], str) and type(value['bytes']) is int
                    and value['bytes'] >= 0 and isinstance(value['sha256'], str), 'Malformed identity reference')
            yield tokens, {key: value[key] for key in ('path', 'bytes', 'sha256')}
        for key, child in value.items():
            yield from identity_references(child, tokens + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from identity_references(child, tokens + (index,))


class Collector:
    def __init__(self, repository):
        self.repository = Path(repository).resolve()
        self.entries, self.bindings = [], []
        self.keys, self.payloads, self.observed = {}, {}, {}
        self.unique_text_bytes = 0

    def add(self, path, role, expected=None, preferred=None, external=None):
        path = Path(path).resolve()
        observed = ident(path)
        if expected is not None:
            require(observed == {key: expected[key] for key in ('path', 'bytes', 'sha256')},
                    'Input identity changed: ' + str(path))
        self.observed[str(path)] = observed
        key = (str(path), observed['sha256'])
        if key in self.keys:
            row = self.entries[self.keys[key]]
            if role not in row['roles']:
                row['roles'].append(role)
            return row
        require(len(self.entries) < MAX_ENTRIES, 'Bounded entry count exceeded')
        row = {'id': len(self.entries), 'original_path': str(path),
               'bytes': observed['bytes'], 'sha256': observed['sha256'],
               'roles': [role], 'observed_bytes': True}
        with path.open('rb') as stream:
            prefix = stream.read(16)
        if external is not None:
            row.update(disposition='external', repository_reference=external,
                       reason='Existing committed evidence bundle linked, not duplicated')
        elif binary(path, prefix):
            row.update(disposition='omitted', prefix_hex=prefix.hex(),
                       reason='Firmware/ELF/object/library/ROM/tool binary bytes omitted; SHA and size only')
            if path.is_relative_to(self.repository / 'firmware'):
                row['repository_reference'] = path.relative_to(self.repository).as_posix()
        else:
            require(observed['bytes'] <= MAX_TEXT_BYTES, 'Bounded individual text size exceeded')
            raw = path.read_bytes()
            require(len(raw) == observed['bytes'] and sha(raw) == observed['sha256'], 'Text changed while reading')
            text(raw)
            if row['sha256'] not in self.payloads:
                self.unique_text_bytes += len(raw)
                require(self.unique_text_bytes <= MAX_UNIQUE_TEXT_BYTES, 'Bounded unique text size exceeded')
                compressed = preferred is None and (path.suffix.lower() == '.log' or len(raw) >= 131072)
                stored = preferred or 'raw/' + row['sha256'][:2] + '/' + row['sha256'] + ('.gz' if compressed else '')
                data = gzip.compress(raw, compresslevel=9, mtime=0) if compressed else raw
                self.payloads[row['sha256']] = {'stored_path': stored, 'encoding': 'gzip' if compressed else 'raw',
                                               'stored_bytes': len(data), 'stored_sha256': sha(data)}
            row.update(disposition='stored', **self.payloads[row['sha256']])
        self.keys[key] = row['id']
        self.entries.append(row)
        return row

    def bind(self, container, tokens, target, kind='identity'):
        self.bindings.append({'container_id': container['id'], 'tokens': list(tokens),
                              'target_id': target['id'], 'kind': kind})

    def stable(self):
        require(all(ident(path) == observed for path, observed in self.observed.items()),
                'Selected archival input changed')

    def payload(self, row):
        require(row['disposition'] == 'stored', 'Only stored text has payload')
        raw = Path(row['original_path']).read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Selected input changed before encoding')
        data = gzip.compress(raw, compresslevel=9, mtime=0) if row['encoding'] == 'gzip' else raw
        require(len(data) == row['stored_bytes'] and sha(data) == row['stored_sha256'], 'Deterministic stored encoding changed')
        return data
