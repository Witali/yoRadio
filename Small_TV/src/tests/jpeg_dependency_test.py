"""Offline JPEG inputs and cached build corruption must fail closed."""
import argparse
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('jpeg_dependency', PROJECT / 'tools/build_jpeg_library.py')
dependency = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dependency)
SELECTION = None


class BundleTests(unittest.TestCase):
    """Keep complete source, licenses and qualified patch bytes available offline."""

    def setUp(self):
        """Faults modify only a temporary copy of the saved source dependency."""
        self.temporary = tempfile.TemporaryDirectory(prefix='small-tv-jpeg-')
        self.addCleanup(self.temporary.cleanup)
        self.vendor = Path(self.temporary.name) / 'vendor'
        shutil.copytree(dependency.VENDOR, self.vendor)

    def test_saved_bundle_and_qualified_patches(self):
        """Production adaptations must match the previously qualified source."""
        upstream = dependency.verify_bundle(self.vendor)
        self.assertEqual(upstream['commit'], 'c85e6b905bf237038faa936dab160ebfc5da0344')
        probe = PROJECT / 'tests/jpeg_library_probe'
        for key in dependency.PATCH_KEYS:
            self.assertEqual((self.vendor / upstream[key]).read_bytes(), (probe / upstream[key]).read_bytes())
        self.assertIn('Independent JPEG Group', (self.vendor / 'README.md').read_text())

    def test_gzip_corruption(self):
        """Reject altered compressed bytes before attempting patch application."""
        archive = self.vendor / 'upstream.tar.gz'
        data = bytearray(archive.read_bytes())
        data[len(data) // 2] ^= 1
        archive.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'compressed source'):
            dependency.verify_bundle(self.vendor)

    def test_uncompressed_archive_corruption(self):
        """A matching gzip checksum cannot substitute different upstream bytes."""
        archive = self.vendor / 'upstream.tar.gz'
        data = bytearray(gzip.decompress(archive.read_bytes()))
        data[1024] ^= 1
        archive.write_bytes(gzip.compress(data, mtime=0))
        bundle = self.vendor / 'BUNDLE.json'
        metadata = json.loads(bundle.read_text())
        metadata['gzip_sha256'] = dependency.sha(archive)
        dependency.save_json(bundle, metadata)
        with self.assertRaisesRegex(ValueError, 'upstream source'):
            dependency.verify_bundle(self.vendor)

    def test_archive_size(self):
        """The original tar length is checked separately from gzip file size."""
        bundle = self.vendor / 'BUNDLE.json'
        metadata = json.loads(bundle.read_text())
        metadata['tar_bytes'] -= 1
        dependency.save_json(bundle, metadata)
        with self.assertRaisesRegex(ValueError, 'upstream source'):
            dependency.verify_bundle(self.vendor)

    def test_revision_disagreement(self):
        """Bundle and upstream provenance may not identify different revisions."""
        bundle = self.vendor / 'BUNDLE.json'
        metadata = json.loads(bundle.read_text())
        metadata['commit'] = '0' * 40
        dependency.save_json(bundle, metadata)
        with self.assertRaisesRegex(ValueError, 'revision'):
            dependency.verify_bundle(self.vendor)

    def test_every_patch_corruption(self):
        """All three adaptations are mandatory and pinned independently."""
        upstream = dependency.verify_bundle(self.vendor)
        for key in dependency.PATCH_KEYS:
            with self.subTest(key=key):
                path = self.vendor / upstream[key]
                saved = path.read_bytes()
                try:
                    path.write_bytes(saved + b'\n')
                    with self.assertRaisesRegex(ValueError, 'adaptation patch'):
                        dependency.verify_bundle(self.vendor)
                finally:
                    path.write_bytes(saved)

    def test_every_license_corruption(self):
        """The bundled archive does not replace retaining readable license files."""
        upstream = dependency.verify_bundle(self.vendor)
        for name in upstream['license_files']:
            with self.subTest(name=name):
                path = self.vendor / name
                saved = path.read_bytes()
                try:
                    path.write_bytes(saved + b'changed')
                    with self.assertRaisesRegex(ValueError, 'license'):
                        dependency.verify_bundle(self.vendor)
                finally:
                    path.write_bytes(saved)


@unittest.skipIf(SELECTION is None, 'Pass --selection to test an actual compiled dependency')
class CachedBuildTests(unittest.TestCase):
    """Exercise real incremental-build refusal without recompiling or fake tools."""

    def setUp(self):
        """Clone the verified source/archive, keeping the original build unchanged."""
        selection = json.loads(SELECTION.read_text())
        original = Path(selection['build_directory'])
        self.temporary = tempfile.TemporaryDirectory(prefix='small-tv-jpeg-cache-')
        self.addCleanup(self.temporary.cleanup)
        output = Path(self.temporary.name)
        self.directory = output / selection['fingerprint']
        self.directory.mkdir()
        for name in ('source', 'library'):
            source = original / name
            if name == 'source':
                shutil.copytree(source, self.directory / name)
            else:
                (self.directory / name).mkdir()
                for path in [source / 'libjpeg.a', *source.glob('*.h')]:
                    shutil.copyfile(path, self.directory / name / path.name)
        for name in ('rv32-toolchain.cmake', 'report.json'):
            shutil.copyfile(original / name, self.directory / name)
        report = json.loads((original / 'report.json').read_text())
        tools = {Path(p).name: Path(p) for p in report['build_inputs']['tools']}
        self.arguments = argparse.Namespace(vendor=dependency.VENDOR, output=output,
            toolchain_bin=tools['riscv32-esp-elf-gcc.exe'].parent,
            cmake=tools['cmake.exe'], ninja=tools['ninja.exe'])

    def reuse(self):
        """Run the production verification path on genuine compiler products."""
        with contextlib.redirect_stdout(io.StringIO()):
            dependency.build(self.arguments)

    def test_unchanged_reuse(self):
        """Repeated app builds need no separate upstream checkout or network."""
        self.reuse()

    def test_changed_private_header(self):
        """A stale archive paired with a changed private ABI must be rejected."""
        path = self.directory / 'source/src/jpegint.h'
        path.write_bytes(path.read_bytes() + b'\n/* modified */\n')
        with self.assertRaisesRegex(ValueError, 'Cached JPEG build changed'):
            self.reuse()

    def test_changed_configured_header(self):
        """Generated precision/ABI configuration is part of the verified build."""
        path = self.directory / 'library/jconfig.h'
        path.write_bytes(path.read_bytes() + b'\n#define ALTERED 1\n')
        with self.assertRaisesRegex(ValueError, 'Cached JPEG build changed'):
            self.reuse()

    def test_changed_library(self):
        """Never reuse a damaged or silently replaced target archive."""
        path = self.directory / 'library/libjpeg.a'
        data = bytearray(path.read_bytes())
        data[-1] ^= 1
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'Cached JPEG build changed'):
            self.reuse()

    def test_wrong_reported_library_digest(self):
        """The digest handed to cache identity generation must match the archive."""
        path = self.directory / 'report.json'
        report = json.loads(path.read_text())
        report['library_sha256'] = '0' * 64
        dependency.save_json(path, report)
        with self.assertRaisesRegex(ValueError, 'Cached JPEG build changed'):
            self.reuse()

    def test_incomplete_build(self):
        """Interrupted dependency builds cannot be mistaken for reusable results."""
        (self.directory / 'report.json').unlink()
        with self.assertRaisesRegex(ValueError, 'Incomplete JPEG build'):
            self.reuse()


def main():
    """Run bundle controls and, when supplied, genuine compiler-product controls."""
    global SELECTION
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', type=Path)
    arguments, remaining = parser.parse_known_args()
    SELECTION = arguments.selection
    # Decorators run at import time, before CLI arguments are available.
    CachedBuildTests.__unittest_skip__ = SELECTION is None
    unittest.main(argv=[__file__, *remaining])


if __name__ == '__main__':
    main()
