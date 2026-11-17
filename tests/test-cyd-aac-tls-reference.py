"""Reject incomplete, rebound or incorrectly configured AAC reference records."""
import copy
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).parent / 'target/cyd_full_app_openeth_qemu/aac-reference.py'
spec = importlib.util.spec_from_file_location('aac_reference', path)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


class AacReferenceTests(unittest.TestCase):
    def setUp(self):
        self.expected = {}
        self.rows = []
        for profile, fixture in reference.fixtures():
            self.expected[profile] = dict(input_bytes=len(fixture['data']),
                                          input_sha256=reference.hashlib.sha256(fixture['data']).hexdigest(),
                                          adts_frames=fixture['adts_frames'], core_rate=fixture['core_rate'])
            for plus in (1, 0):
                rate = 48000 if plus else fixture['core_rate']
                frames = fixture['adts_frames'] * 1024 * (rate // fixture['core_rate'])
                self.rows.append(dict(profile=profile, plus=plus, input=len(fixture['data']),
                    input_sha256=self.expected[profile]['input_sha256'], rate=rate, channels=2, bits=16,
                    frames=frames, pcm_bytes=frames * 4, pcm_sha256=('a' if profile == 'lc' else 'b' if plus else 'c') * 64,
                    calls=fixture['adts_frames'] + 1, resizes=0, heap_before=200000, heap_after=200000,
                    stack_free=12000, core=1, priority=3, drained=1))

    def transcript(self, rows=None):
        rows = self.rows if rows is None else rows
        return '\n'.join(['AAC_TLS_REFERENCE ' + ' '.join(f'{key}={value}' for key, value in row.items()) for row in rows] +
                         ['AAC_TLS_REFERENCE_COMPLETE cases=4 handles_closed=4 heap_integrity=1'])

    def test_whole_lc_and_repeated_he_adts_accounting(self):
        fixtures = dict(reference.fixtures())
        self.assertEqual(len(fixtures['lc']['data']), 443706)
        self.assertEqual(len(fixtures['he']['data']), 102420)
        self.assertEqual(fixtures['he']['adts_frames'], 300)
        self.assertEqual(fixtures['he']['pcm_frames'], 614400)
        self.assertEqual(fixtures['he']['repetitions'], 20)
        self.assertEqual(reference.validate_log(self.transcript(), self.expected), self.rows)

    def test_census_order_and_native_faults(self):
        valid = self.transcript()
        for text in (self.transcript(self.rows[:-1]), self.transcript(self.rows[::-1]),
                     self.transcript(self.rows + self.rows[:1]), valid.replace('handles_closed=4', 'handles_closed=3'),
                     valid + '\nassert failed: reference', valid + '\nAAC_TLS_REFERENCE_EXTRA'):
            with self.subTest(text=text[:50]), self.assertRaises(ValueError):
                reference.validate_log(text, self.expected)

    def test_complete_pcm_geometry_and_input_binding(self):
        for key, value in dict(input=1, input_sha256='0' * 64, rate=24000, channels=1, bits=24,
                               frames=1, pcm_bytes=4, core=0, priority=6, drained=0, stack_free=0,
                               pcm_sha256='g' * 64, plus=0).items():
            rows = copy.deepcopy(self.rows)
            rows[2][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                reference.validate_log(self.transcript(rows), self.expected)

    def test_controls_must_distinguish_sbr_and_preserve_lc(self):
        for index, sha in ((1, 'b' * 64), (3, 'b' * 64)):
            rows = copy.deepcopy(self.rows)
            rows[index]['pcm_sha256'] = sha
            with self.subTest(index=index), self.assertRaises(ValueError):
                reference.validate_log(self.transcript(rows), self.expected)

    def test_duplicate_fields_and_repeated_heap_retention(self):
        rows = copy.deepcopy(self.rows)
        rows[2]['heap_after'] -= 4
        with self.assertRaises(ValueError):
            reference.validate_log(self.transcript(rows), self.expected)
        with self.assertRaises(ValueError):
            reference.validate_log(self.transcript().replace('profile=lc', 'profile=lc profile=lc', 1), self.expected)


if __name__ == '__main__':
    unittest.main()
