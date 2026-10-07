"""Keep the TLS RAM result and its unresolved full-HE failures reproducible."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import sha, TLS_CERTIFICATE_REJECTED
from ota_diagnostic import serial_health
from summarize_public import inspect

RESULT = ROOT/'tests/results/esp32c3-tls-dynamic-20261001'
FIRMWARE = ROOT/'firmware/development/esp32c3-tls-dynamic'


def read(path):
    return json.loads(path.read_text())


class Evidence(unittest.TestCase):
    def test_artifact_and_only_intended_config_change(self):
        manifest = read(FIRMWARE/'manifest.json')
        for name, expected in manifest['files'].items():
            data = (FIRMWARE/name).read_bytes()
            self.assertEqual(len(data), expected['bytes'])
            self.assertEqual(sha(data), expected['sha256'])
        def config(path):
            return dict(line.split('=', 1) for line in path.read_text().splitlines()
                        if line.startswith('CONFIG_'))
        before = config(ROOT/'firmware/development/esp32c3-tcp-pcb-pool-fixed/sdkconfig')
        after = config(FIRMWARE/'sdkconfig')
        self.assertEqual({k: (before.get(k), after.get(k)) for k in before.keys()|after.keys()
                          if before.get(k) != after.get(k)},
                         {'CONFIG_MBEDTLS_DYNAMIC_BUFFER': (None, 'y')})
        for name, value in [('CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN', '16384'),
                            ('CONFIG_MBEDTLS_SSL_OUT_CONTENT_LEN', '4096'),
                            ('CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL', 'y')]:
            self.assertEqual(after[name], value)
        self.assertNotIn('CONFIG_MBEDTLS_DYNAMIC_FREE_CONFIG_DATA', after)

    def test_public_result_preserves_full_he_failure(self):
        report = read(RESULT/'https/report.json')
        self.assertEqual(report['image'], read(FIRMWARE/'manifest.json')['image'])
        summary = inspect(RESULT/'https')
        self.assertEqual(summary, read(RESULT/'https/summary.json'))
        self.assertEqual([c['playback_result'] for c in summary['cases']],
                         ['PASS', 'FAIL', 'FAIL', 'FAIL', 'PASS'])
        self.assertEqual(len(summary['allocation_failures']), 3)
        self.assertTrue(all('requested=55128 ' in r['line'] for r in summary['allocation_failures']))
        self.assertFalse(summary['panic_or_capture_errors'])
        self.assertEqual(len(summary['reset_banners']), 1)
        for case in report['cases']:
            if case['name'] in ('idle:recovery', 'restore'):
                self.assertEqual(case['result'], 'PASS')

    def test_switches_and_corrected_certificate_gate(self):
        cases = {c['name']: c for c in read(RESULT/'local/report.json')['cases']}
        self.assertEqual(cases['switching-and-heap']['evidence']['station_changes'], 21)
        self.assertEqual(cases['switching-and-heap']['result'], 'PASS')
        self.assertEqual(cases['websocket-format-and-reconnect']['result'], 'PASS')
        self.assertEqual(cases['untrusted-tls-rejected']['result'], 'FAIL')
        repeated = read(RESULT/'tls-rejection/report.json')
        self.assertTrue(all(c['result'] == 'PASS' for c in repeated['cases']))
        evidence = repeated['cases'][0]['evidence']
        self.assertTrue(evidence['certificate_bundle_rejected'])
        self.assertTrue(evidence['http_recovered'])
        self.assertIn('TLSV1_ALERT_ACCESS_DENIED', evidence['tls_alerts'])
        self.assertTrue(any(r['line'] == TLS_CERTIFICATE_REJECTED
                            for r in read(RESULT/'tls-rejection/performance.json')))

    def test_ota_and_return_to_baseline(self):
        cases = read(RESULT/'ota/report.json')['cases']
        self.assertEqual(len(cases), 15)
        self.assertTrue(all(c['result'] == 'PASS' for c in cases))
        self.assertEqual(serial_health(read(RESULT/'ota/performance.json')),
                         read(RESULT/'ota/serial-health.json'))
        self.assertEqual(read(RESULT/'ota/serial-health.json')['result'], 'PASS')
        for directory in ('install', 'restore'):
            report = read(RESULT/directory/'report.json')
            self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
            self.assertEqual(serial_health(read(RESULT/directory/'performance.json'))['result'], 'PASS')
        baseline = read(ROOT/'firmware/development/esp32c3-tcp-pcb-pool-fixed/manifest.json')
        self.assertEqual(read(RESULT/'final-board.json')['image']['app_elf_sha256'],
                         baseline['image']['app_elf_sha256'])


if __name__ == '__main__':
    unittest.main()
