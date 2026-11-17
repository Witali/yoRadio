"""Pin current AAC regression inputs without weakening the historical default."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('aac_tasks', Path(__file__).with_name('run-cyd-aac-playback-task-qemu.py'))
tasks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tasks)


class SourceReleaseTests(unittest.TestCase):
    def setUp(self):
        self.release = dict(files={name: dict(sha256=tasks.sha(tasks.ROOT / name),
            bytes=(tasks.ROOT / name).stat().st_size) for name in sorted(tasks.SOURCE_RELEASE_FILES)})
        self.temp = tempfile.TemporaryDirectory(prefix='aac-reviewed-release-')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'release.json'

    def write(self, release):
        body = (json.dumps(release, sort_keys=True) + '\n').encode()
        self.path.write_bytes(body)
        return hashlib.sha256(body).hexdigest()

    def test_current_manifest_requires_its_exact_explicit_digest(self):
        digest = self.write(self.release)
        self.assertEqual(tasks.reviewed_source_release(self.path, digest), self.release)
        self.assertEqual(tasks.SOURCE_RELEASE_SHA, '73599ab651a72f153e777bc47dec5d816e1e38224e0795195db426da11c1d3e7')
        for other in ('0' * 64, digest.upper(), '', tasks.SOURCE_RELEASE_SHA):
            with self.subTest(other=other), self.assertRaises(ValueError):
                tasks.reviewed_source_release(self.path, other)

    def test_missing_and_substituted_files_cannot_narrow_the_check(self):
        name = sorted(tasks.SOURCE_RELEASE_FILES)[0]
        for substitute in (None, 'README.md', '../outside.c', 'C:/external.c'):
            release = copy.deepcopy(self.release)
            value = release['files'].pop(name)
            if substitute is not None:
                release['files'][substitute] = value
            digest = self.write(release)
            with self.subTest(substitute=substitute), self.assertRaises(ValueError):
                tasks.reviewed_source_release(self.path, digest)

    def test_stale_hash_and_size_are_rejected(self):
        for key, value in (('sha256', '0' * 64), ('bytes', 1)):
            release = copy.deepcopy(self.release)
            release['files'][sorted(tasks.SOURCE_RELEASE_FILES)[0]][key] = value
            digest = self.write(release)
            with self.subTest(key=key), self.assertRaises(ValueError):
                tasks.reviewed_source_release(self.path, digest)


if __name__ == '__main__':
    unittest.main()
