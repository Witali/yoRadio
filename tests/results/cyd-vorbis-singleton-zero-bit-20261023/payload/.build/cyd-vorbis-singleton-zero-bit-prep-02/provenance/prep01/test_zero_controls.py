"""Proposed pure host controls; no generation main, reference, decoder or target."""
import copy
import unittest
import generate_zero as g
import independent_zero_witness as w


def fixture(index=0):
    cases, fields, raw = g.originals(); original = cases[index]
    case, reports, data, changes = g.build_case(original, fields, raw)
    return original, fields[original['id']], raw, case, reports, data, changes


def packets(case, data):
    raw = data[case['audio']]
    return [raw[a:b] for a, b in zip(case['offsets'], case['offsets'][1:])]


def flip(raw, bit):
    data = bytearray(raw); data[bit // 8] ^= 1 << (bit % 8); return bytes(data)


class ZeroControls(unittest.TestCase):
    def reject(self, reason, action):
        with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
            action()

    def test_all_four_complete_pairs_all_112_packets(self):
        for index in range(4):
            old, old_fields, raw, new, fields, data, changes = fixture(index)
            book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
            for p, (a, b) in enumerate(zip(packets(old, raw), packets(new, data))):
                original, original_report = w.prior.parse_audio(a, book, p)
                zero, report, positions = w.parse_zero_audio(b, book, p)
                expected = copy.deepcopy(original); expected['single_entry_wire_bits'] = [[0], [0]]
                self.assertEqual(zero, expected)
                self.assertEqual(w.unchanged_except_tokens(a, b, positions), changes[p]['changed_bit_offsets'])
                w.prior.compare_field_report(report, fields['audio'][p])
                w.prior.compare_field_report(original_report, old_fields['audio'][p])

    def test_frozen_original_bytes_and_metadata_preserved(self):
        cases, fields, raw = g.originals(); before = copy.deepcopy((cases, fields, raw))
        for case in cases:
            g.build_case(case, fields, raw)
        self.assertEqual((cases, fields, raw), before)

    def test_all_identification_comment_setup_bytes_identical(self):
        for i in range(4):
            old, _, raw, new, _, data, _ = fixture(i)
            for k in ('identification', 'comment', 'setup'):
                self.assertEqual(raw[old[k]], data[new[k]])

    def test_dense_original_index_zero(self):
        old, _, raw, new, _, data, _ = fixture(0); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        actual, _, _ = w.parse_zero_audio(packets(new, data)[0], book, 0)
        self.assertEqual(actual['vector_entry_ids'], [[0], [0]])

    def test_sparse_original_index_four(self):
        old, _, raw, new, _, data, _ = fixture(2); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        actual, _, _ = w.parse_zero_audio(packets(new, data)[0], book, 0)
        self.assertEqual(actual['vector_entry_ids'], [[4], [4]])

    def test_prior_alternating_parser_is_unchanged_original_only(self):
        old, _, raw, new, _, data, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        self.reject('actual_singleton_wire_pattern', lambda: w.prior.parse_audio(packets(new, data)[0], book, 0))

    def test_zero_parser_rejects_original_one_token(self):
        old, _, raw, _, _, _, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        self.reject('preferred_singleton_token_must_be_zero', lambda: w.parse_zero_audio(packets(old, raw)[0], book, 0))

    def test_mode_change_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        self.reject('audio_mode', lambda: w.parse_zero_audio(flip(packets(new, data)[0], 1), book, 0))

    def test_window_change_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        self.reject('previous_window', lambda: w.parse_zero_audio(flip(packets(new, data)[2], 2), book, 2))

    def test_classword_change_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        self.reject('both_classwords_before_tokens', lambda: w.parse_zero_audio(flip(packets(new, data)[0], 36), book, 0))

    def test_floor_change_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        self.reject('floor_present', lambda: w.parse_zero_audio(flip(packets(new, data)[0], 2), book, 0))

    def test_missing_token_byte_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        self.reject('bounded_bit_read', lambda: w.parse_zero_audio(packets(new, data)[0][:-1], book, 0))

    def test_extra_byte_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        self.reject('exact_bytes_and_padding_length', lambda: w.parse_zero_audio(packets(new, data)[0] + b'\0', book, 0))

    def test_nonzero_padding_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); book, _, _ = w.prior.parse_setup(raw[old['setup']], old['id'])
        packet = packets(new, data)[2]
        self.reject('zero_padding', lambda: w.parse_zero_audio(flip(packet, len(packet) * 8 - 1), book, 2))

    def test_pair_non_token_bit_change_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); a, b = packets(old, raw)[0], packets(new, data)[0]
        self.reject('all_non_token_bits_unchanged', lambda: w.unchanged_except_tokens(a, flip(b, 5), [38, 39]))

    def test_pair_padding_change_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); a, b = packets(old, raw)[2], packets(new, data)[2]
        self.reject('all_non_token_bits_unchanged', lambda: w.unchanged_except_tokens(a, flip(b, 47), [40, 41]))

    def test_pair_one_token_is_not_zero_rejected(self):
        old, _, raw, new, _, data, _ = fixture(); a, b = packets(old, raw)[0], packets(new, data)[0]
        self.reject('actual_zero_token_bits', lambda: w.unchanged_except_tokens(a, flip(b, 38), [38, 39]))

    def test_pair_lengths_must_match(self):
        old, _, raw, new, _, data, _ = fixture(); a, b = packets(old, raw)[0], packets(new, data)[0]
        self.reject('same_packet_bytes_two_token_positions', lambda: w.unchanged_except_tokens(a, b + b'\0', [38, 39]))

    def test_missing_token_metadata_rejected(self):
        old, fields, raw, _, _, _, _ = fixture(); report = copy.deepcopy(fields['audio'][0]); report['fields'].pop()
        self.reject('two_original_singleton_fields', lambda: g.zero_packet(packets(old, raw)[0], report, 0, old['id']))

    def test_changed_token_offset_metadata_rejected(self):
        old, fields, raw, _, _, _, _ = fixture(); report = copy.deepcopy(fields['audio'][0]); report['fields'][-1]['offset'] -= 1
        self.reject('actual_original_token_field_shape', lambda: g.zero_packet(packets(old, raw)[0], report, 0, old['id']))

    def test_actual_original_bit_must_match_metadata(self):
        old, fields, raw, _, _, _, _ = fixture()
        self.reject('actual_original_token_value', lambda: g.zero_packet(flip(packets(old, raw)[0], 39), fields['audio'][0], 0, old['id']))

    def test_field_report_only_zeroes_actual_tokens(self):
        _, fields, _, _, _, _, _ = fixture(); original = copy.deepcopy(fields['audio'][0])
        changed = w.zero_field_report(original, [38, 39])
        self.assertEqual(original, fields['audio'][0])
        self.assertEqual([f['value'] for f in changed['fields'][-2:]], [0, 0])

    def test_all_new_carriers_independent_CRC_and_packet_checks(self):
        for i in range(4):
            old, _, _, new, _, data, _ = fixture(i)
            full = [data[new[k]] for k in ('identification', 'comment', 'setup')] + packets(new, data)
            self.assertEqual(len(w.prior.carrier(data[new['ogg']], full, [0, 0, 0] + old['packet_granules'], 0x53470005 + i)), 17)

    def test_changed_new_carrier_CRC_rejected(self):
        old, _, _, new, _, data, _ = fixture()
        full = [data[new[k]] for k in ('identification', 'comment', 'setup')] + packets(new, data)
        carrier = data[new['ogg']]
        self.reject('ogg_crc', lambda: w.prior.carrier(flip(carrier, len(carrier) * 8 - 1), full, [0, 0, 0] + old['packet_granules'], 0x53470005))


if __name__ == '__main__':
    unittest.main()
