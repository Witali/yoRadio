"""Check the exact SDK RX routing diff and reject unaudited SDK changes."""
import argparse
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from patch_tls_rx_reserve import patch, RX_FUNCTIONS, DECLARATION


class RxRoutingTests(unittest.TestCase):
    source = b''

    def test_only_four_rx_allocation_calls_change(self):
        result = patch(self.source).decode()
        original = self.source.decode().replace('\r\n', '\n')
        self.assertEqual(result.count('yoradio_tls_rx_calloc('), 5)  # Four calls and declaration.
        for name in RX_FUNCTIONS:
            start = result.index(name + '(mbedtls_ssl_context *ssl)')
            end = result.index('\n}\n', start)
            body = result[start:end]
            self.assertEqual(body.count('yoradio_tls_rx_calloc('), 1)
            self.assertNotIn('mbedtls_calloc(', body)
        # Every free, parser, length check, crypto operation and TX path is exact.
        restored = result.replace(DECLARATION, '').replace('yoradio_tls_rx_calloc(', 'mbedtls_calloc(')
        self.assertEqual(restored, original)

    def test_line_endings_do_not_change_audited_source_identity(self):
        lf = self.source.replace(b'\r\n', b'\n')
        self.assertEqual(patch(lf), patch(lf.replace(b'\n', b'\r\n')))

    def test_reject_changed_sdk_and_double_patch(self):
        for changed in (self.source + b'\n', patch(self.source),
                        self.source.replace(b'mbedtls_calloc', b'changed_calloc', 1)):
            with self.subTest(), self.assertRaisesRegex(ValueError, 'Unaudited'):
                patch(changed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    args, rest = parser.parse_known_args()
    RxRoutingTests.source = args.source.read_bytes()
    unittest.main(argv=[sys.argv[0], *rest])
