"""Replay physical RX ownership evidence and retain every failed gate."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-rx-ownership-20261005'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import Failure, check_cpu, check_recovery_heap
from rx_ownership import analyze
from summarize_rx_ownership import summarize

RUNS = ('vorbis-prefill-settle', 'vorbis-rx-settle', 'vorbis-rx-chunked',
        'mp3-rx-chunked', 'opus-rx-chunked')


def read(path): return json.loads(path.read_text())
def sha(data): return hashlib.sha256(data).hexdigest()


class RXEvidence(unittest.TestCase):
    def test_byte_manifest(self):
        manifest = read(DATA/'manifest.json')
        files = {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                 if p.is_file() and p.name != 'manifest.json'}
        self.assertEqual(files, set(manifest))
        for path, value in manifest.items():
            data = (DATA/path).read_bytes()
            self.assertEqual(len(data), value['bytes'], path)
            self.assertEqual(sha(data), value['sha256'], path)

    def test_unchanged_load_and_recovery_gates(self):
        for name in RUNS:
            folder = DATA/name
            report, rows = read(folder/'report.json'), read(folder/'performance.json')
            cases = {c['name']: c for c in report['cases']}
            self.assertEqual(cases['initial-load']['result'], 'FAIL', name)
            self.assertEqual(cases['initial-load']['reason'],
                             'Progressive heap loss during continuous playback', name)
            expected_failures = {'initial-load'}
            if name == 'opus-rx-chunked':
                expected_failures.add('settled-load')
                self.assertEqual(cases['settled-load']['reason'], 'WebUI response exceeded 2 s')
            self.assertEqual({c['name'] for c in report['cases'] if c['result'] != 'PASS'}, expected_failures)
            for window in report['windows']:
                start, end = window['start']+window['warmup'], window['end']
                selected = [r for r in rows if start <= r['at'] <= end]
                if window['name'] == 'initial-load':
                    with self.assertRaisesRegex(Failure, 'Progressive heap loss'):
                        check_cpu(selected, start=start, end=end)
                else:
                    values = check_cpu(selected, start=start, end=end)
                    if 'evidence' in cases['settled-load']:
                        for key, value in values.items():
                            self.assertAlmostEqual(value, cases['settled-load']['evidence'][key])
                    else:
                        status = next(b for b in read(folder/'status.json') if b['case'] == 'settled-load')
                        self.assertGreater(max(s['request_ms'] for s in status['samples']), 2000)
            check_recovery_heap(cases['idle-before']['evidence'], cases['idle-after']['evidence'])
            self.assertTrue(all(r['largest'] == 114688 for r in cases['idle-after']['evidence']))

    def test_ownership_captures_including_rejected_logs(self):
        for name in RUNS[1:]:
            self.assertEqual(summarize(DATA/name), read(DATA/name/'summary.json'), name)
        for name in ('vorbis-rx-settle', 'mp3-rx-chunked'):
            with self.assertRaises(ValueError): analyze(read(DATA/name/'performance.json'))
            self.assertFalse(read(DATA/name/'summary.json')['ownership']['complete'])
        result = read(DATA/'vorbis-rx-chunked/summary.json')
        self.assertTrue(result['ownership']['complete'])
        self.assertEqual(result['phases']['idle-after']['live_max'], 0)
        self.assertEqual(result['phases']['settled-load']['live_min'], 8)
        self.assertEqual(result['phases']['settled-load']['live_max'], 10)
        self.assertEqual(result['ownership']['maximum_allocated_payload_bytes'], 17644)
        # This is TLSF accounting inferred from pinned SDK sources, not a
        # hard-coded assumption that every RX allocation has the same size.
        self.assertEqual(result['phases']['settled-load']['inferred_heap_bytes_max'], 17724)
        opus = read(DATA/'opus-rx-chunked/summary.json')
        self.assertTrue(opus['ownership']['complete'])
        self.assertEqual(opus['phases']['idle-after']['live_max'], 0)
        self.assertEqual(opus['phase_metrics']['settled-load']['cpu_and_heap']['result'], 'PASS')
        self.assertGreater(opus['phase_metrics']['settled-load']['maximum_http_ms'], 2000)

    def test_build_and_source_identity(self):
        build = read(DATA/'verify/build.json')
        control = read(ROOT/'tests/results/esp32c3-output-dma-20261005/verify-prefill/build.json')
        self.assertEqual(build['types'], control['types'])
        self.assertEqual(build['features'], control['features'])
        self.assertEqual(build['sections']['.iram0.text'], control['sections']['.iram0.text'])
        self.assertEqual(build['sections']['.dram0.bss']-control['sections']['.dram0.bss'], 552)
        for path, digest in build['source_sha256'].items():
            self.assertEqual(sha((DATA/'verify/sources'/path).read_bytes()), digest)
        for caller, callee in build['rx_ownership_calls'].items():
            self.assertRegex((DATA/'verify'/(caller+'.asm')).read_text(),
                             r'\b(?:j|jal|jalr)\s+[^\n]*<'+re.escape(callee)+'>')
        host = read(DATA/'host/report.json')
        self.assertTrue(host['pass'])
        for path, digest in host['source_sha256'].items():
            base = 'verify/sources' if path.startswith('idf/') else 'sources'
            self.assertEqual(sha((DATA/base/path).read_bytes()), digest)
        artifact = ROOT/'firmware/development/esp32c3-rx-owner-diagnostic'
        app = (artifact/'app.bin').read_bytes()
        self.assertEqual(sha(app), build['app_sha256'])
        self.assertEqual(app[176:208].hex(), build['elf_sha256'])
        self.assertEqual(sha((artifact/'sdkconfig').read_bytes()), build['sdkconfig_sha256'])
        self.assertTrue(read(artifact/'manifest.json')['hardware_tested'])
        self.assertFalse(read(artifact/'manifest.json')['production_qualified'])

    def test_runtime_sources_and_ota_restore(self):
        for name in (*RUNS, 'ota-diagnostic', 'ota-restore'):
            report = read(DATA/name/'report.json')
            for path, digest in report['test_sources_sha256'].items():
                if Path(path).stem in ('common','run','diagnostic','pool_settle','memory',
                                      'ota','ota_transition','serial_lines','server','fixtures','generate_stress'):
                    source = DATA/'runner-sources'/digest/Path(path).name
                    self.assertEqual(sha(source.read_bytes()), digest)
        for name in ('ota-diagnostic', 'ota-restore'):
            cases = read(DATA/name/'report.json')['cases']
            self.assertTrue(all(c['result'] == 'PASS' for c in cases))
            self.assertTrue(cases[0]['evidence']['wifi_unchanged'])
            self.assertTrue(cases[0]['evidence']['playlist_unchanged'])
            self.assertTrue(cases[0]['evidence']['settings_unchanged'])
        board = read(DATA/'board-final.json')
        target = read(ROOT/'firmware/development/esp32c3-output-dma-prefill/manifest.json')
        self.assertEqual(board['info']['app_elf_sha256'], target['elf_sha256'])
        self.assertTrue(board['status']['audio'])


if __name__ == '__main__': unittest.main()
