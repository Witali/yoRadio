"""Validate fault fixture construction, retained real-library results and strict parsing."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from generate_aac_faults import generate
from run_aac_faults import parse_log

FIXTURES = ROOT/'tests/fixtures/aac_faults'
DATA = ROOT/'tests/results/esp32c3-aac-faults-20261004'


class FaultTests(unittest.TestCase):
    def test_reproducible_fixtures(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            generate(output)
            for path in output.iterdir():
                self.assertEqual(path.read_bytes(), (FIXTURES/path.name).read_bytes(), path.name)

    def test_frame_lengths_hashes_and_overruns(self):
        manifest = json.loads((FIXTURES/'manifest.json').read_text())
        trace = (ROOT/'tests/fixtures/aac_sbr_gap/hev2-44100-stereo.trace').read_text()
        spans = [list(map(int, line.split()[2:])) for line in trace.splitlines()
                 if line.startswith('FIL 0 ')]
        for name, meta in manifest['cases'].items():
            frame = (FIXTURES/(name+'.aac')).read_bytes()
            self.assertEqual(len(frame), meta['bytes'])
            self.assertEqual(hashlib.sha256(frame).hexdigest(), meta['sha256'])
            self.assertEqual(((frame[3] & 3) << 11) | (frame[4] << 3) | (frame[5] >> 5), len(frame))
            bits = ''.join(f'{b:08b}' for b in frame)
            if name == 'header-only':
                self.assertEqual(len(frame), 7)
            elif name == 'sbr-truncated':
                self.assertEqual(int(bits[spans[0][1]:spans[0][1]+4], 2), 13)
                self.assertGreater(spans[0][2], len(bits))
            else:
                begin = spans[0 if name == 'sbr-count-overrun' else 1][0]
                self.assertEqual(int(bits[begin:begin+3], 2), 6)  # ID_FIL
                self.assertEqual(bits[begin+3:begin+15], '1'*12)
                declared_bytes = 15 + 255 - 1
                self.assertGreater(declared_bytes*8, len(bits)-(begin+15))

    def test_retained_results_and_no_partial_pcm(self):
        result = parse_log((DATA/'diagnostics.log').read_text())
        stored = json.loads((DATA/'result.json').read_text())
        for key, value in result.items():
            self.assertEqual(value, stored[key], key)
        self.assertEqual([r['public_error'] for r in result['outcomes']], [-2]*4+[0]*4)
        self.assertTrue(all(r['pcm_bytes'] == 0 for r in result['outcomes']))
        self.assertEqual(result['recovery_frames'], 120)
        self.assertFalse(result['hardware_tested'])

    def test_incomplete_duplicate_and_wrong_outcomes_are_rejected(self):
        log = (DATA/'diagnostics.log').read_text()
        for changed in (
            log.replace('AAC_LATE_OOM_PASS parity=0 allocation=owner', 'missing'),
            log.replace('AAC_MALFORMED_PASS case=sbr_truncated', 'missing'),
            log.replace('AAC_FAULT_OUTCOME public_error=-2', 'AAC_FAULT_OUTCOME public_error=0', 1),
            log.replace('AAC_FAULT_OUTCOME public_error=0 pcm_bytes=0',
                        'AAC_FAULT_OUTCOME public_error=0 pcm_bytes=2048', 1),
            log+'\nAAC_MALFORMED_PASS case=header_only recovery_frames=15\n',
            log.replace('recoveries=8 heap=valid', 'recoveries=7 heap=valid'),
            log+'\nCORRUPT HEAP\n',
            log+'\nassert failed: decode\n',
        ):
            with self.assertRaises(ValueError):
                parse_log(changed)

    def test_subsequent_pcm_matches_baseline_exactly(self):
        rows = json.loads((DATA/'pcm-comparison.json').read_text())
        self.assertEqual({r['case'] for r in rows}, {'gaps', 'late'})
        self.assertEqual(sum(r['channel_samples'] for r in rows), 865280)
        for row in rows:
            pcm = gzip.decompress((DATA/(row['case']+'.pcm.gz')).read_bytes())
            self.assertEqual(pcm, gzip.decompress((ROOT/row['baseline']).read_bytes()))
            self.assertEqual(hashlib.sha256(pcm).hexdigest(), row['pcm_sha256'])
            self.assertEqual(row['different'], 0)
            self.assertEqual(row['max_error_lsb'], 0)

    def test_evidence_hashes(self):
        manifest = json.loads((DATA/'manifest.json').read_text())
        for name, digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((DATA/name).read_bytes()).hexdigest(), digest, name)


if __name__ == '__main__':
    unittest.main()
