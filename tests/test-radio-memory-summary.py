import json
import hashlib
from pathlib import Path
import sys
import unittest
from evidence_sources import historical_source
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from summarize_memory import summarize
EVIDENCE = ROOT/'tests/results/esp32c3-aac-radio-ram-20261001'


class MemorySummaryTests(unittest.TestCase):
    def inputs(self, name):
        return [json.loads((EVIDENCE/name/file).read_text()) for file in
                ('report.json', 'status.json', 'performance.json')]

    def test_retained_summaries(self):
        for name in ('profile', 'http-profile'):
            self.assertEqual(summarize(*self.inputs(name)),
                             json.loads((EVIDENCE/name/'summary.json').read_text()))

    def test_source_fingerprints(self):
        manifest=json.loads((EVIDENCE/'diagnostics-implementation.json').read_text())
        for path,digest in manifest['files'].items():
            snapshot=manifest.get('snapshots',{}).get(path)
            data=(EVIDENCE/snapshot).read_bytes() if snapshot else historical_source(ROOT,path,digest)
            self.assertEqual(hashlib.sha256(data).hexdigest(),digest,path)

    def test_fallback_and_no_pcm_stay_failed(self):
        result = summarize(*self.inputs('profile'))
        self.assertEqual([r['playback_result'] for r in result['cases'][:3]],
                         ['PASS', 'FAIL', 'FAIL'])
        self.assertEqual(result['no_pcm'], ['memory-playback:flac-48000-2ch-60s'])

    def test_missing_samples_or_checkpoints_rejected(self):
        report, status, rows = self.inputs('http-profile')
        for marker in ('PERF CPU:', 'Memory after first ', 'PERF STACK:'):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                summarize(report, status, [r for r in rows if marker not in r['line']])
        with self.assertRaises(ValueError):
            summarize(report, status, rows + [next(r for r in rows if 'Memory after first ' in r['line'])])


if __name__ == '__main__':
    unittest.main()
