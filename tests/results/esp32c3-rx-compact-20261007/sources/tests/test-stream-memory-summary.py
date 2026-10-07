"""Reject incomplete studies and damaged ownership evidence; keep original FAILs."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from summarize_stream_memory import summarize


class StreamSummary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='memory-summary-', dir=ROOT/'.build')
        self.folder = Path(self.temp.name)
        self.assertEqual(self.folder.resolve().parent, (ROOT/'.build').resolve())
        self.addCleanup(self.temp.cleanup)
        idle = dict(result='PASS', evidence=dict(samples=[dict(heap=100000, largest=80000, tasks=17)]*2))
        cases = [dict(idle, name='idle-before'),
                 dict(name='cpu-under-http-load:test', result='FAIL', reason='Retain original failure'),
                 dict(idle, name='idle-after')]
        cases += [dict(name=n, result='PASS') for n in ('stop-recovery', 'runtime', 'restore-board')]
        report = dict(board=dict(app_elf_sha256='test-image'), fixture_hashes={'test': 'test-hash'},
                      load_seconds=60, cpu_budget_percent=None, cases=cases)
        batches = [dict(case='settled-idle', started_at=0, ended_at=12, samples=[]),
                   dict(case='load:test', started_at=13, ended_at=73,
                        samples=[dict(seconds=s, request_ms=100, rssi=-60) for s in range(60)]),
                   dict(case='settled-idle', started_at=75, ended_at=87, samples=[])]
        rows = []
        for seq, at in enumerate(range(2, 88, 5), 1):
            live = int(13 <= at < 73)
            allocs, frees = (1, 0) if live else (int(at >= 73), int(at >= 73))
            rows.append(dict(at=at, line=f'PERF RX_OWNER: seq={seq} live={live} peak={allocs} '
                f'allocs={allocs} frees={frees} lost=0 unmatched=0 payload={1728*live} '
                f'metadata={28*live} missing=0 walk_us=150'))
            if live:
                rows.append(dict(at=at, line=f'PERF RX_BLOCK: seq={seq} id=1 payload=0x1000 '
                    'payload_bytes=1728 metadata=0x2000 metadata_bytes=28'))
            rows += [dict(at=at, line='PERF CPU: busy=96.0% idle=4.0% heap=22000 largest=10000 tasks=17'),
                     dict(at=at, line='PERF AAC: window 5000 ms, audio 5000 ms, decode 4000 ms'),
                     dict(at=at+5, line=f'PERF NET_HEAP: seq={seq} age_ms=5000 heap=22000 '
                          'largest=10000 used=250000 blocks=400 free_blocks=20 active=2 tw=3 bound=0 '
                          'listen=1 tx_segments=0 tx_bytes=0 rx_segments=0 rx_bytes=0 missed=0 walk_us=100'),
                     dict(at=at+5, line=f'PERF NET_RX: seq={seq} age_ms=5000 window=22040 maximum=23040 refused=0')]
        self.data = dict(zip(('report.json', 'status.json', 'performance.json', 'checkpoint.json'),
                            (report, batches, sorted(rows, key=lambda r:r['at']),
                             dict(finished=True, complete=True, all_cases_pass=False))))

    def run_summary(self):
        for name, value in self.data.items():
            (self.folder/name).write_text(json.dumps(value), encoding='utf-8')
        return summarize(self.folder)

    def test_measured_ranges_headers_aged_credit_and_original_failure(self):
        result = self.run_summary()
        self.assertEqual(result['acceptance'][1]['result'], 'FAIL')
        self.assertEqual(result['playback']['cases'][0]['full_window']['strict']['result'], 'PASS')
        self.assertFalse(result['acoustic_continuity_qualified'])
        self.assertTrue(result['ownership']['load_coverage_complete'])
        self.assertEqual(result['owner_phases']['load']['ranges']['inferred_heap_bytes']['median'], 1764)
        self.assertEqual(result['owner_phases']['load']['ranges']['allocated_payload_bytes']['median'], 1756)
        self.assertEqual(result['owner_phases']['idle-after']['ranges']['live']['max'], 0)
        net = result['network']['windows']['load']
        self.assertTrue(net['coverage_complete'])
        self.assertEqual(net['samples'], 10)  # sample_at is UART time minus 5 s
        self.assertEqual(net['receive_credit']['uncredited']['median'], 1000)

    def test_incomplete_and_shorter_runs_rejected(self):
        original = copy.deepcopy(self.data)
        for key, change in (
            ('checkpoint.json', lambda v:v.update(complete=False)),
            ('report.json', lambda v:v.update(load_seconds=61)),
            ('report.json', lambda v:v['cases'].pop()),
            ('status.json', lambda v:v[1].update(in_progress=True)),
            ('status.json', lambda v:v[1].update(interrupted='TimeoutError'))):
            self.data = copy.deepcopy(original)
            change(self.data[key])
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.run_summary()

    def test_missing_owner_row_rejected_without_repair(self):
        records = self.data['performance.json']
        records.pop(next(i for i, r in enumerate(records) if 'RX_BLOCK:' in r['line']))
        result = self.run_summary()
        self.assertFalse(result['ownership']['complete'])
        self.assertEqual(result['ownership']['reason'], 'Missing/duplicate live RX owners')
        self.assertEqual(result['acceptance'][1]['result'], 'FAIL')

    def test_long_telemetry_gap_does_not_pass_coverage(self):
        for r in self.data['performance.json']:
            if 'RX_OWNER:' in r['line'] or 'RX_BLOCK:' in r['line']:
                r['at'] = 30 + r['at']*.01
        result = self.run_summary()
        self.assertTrue(result['ownership']['complete'])  # internally intact snapshot rows
        self.assertFalse(result['ownership']['load_coverage_complete'])

    def test_missing_credit_row_does_not_pass_network_coverage(self):
        records = self.data['performance.json']
        records.pop(next(i for i, r in enumerate(records) if 'NET_RX:' in r['line'] and r['at'] > 30))
        result = self.run_summary()
        self.assertFalse(result['network']['windows']['load']['coverage_complete'])


if __name__ == '__main__':
    unittest.main()
