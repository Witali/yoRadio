"""Regress erase/program observation without weakening the persistence condition."""
from pathlib import Path
import tempfile
import unittest
import json

from raw_flash_observer import read_stored_key, persistence_complete


class RawFlashTests(unittest.TestCase):
    def test_erased_incomplete_or_invalid_is_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'flash.bin'
            for data in (b'\xff'*20,b'US-H',b'US-H'+b'\xff'*16,b'\xff\0'+bytes(18),
                         b'\0'*20,b'X\x01\0'+bytes(17)):
                with self.subTest(data=data):
                    path.write_bytes(data)
                    self.assertIsNone(read_stored_key(path,0))

    def test_maximum_key_and_original_offset(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'flash.bin'
            value = 'ZZ-ABCDEFGHIJKLMNOP'
            path.write_bytes(bytes(199)+value.encode()+b'\0')
            self.assertEqual(read_stored_key(path,199),value)

    def test_matching_first_page_with_dirty_settings_is_not_complete(self):
        self.assertFalse(persistence_complete(lambda:'US-H','US-H',lambda:b'\1'))
        self.assertFalse(persistence_complete(lambda:None,'US-H',lambda:b'\0'))
        self.assertFalse(persistence_complete(lambda:'GB','US-H',lambda:b'\0'))
        self.assertTrue(persistence_complete(lambda:'US-H','US-H',lambda:b'\0'))

    def test_flag_changed_during_image_read_is_not_complete(self):
        values = iter((b'\0',b'\1'))
        self.assertFalse(persistence_complete(lambda:'US-H','US-H',lambda:next(values)))

    def test_factory_requires_the_exact_key(self):
        self.assertFalse(persistence_complete(lambda:None,'US-H'))
        self.assertFalse(persistence_complete(lambda:'US','US-H'))
        self.assertTrue(persistence_complete(lambda:'US-H','US-H'))


def run_tests():
    """Expose the same five negative/positive controls to the full QEMU suite."""
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(RawFlashTests))
    return {'passed':result.wasSuccessful(),'tests':result.testsRun}


if __name__ == '__main__':
    report=run_tests()
    print(json.dumps(report))
    raise SystemExit(0 if report['passed'] else 1)
