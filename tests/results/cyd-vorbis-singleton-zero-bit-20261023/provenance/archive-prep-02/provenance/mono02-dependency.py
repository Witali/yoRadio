"""Explicit read-only access to the hash-pinned committed CYD evidence archive."""
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath

DEPENDENCY = 'tests/results/cyd-vorbis-map2-20261020'
MANIFEST_SHA = 'c3e1fa16adb85d25f90339a9d4c74b6c0cbc9feac3d4097624bbe1d6553bd11c'
VERIFY_SHA = '74afcd06807e0377e0645069bdc1667ca0674aa1523139678fa27562c12059f4'


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(value):
    return str(value).replace('\\', '/')


def rel(value):
    value = norm(value)
    path = PurePosixPath(value)
    need(value and not path.is_absolute() and '..' not in path.parts and ':' not in value,
         'Unsafe relative archive path')
    return path.as_posix()


def obj(data):
    return json.loads(data.decode('utf-8-sig'))


class Dependency:
    def __init__(self, repository):
        self.repository = Path(repository).resolve()
        self.root = (self.repository / DEPENDENCY).resolve()
        need(self.root.is_relative_to(self.repository), 'Dependency path escaped repository')
        data = (self.root / 'manifest.json').read_bytes()
        need(sha(data) == MANIFEST_SHA, 'Committed CYD manifest identity differs')
        self.manifest = obj(data)
        need(self.manifest['schema'] == 'cyd-map2-checkpoint-v1', 'Wrong dependency archive schema')
        self.files = self.manifest['files']

    def read(self, key):
        key = rel(key)
        row = self.files[key]
        need(row['stored'] is not None, 'Dependency key is a binary omission: ' + key)
        path = (self.root / rel(row['stored'])).resolve()
        need(path.is_relative_to(self.root), 'Dependency stored path escaped archive')
        blob = path.read_bytes()
        need(len(blob) == row['stored_bytes'] and sha(blob) == row['stored_sha256'], 'Dependency stored bytes differ: ' + key)
        need(row['encoding'] in ('raw', 'gzip'), 'Unknown dependency encoding')
        data = gzip.decompress(blob) if row['encoding'] == 'gzip' else blob
        need(len(data) == row['raw_bytes'] and sha(data) == row['raw_sha256'], 'Dependency raw bytes differ: ' + key)
        return data

    def current(self):
        need(sha((self.root / 'manifest.json').read_bytes()) == MANIFEST_SHA,
             'Dependency manifest changed during operation')
