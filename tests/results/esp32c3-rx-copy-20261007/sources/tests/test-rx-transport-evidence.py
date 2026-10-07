"""Replay the RX telemetry and native packet-copy experiments separately."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from summarize_stream_memory import summarize

DATASETS = {
    'compact': ('esp32c3-rx-compact-20261007', 'esp32c3-rx-owner-crc'),
    'copy': ('esp32c3-rx-copy-20261007', 'esp32c3-rx-copy'),
}


def folder(kind):
    return ROOT/'tests/results'/DATASETS[kind][0]


def read(kind, name):
    return json.loads((folder(kind)/name).read_text(encoding='utf-8'))


class RxTransportEvidence(unittest.TestCase):
    def test_manifests(self):
        for kind in DATASETS:
            path = folder(kind)
            manifest = read(kind, 'manifest.json')
            self.assertEqual(set(manifest), {p.relative_to(path).as_posix()
                for p in path.rglob('*') if p.is_file() and p != path/'manifest.json'})
            for name, expected in manifest.items():
                data = (path/name).read_bytes()
                self.assertEqual(dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()), expected)

    def test_replay_keeps_full_windows_and_original_failures(self):
        for kind in DATASETS:
            actual = summarize(folder(kind)/'board')
            self.assertEqual(actual, read(kind, 'summary.json'))
            self.assertEqual(actual['requested_seconds'], 600)
            self.assertGreaterEqual(actual['observed_seconds'], 600)
            self.assertIsNone(actual['cpu_budget_percent'])
            self.assertEqual(actual['acceptance'], read(kind, 'board/report.json')['cases'])
            self.assertFalse(actual['acoustic_continuity_qualified'])

    def test_compact_capture_loss_is_retained_as_failure(self):
        summary = read('compact', 'summary.json')
        self.assertEqual(summary['ownership'],
                         dict(complete=False, reason='Missing/duplicate live RX owners'))
        self.assertEqual(summary['acceptance'][1]['result'], 'FAIL')
        self.assertEqual(summary['acceptance'][1]['reason'], 'Incomplete CPU/heap evidence')
        records = read('compact', 'board/performance.json')
        self.assertTrue(any('PERF RX_OWNER2:' in r['line'] for r in records))
        self.assertFalse(any('PERF RX_OWNER:' in r['line'] for r in records))

    def test_copy_does_not_claim_its_untraced_buffers_disappeared(self):
        report = read('copy', 'board/report.json')
        self.assertFalse(report['rx_diagnostics'])
        self.assertEqual(read('copy', 'summary.json')['ownership'],
                         dict(complete=False, reason='Missing RX ownership telemetry'))
        assembly = (folder('copy')/'verify/wlanif_input.txt').read_text()
        self.assertIn('<pbuf_alloc>', assembly)
        self.assertIn('<esp_netif_free_rx_buffer>', assembly)
        self.assertNotIn('<esp_pbuf_allocate>', assembly)

    def test_exact_image_and_configuration(self):
        baseline = ROOT/'firmware/development/esp32c3-output-first/sdkconfig'
        base = set(baseline.read_text().splitlines())
        for kind, (_, variant) in DATASETS.items():
            image = ROOT/'firmware/development'/variant/'app.bin'
            build = read(kind, 'firmware/manifest.json')
            self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), build['app_sha256'])
            self.assertEqual(image.read_bytes()[176:208].hex(), read(kind, 'summary.json')['image'])
            config = set((folder(kind)/'firmware/sdkconfig').read_text().splitlines())
            keys = ['YORADIO_RX_BUFFER_DIAGNOSTICS'] if kind == 'compact' else ['LWIP_L2_TO_L3_COPY', 'L2_TO_L3_COPY']
            self.assertEqual(config-base, {'CONFIG_'+key+'=y' for key in keys})
            self.assertEqual(base-config, {'# CONFIG_'+key+' is not set' for key in keys})
            self.assertFalse(build['production_qualified'])

    def test_ota_restoration_and_playback(self):
        original = ROOT/'firmware/development/esp32c3-output-first/app.bin'
        for kind in DATASETS:
            for phase in ('ota', 'restore'):
                cases = read(kind, phase+'/report.json')['cases']
                self.assertTrue(cases)
                self.assertTrue(all(c['result'] == 'PASS' for c in cases))
            final = read(kind, 'board-final.json')
            self.assertEqual(final['info']['app_elf_sha256'], original.read_bytes()[176:208].hex())
            self.assertTrue(final['status']['audio'])


if __name__ == '__main__':
    unittest.main()
