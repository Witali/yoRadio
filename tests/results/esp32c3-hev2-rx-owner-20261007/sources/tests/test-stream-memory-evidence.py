"""Replay the retained ten-minute C3 HE-AACv2 RX-owner investigation."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-hev2-rx-owner-20261007'
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from summarize_stream_memory import summarize
from rx_ownership import analyze


def read(name):
    return json.loads((DATA/name).read_text(encoding='utf-8'))


class MemoryEvidence(unittest.TestCase):
    def test_manifest_and_sources(self):
        manifest = read('manifest.json')
        self.assertEqual(set(manifest), {p.relative_to(DATA).as_posix()
            for p in DATA.rglob('*') if p.is_file() and p != DATA/'manifest.json'})
        for name, expected in manifest.items():
            data = (DATA/name).read_bytes()
            self.assertEqual(dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()), expected, name)

    def test_summary_replay_preserves_the_original_outcomes(self):
        actual = summarize(DATA/'board-10min')
        self.assertEqual(actual, read('summary.json'))
        self.assertEqual(actual['requested_seconds'], 600)
        self.assertGreaterEqual(actual['observed_seconds'], 600)
        self.assertIsNone(actual['cpu_budget_percent'])
        self.assertEqual(actual['acceptance'], read('board-10min/report.json')['cases'])
        self.assertFalse(actual['acoustic_continuity_qualified'])
        self.assertEqual(actual['ownership'], dict(complete=False, reason='Merged/truncated telemetry line'))
        self.assertEqual(actual['acceptance'][1]['reason'], 'Progressive heap loss during continuous playback')

    def test_independent_post_stop_snapshots_do_not_repair_full_capture(self):
        batches = read('board-10min/status.json')
        end = next(b['ended_at'] for b in batches if b['case'].startswith('load:'))
        result = analyze([r for r in read('board-10min/performance.json') if r['at'] >= end])
        self.assertEqual(result, read('board-10min/post-stop-rx.json')['ownership'])
        self.assertEqual([s['seq'] for s in result['snapshots']], [180, 181])
        self.assertEqual(result['maximum_live'], 0)
        self.assertTrue(all(s['allocs'] == s['frees'] for s in result['snapshots']))

    def test_interrupted_preliminary_run_is_not_completed_evidence(self):
        self.assertFalse(read('board/termination.json')['complete'])
        self.assertFalse(read('board/checkpoint.json')['complete'])
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            summarize(DATA/'board')

    def test_diagnostic_image_and_single_configuration_change(self):
        artifact = ROOT/'firmware/development/esp32c3-output-first-rx-owner'
        build = read('firmware/manifest.json')
        self.assertEqual(hashlib.sha256((artifact/'app.bin').read_bytes()).hexdigest(), build['app_sha256'])
        self.assertEqual((artifact/'app.bin').read_bytes()[176:208].hex(), read('summary.json')['image'])
        diagnostic = set((DATA/'firmware/sdkconfig').read_text().splitlines())
        ordinary = set((ROOT/'firmware/development/esp32c3-output-first/sdkconfig').read_text().splitlines())
        self.assertEqual(diagnostic-ordinary, {'CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS=y'})
        self.assertEqual(ordinary-diagnostic, {'# CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS is not set'})
        self.assertFalse(build['production_qualified'])

    def test_ota_and_final_image(self):
        for phase in ('ota', 'restore'):
            cases = read(phase+'/report.json')['cases']
            self.assertTrue(cases)
            self.assertTrue(all(c['result'] == 'PASS' for c in cases), phase)
        original = ROOT/'firmware/development/esp32c3-output-first/app.bin'
        final = read('board-final.json')
        self.assertEqual(final['info']['app_elf_sha256'], original.read_bytes()[176:208].hex())
        self.assertTrue(final['status']['audio'])


if __name__ == '__main__':
    unittest.main()
