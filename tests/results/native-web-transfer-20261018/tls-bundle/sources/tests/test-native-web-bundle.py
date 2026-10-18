"""Structural and secret destination regressions; no real keys are persisted."""
import importlib.util
from pathlib import Path
import stat
import struct
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'idf/components/native_web_transport/tools/pack_tls_bundle.py'
spec = importlib.util.spec_from_file_location('pack_tls_bundle', SOURCE)
packer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packer)


class BundleTests(unittest.TestCase):
    def test_header_and_nvs_namespace(self):
        bundle = packer.build_bundle(b'certificate', b'private')
        self.assertEqual(struct.unpack('<4sHHII', bundle[:16]), (b'NTLS', 1, 1, 11, 7))
        self.assertEqual(bundle[16:], b'certificateprivate')
        self.assertEqual(packer.encode_output(bundle, True).decode().splitlines(),
                         ['key,type,encoding,value', 'web_tls,namespace,,',
                          'bundle,data,hex2bin,' + bundle.hex()])

    def test_maintenance(self):
        self.assertEqual(packer.build_bundle(maintenance=True), b'NTLS\1\0' + b'\0' * 10)
        with self.assertRaises(ValueError):
            packer.build_bundle(b'cert', maintenance=True)

    def test_lengths_and_nul(self):
        for cert, key in [(b'', b'key'), (b'cert', b''), (b'\0', b'key'),
                          (b'cert', b'\0'), (b'c' * 8193, b'key'),
                          (b'cert', b'k' * 4097)]:
            with self.subTest(lengths=(len(cert), len(key))):
                with self.assertRaises(ValueError):
                    packer.build_bundle(cert, key)
        self.assertEqual(len(packer.build_bundle(b'c' * 8192, b'k' * 4096)), 12304)

    def test_reject_every_repository_destination(self):
        roots = packer.repository_roots()
        self.assertTrue(roots)
        for root in roots:
            for suffix in ['firmware/tls.bin', 'tests/results/key.csv', '.build/key.bin']:
                with self.assertRaises(ValueError):
                    packer.check_secret_destination(root / suffix)

    def test_private_exclusive_output_and_bounded_read(self):
        with tempfile.TemporaryDirectory(prefix='native-web-bundle-') as folder:
            output = Path(folder) / 'synthetic.bin'
            packer.write_secret(output, b'nonsecret')
            self.assertEqual(packer.read_bounded(output, 9), b'nonsecret')
            with self.assertRaises(FileExistsError):
                packer.write_secret(output, b'replacement')
            with self.assertRaises(ValueError):
                packer.read_bounded(output, 8)
            if hasattr(stat, 'S_IMODE') and __import__('os').name == 'posix':
                self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)


if __name__ == '__main__':
    unittest.main()
