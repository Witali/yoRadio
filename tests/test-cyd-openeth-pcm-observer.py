"""Exercise the EOF and progress predicates against diagnostic DAC output."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


runner = Path(__file__).with_name('run-cyd-full-app-openeth.py')
spec = importlib.util.spec_from_file_location('cyd_openeth', runner)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class PcmObserverTests(unittest.TestCase):
    def test_dac_progress_excludes_driver_bytes(self):
        health = {'output_driver': {'written_bytes': 1024}}
        self.assertEqual(probe.output_progress(health, '', 'dac'), 0)
        self.assertEqual(probe.output_progress(health, '', 'pdm'), 1024)
        self.assertEqual(probe.output_progress(health, 'bad CYD_OPENETH_PCM_PROGRESS frames=960\n', 'dac'), 0)
        log = 'CYD_OPENETH_PCM_PROGRESS frames=648\r\nCYD_OPENETH_PCM_PROGRESS frames=5448\r\n'
        self.assertEqual(probe.output_progress(health, log, 'legacy_dac'), 5448)

    def observe_eof(self, uart, *, allocations=0):
        report = {'audio_backend': 'dac', 'observed': []}
        health = dict(output_driver=dict(requested_bytes=528000, written_bytes=528000, errors=0,
                                         timeouts=0, short_writes=0, saturated=False),
                      decoder_failure={'sequence': 0}, stream_failure={'sequence': 0},
                      output={'failures': 0}, allocation_failures=allocations)
        status = json.dumps(dict(generation=1, audio=False, connecting=False, format='stream ended'))
        server = SimpleNamespace(fixtures={'station': {'data': b'123'}})
        guest = SimpleNamespace(poll=lambda: None)
        with patch.object(probe, 'request', return_value=status), patch.object(probe, 'sample', return_value=health), \
             patch.object(probe, 'guest_log', return_value=uart), patch.object(probe, 'check_asset', return_value={'bytes': 13588}):
            if allocations:
                with self.assertRaisesRegex(RuntimeError, 'Unexpected allocation failure'):
                    probe.observe_eof(0, server, dict(complete=True, sent=3), guest, runner, 1, report)
            else:
                probe.observe_eof(0, server, dict(complete=True, sent=3), guest, runner, 1, report)
        self.assertEqual(report['web_asset_after_eof']['bytes'], 13588)

    def test_exact_ordered_flush(self):
        self.observe_eof('CYD_OPENETH_PCM_FLUSH frames=528000 status=0\n')

    def test_memory_failure_preserves_post_eof_webui_evidence(self):
        self.observe_eof('CYD_OPENETH_PCM_FLUSH frames=528000 status=0\n', allocations=1)

    def test_truncated_failed_or_duplicate_flush_rejected(self):
        good = 'CYD_OPENETH_PCM_FLUSH frames=528000 status=0\n'
        for uart in ('', 'CYD_OPENETH_PCM_FLUSH frames=40008 status=0\n',
                     'CYD_OPENETH_PCM_FLUSH frames=528000 status=-1\n', good + good):
            with self.subTest(uart=uart), self.assertRaisesRegex(RuntimeError, 'Unexpected decoded PCM frame count'):
                self.observe_eof(uart)


if __name__ == '__main__':
    unittest.main()
