"""Keep SDK return-code signs and reject arbitrary TLS log text."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from tls_error_codes import error_detail
from common import filter_tls_line, TLS_CERTIFICATE_REJECTED, check_certificate_rejection, Failure


class ErrorCodes(unittest.TestCase):
    def test_complete_filter_preserves_codes_and_strips_colours(self):
        for colour in ('', '\x1b[0;31m'):
            for tag, body, expected in (
                ('Dynamic Impl', 'mbedtls_ssl_fetch_input error=80', 'fetch_input'),
                ('esp-tls-mbedtls', 'read error :-0x0050', 'read'),
            ):
                with self.subTest(colour=colour, tag=tag):
                    self.assertEqual(filter_tls_line(f'{colour}E (123) {tag}: {body}\x1b[0m'),
                                     f'TLS failure: component={tag} operation={expected} mbedtls_return=-80')

    def test_filter_retains_generic_errors_and_existing_allocation_evidence(self):
        self.assertEqual(filter_tls_line('E (123) Dynamic Impl: alloc(17058 bytes) failed'),
                         'TLS failure: component=Dynamic Impl allocation_bytes=17058')
        for body in ('unknown error for private.example',
                     'read error :-0x0050 host=private.example',
                     'certificate subject: private.example 0x0050'):
            with self.subTest(body=body):
                self.assertEqual(filter_tls_line(f'E (123) esp-tls-mbedtls: {body}'),
                                 'TLS failure: component=esp-tls-mbedtls')
        self.assertIsNone(filter_tls_line('I (123) esp-tls-mbedtls: read error :-0x0050'))
        self.assertIsNone(filter_tls_line('E (123) private-tag: read error :-0x0050'))

    def test_certificate_gate_does_not_accept_a_numeric_handshake_code_alone(self):
        marker = filter_tls_line('E (123) esp-x509-crt-bundle: Failed to verify certificate')
        self.assertEqual(marker, TLS_CERTIFICATE_REJECTED)
        code = filter_tls_line('E (123) esp-tls-mbedtls: mbedtls_ssl_handshake returned -0x2700')
        with self.assertRaises(Failure):
            check_certificate_rejection(['TLSV1_ALERT_ACCESS_DENIED'], [dict(line=code)])
        self.assertTrue(check_certificate_rejection(['TLSV1_ALERT_ACCESS_DENIED'], [dict(line=marker)]))

    def test_sdk_formats_and_signed_return(self):
        cases = [
            ('Dynamic Impl', 'mbedtls_ssl_fetch_input error=80', 'fetch_input', -80),
            ('esp-tls-mbedtls', 'read error :-0x0050', 'read', -80),
            ('esp-tls-mbedtls', 'write error :-0x004c', 'write', -76),
            ('esp-tls-mbedtls', 'mbedtls_ssl_handshake returned -0x2700', 'handshake', -9984),
        ]
        for component, body, operation, code in cases:
            with self.subTest(body=body):
                self.assertEqual(error_detail(component, body),
                                 f' operation={operation} mbedtls_return={code}')

    def test_decimal_and_hex_match_for_unknown_negative_returns(self):
        for value in (1, 76, 80, 0x2700, 0x7f80, 0x7fffffff):
            with self.subTest(value=value):
                decimal = error_detail('Dynamic Impl', f'mbedtls_ssl_fetch_input error={value}')
                hexadecimal = error_detail('esp-tls-mbedtls', f'read error :-0x{value:04X}')
                self.assertTrue(decimal.endswith(f'mbedtls_return={-value}'))
                self.assertTrue(hexadecimal.endswith(f'mbedtls_return={-value}'))

    def test_wrong_component_and_noncanonical_messages_are_not_interpreted(self):
        for component, body in [
            ('esp-tls', 'read error :-0x0050'),
            ('SSL client', 'mbedtls_ssl_fetch_input error=80'),
            ('Dynamic Impl', 'read error :-0x0050'),
            ('esp-tls-mbedtls', 'mbedtls_ssl_fetch_input error=80'),
            ('Dynamic Impl', 'mbedtls_ssl_fetch_input error=-80'),
            ('Dynamic Impl', 'mbedtls_ssl_fetch_input error=0'),
            ('Dynamic Impl', 'mbedtls_ssl_fetch_input error=2147483648'),
            ('Dynamic Impl', 'mbedtls_ssl_fetch_input error=' + '9' * 100),
            ('Dynamic Impl', 'mbedtls_ssl_fetch_input error=٨٠'),
            ('esp-tls-mbedtls', 'read error :-0x80000000'),
            ('esp-tls-mbedtls', 'read error :-0x0000'),
            ('esp-tls-mbedtls', 'read error :-0x50'),
            ('esp-tls-mbedtls', 'read error :-0x0050 host=private.example'),
            ('esp-tls-mbedtls', 'subject=private.example read error :-0x0050'),
            ('Dynamic Impl', 'mbedtls_ssl_fetch_input error=80\nprivate.example'),
            ('esp-tls-mbedtls', 'alloc(17058 bytes) failed'),
        ]:
            with self.subTest(component=component, body=body):
                self.assertEqual(error_detail(component, body), '')


if __name__ == '__main__':
    unittest.main()
