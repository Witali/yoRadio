"""Known-answer mono measurements and policy guards; no references or target execution."""
import copy
import hashlib
import math
from pathlib import Path
import struct
import unittest

import mono_metrics as mono
import pcm_metrics as stereo
from policy21 import CASE_IDS, CHANNELS, CASE_RATES, DECODERS, FRAMES, bounded_policy


def pcm(values): return struct.pack('<' + 'h' * len(values), *values)


def full_policy_rows():
    """Explicit nonzero raw samples for full7040-frame mono/stereo geometry."""
    rows = []
    for index, (name, channels, rate) in enumerate(zip(CASE_IDS, CHANNELS, CASE_RATES)):
        packet_bytes = [n * channels * 2 for n in FRAMES]
        reference = pcm(([17] if channels == 1 else [17, -19]) * 7040)
        metrics = mono if channels == 1 else stereo
        measured = metrics.compare(reference, reference, packet_bytes)
        rows.append(dict(case=index, id=name, channels=channels, rate=rate, bits=16, frames=list(FRAMES),
            packet_bytes=packet_bytes, pcm_bytes=len(reference), references={decoder: dict(
                comparison=copy.deepcopy(measured), reference_transition_nonzero={kind: [1] * channels for kind in ('SS', 'SL', 'LS', 'LL')},
                target_transition_nonzero={kind: [1] * channels for kind in ('SS', 'SL', 'LS', 'LL')}) for decoder in DECODERS}))
    return rows


class MonoKnownAnswers(unittest.TestCase):
    def test_signed_little_endian_extrema(self):
        self.assertEqual(mono.samples(bytes.fromhex('0080ffff00000100ff7f')), (-32768, -1, 0, 1, 32767))

    def test_odd_number_of_mono_frames_preserved(self):
        values = [3] * 12 + [-7]
        measured = mono.compare(pcm(values), pcm(values), [0] + [2] * 13)
        self.assertEqual((measured['frames'], measured['zero_lag_direct_mono']['samples'], len(measured['channels'])), (13, 13, 1))
        self.assertEqual(measured['packets'][-1]['all_samples']['reference_sum_squares'], 49)
        self.assertEqual(measured['packets'][-1]['byte_offset'], 24)
        self.assertEqual(measured['packets'][-1]['frames'], 1)

    def test_tail_mismatch_not_truncated(self):
        a, b = [0] * 13, [0] * 12 + [3]
        whole = mono.compare(pcm(a), pcm(b), [0] + [2] * 13)['zero_lag_direct_mono']
        self.assertEqual(whole['first_mismatch'], dict(sample=12, frame=12, channel=0, reference=0, target=3, signed_error=3))
        self.assertEqual(whole['max_abs_error'], 3)

    def test_error_extrema_no_s16_overflow(self):
        a, b = [-32768] + [0] * 11 + [32767], [32767] + [0] * 11 + [-32768]
        measured = mono.compare(pcm(a), pcm(b), [0] + [2] * 13)
        whole = measured['zero_lag_direct_mono']
        self.assertEqual((whole['min_signed_error'], whole['max_signed_error'], whole['max_abs_error']), (-65535, 65535, 65535))
        self.assertEqual(whole['sum_signed_error'], 0)
        self.assertEqual(whole['sum_squared_error'], 8589672450)
        self.assertEqual(whole['signed_error_histogram'], {'-65535': 1, '0': 11, '65535': 1})
        self.assertAlmostEqual(whole['rms_error'], math.sqrt(8589672450 / 13))
        self.assertEqual((whole['reference_clipped_samples'], whole['target_clipped_samples']), (2, 2))
        self.assertEqual(measured['packets'][1]['all_samples']['sum_squared_error'], 4294836225)
        self.assertEqual(measured['packets'][13]['all_samples']['sum_squared_error'], 4294836225)

    def test_zero_primer_and_complete_packet_coverage(self):
        measured = mono.compare(pcm(range(13)), pcm(range(13)), [0] + [2] * 13)
        primer = measured['packets'][0]
        self.assertEqual((primer['bytes'], primer['frames'], primer['all_samples']['samples']), (0, 0, 0))
        self.assertIsNone(primer['all_samples']['max_abs_error'])
        self.assertEqual(sum(p['bytes'] for p in measured['packets']), 26)
        self.assertEqual(sum(p['all_samples']['samples'] for p in measured['packets']), 13)
        self.assertTrue(all(len(p['channels']) == 1 for p in measured['packets']))

    def test_mono_routing_rejects_stereo_or_boolean_channels(self):
        for channels in (0, 2, True):
            with self.subTest(channels=channels):
                with self.assertRaisesRegex(RuntimeError, 'Exactly one actual mono channel'):
                    mono.compare(pcm([1] * 13), pcm([1] * 13), [0] + [2] * 13, channels=channels)

    def test_partial_sample_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Complete mono S16LE frames'):
            mono.samples(b'\0')

    def test_nonbytes_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Complete mono S16LE frames'):
            mono.samples(bytearray(b'\0\0'))

    def test_unequal_lengths_never_truncated(self):
        with self.assertRaisesRegex(RuntimeError, 'Exact full mono PCM byte counts'):
            mono.compare(pcm([1] * 13), pcm([1] * 12), [0] + [2] * 13)

    def test_target_padding_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Exact full mono PCM byte counts'):
            mono.compare(pcm([1] * 13), pcm([1] * 14), [0] + [2] * 13)

    def test_equal_extra_padding_not_in_geometry_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Fourteen complete mono packet boundaries'):
            mono.compare(pcm([1] * 14), pcm([1] * 14), [0] + [2] * 13)

    def test_bad_packet_boundaries_rejected(self):
        bad = ([0] + [2] * 12, [2] * 13 + [0], [0] + [2] * 12 + [1],
               [0] + [2] * 12 + [-2], [0] + [2] * 12 + [0], [False] + [2] * 13)
        for packets in bad:
            with self.subTest(packets=packets):
                with self.assertRaisesRegex(RuntimeError, 'Fourteen complete mono packet boundaries'):
                    mono.compare(pcm([1] * 13), pcm([1] * 13), packets)

    def test_fixed_range_alignment_diagnostic_does_not_change_primary(self):
        a = [i * 100 for i in range(26)]
        b = [0] + a[:-1]
        reference, target = pcm(a), pcm(b)
        measured = mono.compare(reference, target, [0] + [4] * 13)
        diagnostic = mono.alignment(reference, target, 2)
        self.assertEqual(measured['zero_lag_direct_mono']['max_abs_error'], 100)
        self.assertEqual(diagnostic['fixed_reference_frame_range'], [2, 24])
        pair = diagnostic['channel_pairs'][0]
        self.assertEqual((pair['reference_channel'], pair['target_channel']), (0, 0))
        self.assertEqual(pair['minimum_error_lags'], [1])
        self.assertTrue(all(row['samples'] == 22 for row in pair['candidates']))
        self.assertEqual(diagnostic['applied_shift_frames'], 0)
        self.assertFalse(diagnostic['applied_channel_swap'])
        self.assertEqual(reference, pcm(a))
        self.assertEqual(target, pcm(b))

    def test_alignment_rejects_unequal_or_insufficient_frames(self):
        for a, b, lag in ((pcm(range(13)), pcm(range(12)), 2), (pcm(range(4)), pcm(range(4)), 2)):
            with self.assertRaisesRegex(RuntimeError, 'Mono alignment frame shape'):
                mono.alignment(a, b, lag)

    def test_alignment_rejects_invalid_lag(self):
        for lag in (-1, 65, True):
            with self.assertRaisesRegex(RuntimeError, 'Diagnostic lag window'):
                mono.alignment(pcm(range(13)), pcm(range(13)), lag)

    def test_zero_lag_diagnostic_single_frame(self):
        diagnostic = mono.alignment(pcm([-1]), pcm([2]), 0)
        self.assertEqual(diagnostic['fixed_reference_frame_range'], [0, 1])
        self.assertEqual(diagnostic['channel_pairs'][0]['candidates'][0]['sum_squared_error'], 9)
        self.assertEqual(diagnostic['channel_pairs'][0]['minimum_error_lags'], [0])

    def test_maximum_lag_uses_same_single_interior_frame(self):
        diagnostic = mono.alignment(pcm([5] * 129), pcm([5] * 129), 64)
        self.assertEqual(diagnostic['fixed_reference_frame_range'], [64, 65])
        candidates = diagnostic['channel_pairs'][0]['candidates']
        self.assertEqual([r['target_lag_frames'] for r in candidates], list(range(-64, 65)))
        self.assertTrue(all(r['samples'] == 1 and r['sum_squared_error'] == 0 for r in candidates))
        with self.assertRaisesRegex(RuntimeError, 'Mono alignment frame shape'):
            mono.alignment(pcm([5] * 128), pcm([5] * 128), 64)

    def test_stereo_common_module_exact_identity_and_direct_measurement(self):
        source = Path(stereo.__file__).read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(),
                         'a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f')
        raw = pcm([17, -19] * 13)
        measured = stereo.compare(raw, raw, [0] + [4] * 13)
        self.assertEqual((measured['frames'], len(measured['channels'])), (13, 2))
        self.assertEqual(measured['zero_lag_direct_LR']['samples'], 26)
        self.assertEqual(measured['zero_lag_direct_LR']['max_abs_error'], 0)


class FixedBothReferencePolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rows = full_policy_rows()

    def test_full21_both_reference_bound2_accepted(self):
        policy, passed = bounded_policy(self.rows)
        self.assertTrue(passed)
        self.assertEqual(policy['required_reference_comparisons'], 42)
        self.assertEqual(policy['bounded_by_reference'], dict(vorbis=True, libvorbis=True))
        self.assertFalse(policy['applied_mono_duplication'])
        self.assertFalse(policy['applied_padding'])

    def test_two_lsb_boundary_both_references(self):
        rows = copy.deepcopy(self.rows)
        for decoder in DECODERS: rows[0]['references'][decoder]['comparison']['zero_lag_direct_mono']['max_abs_error'] = 2
        self.assertTrue(bounded_policy(rows)[1])

    def test_three_lsb_native_fails_even_if_xiph_passes(self):
        rows = copy.deepcopy(self.rows)
        rows[0]['references']['vorbis']['comparison']['zero_lag_direct_mono']['max_abs_error'] = 3
        policy, passed = bounded_policy(rows)
        self.assertFalse(passed)
        self.assertEqual(policy['bounded_by_reference'], dict(vorbis=False, libvorbis=True))

    def test_three_lsb_xiph_fails_even_if_native_passes(self):
        rows = copy.deepcopy(self.rows)
        rows[0]['references']['libvorbis']['comparison']['zero_lag_direct_mono']['max_abs_error'] = 3
        self.assertEqual(bounded_policy(rows)[0]['bounded_by_reference'], dict(vorbis=True, libvorbis=False))

    def test_bound_cannot_be_disabled_or_fitted(self):
        for bound in (None, True, 0, 1, 3, 65535):
            with self.assertRaisesRegex(RuntimeError, 'Only fixed predeclared bound2'):
                bounded_policy(self.rows, bound)

    def test_full20_subset_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Exact complete21'):
            bounded_policy(self.rows[:-1])

    def test_missing_native_reference_rejected(self):
        rows = copy.deepcopy(self.rows)
        del rows[0]['references']['vorbis']
        with self.assertRaisesRegex(RuntimeError, 'reference geometry'):
            bounded_policy(rows)

    def test_mono_channel_duplication_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]['references']['vorbis']['comparison']['channels'] *= 2
        with self.assertRaisesRegex(RuntimeError, 'measurement sample/packet counts'):
            bounded_policy(rows)

    def test_wrong_pcm_geometry_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]['packet_bytes'][-1] += 2
        with self.assertRaisesRegex(RuntimeError, 'reference geometry'):
            bounded_policy(rows)

    def test_silent_actual_channel_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]['references']['libvorbis']['comparison']['channels'][0]['target_nonzero_samples'] = 0
        self.assertFalse(bounded_policy(rows)[1])

    def test_missing_transition_rejected(self):
        rows = copy.deepcopy(self.rows)
        del rows[0]['references']['libvorbis']['target_transition_nonzero']['LS']
        self.assertFalse(bounded_policy(rows)[1])


if __name__ == '__main__': unittest.main()
