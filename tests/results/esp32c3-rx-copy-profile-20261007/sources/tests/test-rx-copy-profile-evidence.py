"""Replay retained physical RX-copy measurements and their build/host evidence."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-rx-copy-profile-20261007'
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from save_rx_copy_profile_evidence import profile_summary
from summarize_stream_memory import summarize
from ota_diagnostic import serial_health
from rx_copy_profile import analyze


def read(name):
    return json.loads((DATA/name).read_bytes())


class ProfileEvidence(unittest.TestCase):
    def test_exact_archive_and_sources(self):
        manifest = read('manifest.json')
        self.assertEqual(set(manifest), {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                        if p.is_file() and p != DATA/'manifest.json'})
        for name, record in manifest.items():
            data = (DATA/name).read_bytes()
            self.assertEqual(record, dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
        for phase in ('ota', 'study', 'restore'):
            for name, digest in read(phase+'/report.json')['test_sources_sha256'].items():
                self.assertEqual(hashlib.sha256((DATA/'sources'/name).read_bytes()).hexdigest(), digest)
        for name, digest in read('firmware/manifest.json')['source_sha256'].items():
            self.assertEqual(hashlib.sha256((DATA/'sources'/name).read_bytes()).hexdigest(), digest)

    def test_full_replay_preserves_acceptance(self):
        result = dict(profile=profile_summary(DATA/'study'),
                      playback=summarize(DATA/'study', independent_network=True))
        self.assertEqual(result, read('summary.json'))
        self.assertEqual(result['playback']['acceptance'], read('study/report.json')['cases'])
        self.assertGreaterEqual(result['playback']['observed_seconds'], 600)
        self.assertTrue(result['profile']['sizing_valid'])
        self.assertTrue(all(w['coverage_complete'] for w in result['profile']['windows']))
        self.assertFalse(read('provenance.json')['production_qualified'])
        self.assertFalse(read('provenance.json')['acoustic_continuity_qualified'])

    def test_host_build_and_final_free_path(self):
        host = read('host/report.json')
        self.assertTrue(host['passed'])
        for name, digest in host['sources'].items():
            self.assertEqual(hashlib.sha256((DATA/'host/sources'/name).read_bytes()).hexdigest(), digest)
        rows = [dict(at=i*5, line=line) for i, line in enumerate((DATA/'host/run.log').read_text().splitlines())
                if line.startswith('PERF RX_COPY:')]
        self.assertTrue(analyze(rows)['sizing_valid'])
        build = read('firmware/manifest.json')
        self.assertEqual(build['rx_copy_callbacks'], dict(sta='__wrap_wlanif_input', ap='__wrap_wlanif_input'))
        self.assertEqual(build['rx_copy_tracking_bytes'], dict(s_owners=768, s_counts=112))
        self.assertIn('<__wrap_mem_free>', (DATA/'verify/pbuf_free.asm').read_text())
        self.assertIn('<mem_free>', (DATA/'verify/__wrap_mem_free.asm').read_text())

    def test_ota_and_restore(self):
        for phase in ('ota', 'restore'):
            report = read(phase+'/report.json')
            self.assertTrue(report['cases'])
            self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
            self.assertEqual(serial_health(read(phase+'/performance.json')), read(phase+'/serial-health.json'))
        self.assertEqual(read('ota/serial-health.json')['result'], 'PASS')
        # The restore capture ended on an incomplete line; preserve this FAIL
        # even though HTTP identity/settings checks and resumed playback pass.
        self.assertEqual(read('restore/serial-health.json')['result'], 'FAIL')
        self.assertTrue(any('incomplete final line' in f['line']
                            for f in read('restore/serial-health.json')['evidence']['faults']))
        final = read('board-final.json')
        self.assertTrue(final['status']['audio'])
        self.assertEqual(final['stationtimeout'], 10)
        original = json.loads((ROOT/'firmware/development/esp32c3-station-timeout/manifest.json').read_bytes())
        self.assertEqual(final['info']['app_elf_sha256'], original['elf_sha256'])


if __name__ == '__main__':
    unittest.main()
