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

    def framed_rows(self):
        rows = []
        for original in (self.rows[0], self.rows[2]):
            for capacity in (12288, 1024):
                row = copy.deepcopy(original)
                row.update(drained=0, initial_capacity=capacity, resizes=int(capacity == 1024),
                           empty_retries=int(capacity == 1024),
                           encoded_frames=self.expected[row['profile']]['adts_frames'], last_frame_eos=1)
                rows.append(row)
        return rows

    def framed_transcript(self, rows):
        return self.transcript() + '\n' + '\n'.join(
            ['AAC_TLS_FRAME_REFERENCE ' + ' '.join(f'{key}={value}' for key, value in row.items()) for row in rows] +
            ['AAC_TLS_FRAME_REFERENCE_COMPLETE cases=4 handles_closed=4 heap_integrity=1'])

    def test_frame_input_matches_complete_pcm_at_both_buffer_sizes(self):
        rows = self.framed_rows()
        text = self.framed_transcript(rows)
        self.assertEqual(reference.validate_log(text, self.expected), self.rows)
        self.assertEqual(reference.validate_frame_log(text, self.expected, self.rows), rows)

    def test_frame_input_requires_all_bytes_frames_resize_and_final_eos(self):
        for key, value in dict(pcm_sha256='0' * 64, input=1, frames=1, pcm_bytes=4, initial_capacity=8192,
                               resizes=0, empty_retries=2, encoded_frames=1, last_frame_eos=0, drained=1,
                               heap_after=1, core=0).items():
            rows = self.framed_rows()
            rows[1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                reference.validate_frame_log(self.framed_transcript(rows), self.expected, self.rows)
        rows = self.framed_rows()
        for changed in (rows[:-1], rows[::-1], rows + rows[:1]):
            with self.assertRaises(ValueError):
                reference.validate_frame_log(self.framed_transcript(changed), self.expected, self.rows)

    def test_ordinary_parser_small_buffer_retains_complete_identity(self):
        rows = [copy.deepcopy(self.rows[index]) for index in (0, 2)]
        for row in rows:
            row.update(initial_capacity=1024, resizes=1)
        def transcript(changed):
            return self.transcript() + '\n' + '\n'.join(
                ['AAC_TLS_BUFFER_REFERENCE ' + ' '.join(f'{key}={value}' for key, value in row.items()) for row in changed] +
                ['AAC_TLS_BUFFER_REFERENCE_COMPLETE cases=2 handles_closed=2 heap_integrity=1'])
        self.assertEqual(reference.validate_buffer_log(transcript(rows), self.expected, self.rows), rows)
        for key, value in dict(pcm_sha256='0' * 64, frames=1, input=1, initial_capacity=8192,
                               resizes=0, drained=0, heap_after=1).items():
            changed = copy.deepcopy(rows)
            changed[1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                reference.validate_buffer_log(transcript(changed), self.expected, self.rows)

    def fragmented_rows(self):
        rows = []
        for original in (self.rows[0], self.rows[2]):
            for framed in (0, 1):
                row = copy.deepcopy(original)
                row.update(initial_capacity=8192, framed=framed, chunk=257,
                           drained=1 - framed, last_frame_eos=framed,
                           encoded_frames=self.expected[row['profile']]['adts_frames'] if framed else 0)
                rows.append(row)
        return rows

    def fragmented_transcript(self, rows):
        return self.transcript() + '\n' + '\n'.join(
            ['AAC_TLS_FRAGMENT_REFERENCE ' + ' '.join(f'{key}={value}' for key, value in row.items()) for row in rows] +
            ['AAC_TLS_FRAGMENT_REFERENCE_COMPLETE cases=4 handles_closed=4 heap_integrity=1'])

    def test_fragmented_parser_and_frames_require_the_complete_pcm(self):
        rows = self.fragmented_rows()
        text = self.fragmented_transcript(rows)
        self.assertEqual(reference.validate_log(text, self.expected), self.rows)
        self.assertEqual(reference.validate_fragment_log(text, self.expected, self.rows), rows)
        for index in range(4):
            for key, value in dict(pcm_sha256='0' * 64, input=1, input_sha256='0' * 64,
                                   frames=1, pcm_bytes=4, channels=1, rate=24000, plus=0,
                                   initial_capacity=12288, chunk=256, resizes=1,
                                   framed=1 - rows[index]['framed'],
                                   drained=1 - rows[index]['drained'],
                                   last_frame_eos=1 - rows[index]['last_frame_eos'],
                                   encoded_frames=1, heap_after=1, stack_free=0,
                                   calls=0, core=0, priority=6).items():
                changed = copy.deepcopy(rows)
                changed[index][key] = value
                with self.subTest(index=index, key=key), self.assertRaises(ValueError):
                    reference.validate_fragment_log(self.fragmented_transcript(changed), self.expected, self.rows)

    def test_fragmented_reference_rejects_missing_reordered_or_malformed_records(self):
        rows = self.fragmented_rows()
        for changed in (rows[:-1], rows[::-1], rows + rows[:1]):
            with self.assertRaises(ValueError):
                reference.validate_fragment_log(self.fragmented_transcript(changed), self.expected, self.rows)
        text = self.fragmented_transcript(rows)
        for changed in (text.replace('handles_closed=4', 'handles_closed=3'),
                        text.replace('chunk=257', 'chunk=257 chunk=257', 1),
                        text.replace('chunk=257', 'chunk=-257', 1),
                        text.replace('chunk=257', 'chunk', 1),
                        text + '\nAAC_TLS_FRAGMENT_REFERENCE_EXTRA'):
            with self.subTest(text=changed[-80:]), self.assertRaises(ValueError):
                reference.validate_fragment_log(changed, self.expected, self.rows)

    def test_memory_observations_are_bound_to_case_order_and_capacity(self):
        cases = self.fragmented_rows()
        expectations = [(case, case['framed'], 8192, 257) for case in cases]
        rows = [dict(profile=case['profile'], plus=1, framed=case['framed'], initial_capacity=8192,
                     final_capacity=8192, live_free=100000, chunk=257, min_live_free=90000) for case in cases]
        def transcript(changed):
            return '\n'.join('AAC_TLS_MEMORY ' + ' '.join(f'{key}={value}' for key, value in row.items()) for row in changed)
        self.assertEqual(reference.validate_memory_log(transcript(rows), expectations, True), rows)
        for key, value in dict(profile='lc', plus=0, framed=1, initial_capacity=12288, final_capacity=4096,
                               chunk=256, live_free=0, min_live_free=0).items():
            changed = copy.deepcopy(rows)
            changed[2][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                reference.validate_memory_log(transcript(changed), expectations, True)
        for changed in (rows[:-1], rows[::-1], rows + rows[:1]):
            with self.assertRaises(ValueError):
                reference.validate_memory_log(transcript(changed), expectations, True)
        text = transcript(rows)
        for changed in (text.replace('live_free=100000', 'live_free=100000 live_free=100000', 1),
                        text.replace('min_live_free=90000', 'min_live_free=-1', 1),
                        text.replace(' min_live_free=90000', '', 1),
                        text + '\nAAC_TLS_MEMORY_EXTRA'):
            with self.assertRaises(ValueError):
                reference.validate_memory_log(changed, expectations, True)

    def test_historical_memory_records_remain_readable_without_sampled_minimum(self):
        text = 'AAC_TLS_MEMORY profile=lc plus=1 framed=0 initial_capacity=12288 final_capacity=12288 live_free=100000'
        expectations = [(self.rows[0], 0, 12288, 0)]
        rows = reference.validate_memory_log(text, expectations)
        self.assertIsNone(rows[0]['min_live_free'])
        with self.assertRaises(ValueError):
            reference.validate_memory_log(text, expectations, True)


if __name__ == '__main__':
    unittest.main()
