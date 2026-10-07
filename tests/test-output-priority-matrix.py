"""Check scheduler comparison boundaries, missing telemetry and failed gates."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from compare_output_priority_matrix import compare, summarize


class MatrixComparison(unittest.TestCase):
    def setUp(self):
        (ROOT/'.build').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='priority-matrix-test-', dir=ROOT/'.build')
        self.assertEqual(Path(self.temp.name).resolve().parent, (ROOT/'.build').resolve())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.report = dict(board=dict(app_elf_sha256='image'), output_priority=6,
            fixture_hashes=dict(sample='hash'), load_seconds=40,
            cases=[dict(name='cpu-under-http-load:sample', result='FAIL', reason='Original failure')])
        self.status = [dict(case='load:sample', started_at=0, ended_at=21,
                            samples=[dict(rssi=-60, request_ms=12)])]

    def folder(self, name, rows, report=None):
        folder = self.root/name
        folder.mkdir()
        for file, data in [('report', report or self.report), ('performance', rows), ('status', self.status)]:
            (folder/(file+'.json')).write_text(json.dumps(data))
        return folder

    def test_complete_windows_and_failures(self):
        rows = [dict(at=at, line=f'I ({at*1000}) PERF CPU: busy=20% idle=80% decode=10% '
            'stream=0% output=0% wifi=0% tcpip=0% web=0%') for at in (10, 15, 20)]
        rows += [dict(at=11, line='PERF AAC: window 5000 ms, audio 9999 ms, decode 9999 ms'),
                 dict(at=15, line='PERF AAC: window 5000 ms, audio 4000 ms, decode 2000 ms'),
                 dict(at=20, line='PERF AAC: window 5000 ms, audio 6000 ms, decode 3000 ms'),
                 dict(at=25, line='PERF AAC: window 5000 ms, audio 9999 ms, decode 9999 ms')]
        result = summarize(self.folder('complete', rows))['cases'][0]
        self.assertEqual(result['original']['result'], 'FAIL')
        self.assertEqual(result['original']['reason'], 'Original failure')
        self.assertEqual(len(result['decoder_windows']), 2)
        self.assertEqual(result['audio_wall_ratio'], 1)
        self.assertEqual(result['elapsed_decode_ms_per_audio_second'], 500)
        self.assertEqual(result['estimated_decoder_cpu_ms_per_audio_second'], 100)
        self.assertEqual(result['cpu']['observed_seconds'], 10)

    def test_missing_logs_remain_unknown(self):
        result = summarize(self.folder('missing', []))['cases'][0]
        self.assertIsNone(result['audio_wall_ratio'])
        self.assertIsNone(result['estimated_decoder_cpu_ms_per_audio_second'])
        self.assertNotIn('busy_mean_percent', result['cpu'])
        self.assertEqual(result['original']['result'], 'FAIL')

    def test_reject_unmatched_files_and_durations(self):
        control = self.folder('control', [])
        for key, value in [('fixture_hashes', dict(sample='different')), ('load_seconds', 60)]:
            report = copy.deepcopy(self.report)
            report[key] = value
            with self.assertRaisesRegex(ValueError, 'Different fixture hashes or load duration'):
                compare(control, self.folder(key, [], report))


if __name__ == '__main__':
    unittest.main()
