"""Check that the TLS fixture can retain the actual production resource policy."""
import contextlib
from datetime import datetime, timezone
import importlib.util
import io
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('openeth_profile',
    ROOT / 'tests/target/cyd_full_app_openeth_qemu/prepare-profile.py')
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)

SEED = '''CONFIG_IDF_TARGET="esp32"
CONFIG_ETH_USE_ESP32_EMAC=y
# CONFIG_ETH_USE_OPENETH is not set
# CONFIG_YORADIO_NATIVE_DIAGNOSTICS is not set
# CONFIG_FREERTOS_USE_TRACE_FACILITY is not set
# CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS is not set
CONFIG_ESP_TASK_WDT_TIMEOUT_S=5
CONFIG_ESP_INT_WDT_TIMEOUT_MS=300
CONFIG_LWIP_TCP_WND_DEFAULT=11520
CONFIG_LWIP_TCP_RECVMBOX_SIZE=10
CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN=16384
CONFIG_MBEDTLS_SSL_OUT_CONTENT_LEN=4096
# CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE is not set
CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH=""
CONFIG_UNRELATED_SETTING=17
'''


def settings(text):
    pairs = re.findall(r'(?m)^(?:CONFIG_(\w+)=(.*)|# CONFIG_(\w+) is not set)$', text)
    rows = [(key or disabled, value if key else 'n') for key, value, disabled in pairs]
    if len(dict(rows)) != len(rows):
        raise AssertionError('Duplicate sdkconfig settings')
    return dict(rows)


class OpenethProfileTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.build').mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='profile-test-', dir=ROOT / '.build')
        self.folder = Path(self.temporary.name).resolve()
        assert self.folder.is_relative_to(ROOT / '.build')
        self.addCleanup(self.temporary.cleanup)
        self.seed = self.folder / 'seed'
        self.seed.write_text(SEED, encoding='utf-8')
        self.output = self.folder / 'profile'

    def run_profile(self, *flags):
        argv = ['prepare-profile.py', '--sdkconfig', str(self.seed), '--output', str(self.output), *flags]
        with patch('sys.argv', argv):
            profile.main()
        return settings((self.output / 'sdkconfig').read_text())

    def test_plain_openeth_preserves_every_other_setting_and_creates_no_key(self):
        self.assertEqual(self.run_profile(), settings(SEED) | {'ETH_USE_OPENETH': 'y', 'ETH_USE_ESP32_EMAC': 'n'})
        self.assertEqual({p.name for p in self.output.iterdir()}, {'sdkconfig'})

    def test_tls_production_policy_preserves_watchdogs_telemetry_tcp_and_records(self):
        from cryptography import x509
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.x509.oid import ExtendedKeyUsageOID

        actual = self.run_profile('--tls-production-policy')
        self.assertEqual(actual, settings(SEED) | {
            'ETH_USE_OPENETH': 'y', 'ETH_USE_ESP32_EMAC': 'n',
            'MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE': 'y',
            'MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH': '"' + (self.output / 'ca.pem').as_posix() + '"'})
        ca = x509.load_pem_x509_certificate((self.output / 'ca.pem').read_bytes())
        server = x509.load_pem_x509_certificate((self.output / 'server.pem').read_bytes())
        key = serialization.load_pem_private_key((self.output / 'server-key.pem').read_bytes(), password=None)
        self.assertTrue(ca.extensions.get_extension_for_class(x509.BasicConstraints).value.ca)
        self.assertFalse(server.extensions.get_extension_for_class(x509.BasicConstraints).value.ca)
        now = datetime.now(timezone.utc)
        self.assertLess(server.not_valid_before_utc, now)
        self.assertGreater(server.not_valid_after_utc, now)
        self.assertEqual(str(server.extensions.get_extension_for_class(x509.SubjectAlternativeName).value[0].value), '10.0.2.100')
        self.assertIn(ExtendedKeyUsageOID.SERVER_AUTH, server.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value)
        ca.public_key().verify(server.signature, server.tbs_certificate_bytes, padding.PKCS1v15(), server.signature_hash_algorithm)
        self.assertEqual(key.public_key().public_numbers(), server.public_key().public_numbers())

    def test_legacy_tls_diagnostics_remains_explicit_and_compatible(self):
        actual = self.run_profile('--tls-diagnostics')
        expected = settings(SEED) | {'ETH_USE_OPENETH': 'y', 'ETH_USE_ESP32_EMAC': 'n',
            'MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE': 'y',
            'MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH': '"' + (self.output / 'ca.pem').as_posix() + '"',
            'YORADIO_NATIVE_DIAGNOSTICS': 'y', 'ESP_TASK_WDT_TIMEOUT_S': '30'}
        self.assertEqual(actual, expected)

    def test_production_policy_rejects_a_sampler_seed_before_creating_material(self):
        self.seed.write_text(SEED.replace('# CONFIG_YORADIO_NATIVE_DIAGNOSTICS is not set',
                                          'CONFIG_YORADIO_NATIVE_DIAGNOSTICS=y'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'quiet source'):
            self.run_profile('--tls-production-policy')
        self.assertFalse(self.output.exists())

    def test_tls_modes_are_mutually_exclusive(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            self.run_profile('--tls-production-policy', '--tls-diagnostics')
        self.assertEqual(error.exception.code, 2)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
