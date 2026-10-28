"""Validate the immutable dump and the exact archived firmware being tested."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'Small_TV/src'
ARCHIVE = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed'
RESOURCES = ROOT / '.build/small-tv-esp32c2/resources'
FACTORY_SHA = '5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4'


def sha(data):
    """Return a reproducible content identity for a test input."""
    return hashlib.sha256(data).hexdigest()


class ArtifactTests(unittest.TestCase):
    """Check release-input integrity independently of emulators and production code."""
    def test_original_flash(self):
        data = (ROOT / 'Small_TV/full-flash.bin').read_bytes()
        self.assertEqual(len(data), 4 * 1024 * 1024)
        self.assertEqual(sha(data), FACTORY_SHA)

    def test_image_manifest_and_flash_bounds(self):
        manifest = json.loads((ARCHIVE / 'manifest.json').read_text())
        self.assertEqual(manifest['target'], 'esp32c2')
        self.assertEqual(manifest['flash_bytes'], 0x400000)
        previous_end = 0
        for item in manifest['images']:
            data = (ARCHIVE / item['file']).read_bytes()
            self.assertEqual(len(data), item['bytes'])
            self.assertEqual(sha(data), item['sha256'])
            offset = int(item['offset'], 0)
            self.assertGreaterEqual(offset, previous_end)
            previous_end = offset + len(data)
            self.assertLessEqual(previous_end, 0x400000)
        self.assertLessEqual(len((ARCHIVE / 'app.bin').read_bytes()), 0x177000)
        self.assertEqual(previous_end, 0x3e7000)  # raw preferences are outside the assets

    def test_esp_image_checksums(self):
        for filename in ('app.bin', 'bootloader.bin'):
            with self.subTest(image=filename):
                data = (ARCHIVE / filename).read_bytes()
                self.assertEqual(data[0], 0xe9)
                self.assertTrue(1 <= data[1] <= 16)
                cursor, checksum = 24, 0xef
                for _ in range(data[1]):
                    _, length = struct.unpack_from('<II', data, cursor)
                    cursor += 8
                    self.assertLessEqual(cursor + length, len(data))
                    for byte in data[cursor:cursor + length]:
                        checksum ^= byte
                    cursor += length
                # The checksum is the final byte of the next 16-byte block,
                # including when the last segment already ends at a boundary.
                footer = ((cursor + 16) // 16) * 16 - 1
                self.assertEqual(data[footer], checksum)
                self.assertEqual(data[cursor:footer], bytes(footer - cursor))
                self.assertEqual(data[23], 1)
                self.assertEqual(len(data), footer + 33)
                self.assertEqual(data[footer + 1:], hashlib.sha256(data[:footer + 1]).digest())

    def test_partition_table(self):
        data = (ARCHIVE / 'partition-table.bin').read_bytes()
        entries = []
        for offset in range(0, len(data), 32):
            magic = struct.unpack_from('<H', data, offset)[0]
            if magic == 0xebeb:
                self.assertEqual(data[offset + 16:offset + 32], hashlib.md5(data[:offset]).digest())
                break
            self.assertEqual(magic, 0x50aa)
            _, kind, subtype, start, size, name, flags = struct.unpack_from('<HBBII16sI', data, offset)
            entries.append((name.rstrip(b'\0').decode(), kind, subtype, start, size, flags))
        else:
            self.fail('Missing partition-table MD5 entry')
        self.assertEqual(entries, [('nvs', 1, 2, 0x9000, 0x6000, 0),
                                   ('phy_init', 1, 1, 0xf000, 0x1000, 0),
                                   ('factory', 0, 0, 0x10000, 0x177000, 0),
                                   ('assets', 1, 0x40, 0x200000, 0x1e7000, 0)])

    def test_archived_sources_and_generated_media(self):
        recorded = json.loads((ARCHIVE / 'source-manifest.json').read_text())
        generated = json.loads((RESOURCES / 'source-manifest.json').read_text())
        self.assertEqual(generated, recorded, 'Rebuild/archive firmware after production changes')
        canonical = json.dumps(recorded['files'], separators=(',', ':'), sort_keys=True).encode()
        self.assertEqual(sha(canonical), recorded['aggregate_sha256'])
        self.assertEqual(recorded['aggregate_sha256'], json.loads((ARCHIVE / 'manifest.json').read_text())['source_sha256'])
        for item in recorded['files']:
            path = RESOURCES / item['file'][10:] if item['file'].startswith('generated/') else PROJECT / item['file']
            self.assertEqual(sha(path.read_bytes()), item['sha256'], item['file'])
        self.assertEqual((RESOURCES / 'assets.bin').read_bytes(), (ARCHIVE / 'assets.bin').read_bytes())

    def test_executed_http_contract_coverage(self):
        report = json.loads((ROOT / '.build/small-tv-esp32c2/native-tests/report.json').read_text())
        self.assertTrue(report['passed'])
        routes = {(row['method'], row['uri']): row for row in report['routes']}
        self.assertEqual(len(routes), 42)
        with (ROOT / 'Small_TV/analysis/security/registered-routes.tsv').open() as file:
            original = {({'1': 'GET', '3': 'POST'}[row['method']], row['uri'])
                        for row in csv.DictReader(file, delimiter='\t')}
        self.assertEqual(len(original), 34)
        aliases = {('GET', uri) for uri in ('/setup', '/setup.html', '/settings', '/settings.html', '/photo.html', '/advanced')}
        policy = {('GET', '/get_jpeg_write_limit'), ('POST', '/set_jpeg_write_limit')}
        self.assertEqual(set(routes), original | aliases | policy)
        for key, row in routes.items():
            self.assertGreater(row['successes'], 0, key)
            if key[0] == 'POST' and key[1] != '/restart':
                self.assertGreater(row['errors'], 0, key)

    def test_nvs_component_overlay(self):
        """Keep the new private-header correction tied to the actual archived app/ELF."""
        manifest = json.loads((ARCHIVE / 'manifest.json').read_bytes())
        linked = json.loads((ARCHIVE / 'nvs-storage-linkage.json').read_bytes())
        overlay = json.loads((ARCHIVE / 'nvs-storage-overlay.json').read_bytes())
        self.assertTrue(linked['passed'])
        self.assertEqual(linked['app_sha256'], sha((ARCHIVE / 'app.bin').read_bytes()))
        self.assertEqual(linked['elf_sha256'], manifest['elf_sha256'])
        self.assertEqual(linked['overlay'], overlay)
        self.assertEqual(linked['local_translation_units'], 17)
        self.assertTrue(linked['complete_direct_init_read_closure'])
        self.assertFalse(linked['semantic_tests_executed'])
        self.assertFalse(overlay['shared_sdk_modified'])
        self.assertEqual(overlay['source_manifest_sha256'], sha((PROJECT / 'tools/nvs_component_sources.json').read_bytes()))
        for name, digest in overlay['fragments'].items():
            self.assertEqual(digest, sha((PROJECT / 'storage/nvs' / name).read_bytes()))

    def test_keep_alive_range_linkage(self):
        """Require the archived app's actual redirect and all four checked SDK callers."""
        manifest = json.loads((ARCHIVE / 'manifest.json').read_bytes())
        linked = json.loads((ARCHIVE / 'wifi-keep-alive-linkage.json').read_bytes())
        self.assertTrue(linked['passed'])
        self.assertEqual(linked['app_sha256'], sha((ARCHIVE / 'app.bin').read_bytes()))
        self.assertEqual(linked['elf_sha256'], manifest['elf_sha256'])
        self.assertEqual(linked['replacement']['address'], linked['sdk_alias']['address'])
        self.assertEqual(len(linked['sdk_references']), 4)
        self.assertEqual({row['name'] for row in linked['callers']}, {
            'cnx_sta_pm.part.0', 'pm_tx_data_done_process',
            'pm_tx_null_data_done_process', 'pm_keep_alive_timeout_process'})
        self.assertEqual({row['name'] for row in linked['backends']}, {
            'ets_timer_arm', 'ets_timer_arm_us', 'ets_timer_disarm'})
        self.assertFalse(linked['full_runtime_lifecycle_proved'])


def main():
    """Write a fresh result on success and fail the caller on any integrity mismatch."""
    global RESOURCES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--resources', type=Path, default=RESOURCES,
                        help='Resources from the exact isolated production build being tested')
    args = parser.parse_args()
    RESOURCES = args.resources
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ArtifactTests))
    manifest = json.loads((ARCHIVE / 'manifest.json').read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'passed': result.wasSuccessful(), 'cases': result.testsRun,
                                     'failures': len(result.failures), 'errors': len(result.errors),
                                     'source_sha256': manifest['source_sha256'],
                                     'app_sha256': sha((ARCHIVE / 'app.bin').read_bytes()),
                                     'factory_flash_sha256': FACTORY_SHA}, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
