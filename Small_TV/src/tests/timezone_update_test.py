"""Check offline timezone maintenance, rejected archives and optional real-wheel reproduction."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT/'Small_TV/src'
sys.path.insert(0, str(PROJECT/'tools'))
from prepare_timezones import generate_timezones, load_zones
from update_timezones import fetch, snapshot, validate_pin, wheel_record, write_snapshot

REFERENCE, _ = load_zones()
SOURCE = PROJECT/'resources/timezones'
TEMP_ROOT = ROOT/'.build/small-tv-parity/timezone-update/temporary'


def temporary_directory():
    """Keep disposable test files inside the repository's writable build area."""
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=TEMP_ROOT)


def digest(data):
    """Identify data bytes independently from wheel metadata."""
    return hashlib.sha256(data).hexdigest()


def fixture(changes=None, duplicate=None):
    """Build controlled malformed candidates using unchanged committed IANA data."""
    members = {'tzdata/__init__.py': (
        f"__version__ = '{REFERENCE['package_version']}'\n"
        f"IANA_VERSION = '{REFERENCE['iana_version']}'\n"
        "raise RuntimeError('Data archive code must never execute')\n").encode()}
    for row in REFERENCE['files']:
        members['tzdata/zoneinfo/'+row['zone']] = (SOURCE/row['file']).read_bytes()
    for name, data in (changes or {}).items():
        if data is None:
            del members[name]
        else:
            members[name] = data
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in members.items():
            archive.writestr(name, data)
        if duplicate:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', message='Duplicate name:', category=UserWarning)
                archive.writestr(duplicate, members[duplicate])
    data = output.getvalue()
    pin = validate_pin(REFERENCE['iana_version'], REFERENCE['package_version'], digest(data))
    return data, pin


def compare_snapshot(wheel, pin):
    """Require every selected raw file and the generated firmware header to reproduce."""
    manifest, contents = snapshot(wheel, REFERENCE, pin)
    for row in REFERENCE['files']:
        if contents[row['file']] != (SOURCE/row['file']).read_bytes():
            raise AssertionError('Pinned timezone bytes did not reproduce: '+row['zone'])
    if manifest['countries'] != REFERENCE['countries'] or manifest['default_country'] != REFERENCE['default_country']:
        raise AssertionError('Country mapping/default changed during download')
    with temporary_directory() as temporary:
        root = Path(temporary)
        candidate = root/'data'
        write_snapshot(candidate, contents)
        baseline, regenerated = root/'baseline', root/'regenerated'
        baseline.mkdir()
        regenerated.mkdir()
        generate_timezones(baseline)
        generate_timezones(regenerated, candidate)
        header = (regenerated/'timezone_data.h').read_bytes()
        if header != (baseline/'timezone_data.h').read_bytes():
            raise AssertionError('Generated firmware timezone tables changed')
    return {'zones_reproduced': len(manifest['files']), 'country_keys': len(manifest['countries']),
            'generated_header_sha256': digest(header), 'wheel_sha256': digest(wheel)}


class TimezoneUpdateTests(unittest.TestCase):
    """Exercise archive validation and preserve usable data on rejected candidates."""
    def test_offline_roundtrip(self):
        """Reproduction does not install or execute archive code and preserves all rules."""
        wheel, pin = fixture()
        self.assertEqual(compare_snapshot(wheel, pin)['zones_reproduced'], len(REFERENCE['files']))

    def test_corrupt_wheel(self):
        """Byte corruption fails the pinned digest before any data is accepted."""
        wheel, pin = fixture()
        with self.assertRaisesRegex(ValueError, 'digest'):
            snapshot(wheel+b'corruption', REFERENCE, pin)

    def test_wrong_declared_versions(self):
        """A valid archive digest cannot hide different IANA or package editions."""
        for declared in ((f"__version__ = '{REFERENCE['package_version']}'\nIANA_VERSION = '1900a'\n").encode(),
                         (f"__version__ = '1900.1'\nIANA_VERSION = '{REFERENCE['iana_version']}'\n").encode()):
            with self.subTest(declared=declared):
                wheel, pin = fixture({'tzdata/__init__.py': declared})
                with self.assertRaisesRegex(ValueError, 'declares a different'):
                    snapshot(wheel, REFERENCE, pin)

    def test_missing_and_duplicate_zone(self):
        """Reject missing/ambiguous data instead of producing a partial timezone table."""
        member = 'tzdata/zoneinfo/'+REFERENCE['files'][0]['zone']
        for wheel, pin in (fixture({member: None}), fixture(duplicate=member)):
            with self.assertRaisesRegex(ValueError, 'Missing, duplicate'):
                snapshot(wheel, REFERENCE, pin)

    def test_unsupported_future_rule(self):
        """An implicit DST recurrence cannot silently replace explicit IANA rules."""
        row = next(row for row in REFERENCE['files'] if row['zone']=='Europe/London')
        data = (SOURCE/row['file']).read_bytes()
        data = data[:data.rfind(b'\n', 0, len(data)-1)+1]+b'EST5EDT\n'
        wheel, pin = fixture({'tzdata/zoneinfo/'+row['zone']: data})
        with self.assertRaisesRegex(ValueError, 'implicit POSIX'):
            snapshot(wheel, REFERENCE, pin)

    def test_rejected_update_preserves_existing_files(self):
        """Validate all inputs before touching an existing snapshot or unrelated files."""
        with temporary_directory() as temporary:
            output = Path(temporary)
            sentinel = output/'manifest.json'
            sentinel.write_bytes(b'known-good-manifest')
            wheel, pin = fixture({'tzdata/zoneinfo/Europe/London': b'not TZif'})
            with self.assertRaises(ValueError):
                _, contents = snapshot(wheel, REFERENCE, pin)
                write_snapshot(output, contents)
            self.assertEqual(sentinel.read_bytes(), b'known-good-manifest')
            (output/'README.md').write_bytes(b'keep documentation')
            write_snapshot(output, {'manifest.json': b'validated', 'example.tzif': b'data'})
            self.assertEqual((output/'README.md').read_bytes(), b'keep documentation')

    def test_invalid_pins(self):
        """Reject partial/malformed URL and digest components before downloading."""
        for pin in [('2026e/../', '2026.5', 'a'*64), ('2026e', '../2026.5', 'a'*64),
                    ('2026e', '2026.5', 'not-a-sha256')]:
            with self.assertRaises(ValueError):
                validate_pin(*pin)

    def test_unexpected_download_origin(self):
        """Reject non-HTTPS, different hosts and credentials before opening a connection."""
        for url in ('http://pypi.org/pypi/tzdata/json', 'https://example.com/data',
                    'https://user:password@pypi.org/data', 'https://pypi.org:444/data'):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, 'download URL'):
                fetch(url, 128, 'pypi.org')

    def test_published_wheel_digest_and_yanking(self):
        """Reject transport metadata that no longer matches a selected release."""
        row = {'filename': 'tzdata-2026.5-py2.py3-none-any.whl', 'packagetype': 'bdist_wheel',
               'yanked': False, 'digests': {'sha256': 'a'*64}}
        metadata = {'info': {'version': '2026.5'}, 'urls': [row]}
        self.assertIs(wheel_record(metadata, '2026.5', 'a'*64), row)
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            wheel_record(metadata, '2026.5', 'b'*64)
        row['yanked'] = True
        with self.assertRaisesRegex(ValueError, 'non-yanked'):
            wheel_record(metadata, '2026.5', 'a'*64)


def main():
    """Run offline cases, optionally reproducing the actual pinned publisher archive."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--wheel', type=Path, help='Also reproduce the real pinned wheel offline')
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TimezoneUpdateTests))
    reproduction = {'status': 'not_run', 'reason': 'No --wheel supplied; controlled archive cases ran offline'}
    if result.wasSuccessful() and args.wheel:
        pin = validate_pin(REFERENCE['iana_version'], REFERENCE['package_version'], REFERENCE['wheel_sha256'])
        try:
            reproduction = {'status': 'passed', **compare_snapshot(args.wheel.read_bytes(), pin)}
        except (OSError, ValueError, AssertionError, zipfile.BadZipFile) as error:
            reproduction = {'status': 'failed', 'error': str(error)}
    paths = [Path(__file__).resolve(), PROJECT/'tools/update_timezones.py', PROJECT/'tools/prepare_timezones.py',
             PROJECT/'app/services/country_timezones.h', SOURCE/'manifest.json']
    paths += [SOURCE/row['file'] for row in REFERENCE['files']]
    report = {'passed': result.wasSuccessful() and reproduction['status'] != 'failed', 'tests': result.testsRun,
              'iana_version': REFERENCE['iana_version'], 'wheel_reproduction': reproduction,
              'inputs': [{'file': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes())}
                         for path in paths]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
