"""Proposed host construction controls only; never a codec, target or PCM test."""
import copy
from collections import Counter
from fractions import Fraction
import unittest

import generate_singletons as g
import independent_witness as w


def changed_field(bits, name, value):
    raw = bytearray(bits.data())
    field = next(f for f in bits.fields if f['name'] == name)
    for bit in range(field['width']):
        pos = field['offset'] + bit
        raw[pos // 8] = (raw[pos // 8] & ~(1 << (pos % 8))) | (((value >> bit) & 1) << (pos % 8))
    return bytes(raw)


def proof(book):
    return [w.parse_audio(g.audio(book, p).data(), w.expected_book(book['id']), p)[0] for p in range(14)]


def audit(book, observed):
    active = g.active_id(book)
    usage = Counter(e for p in observed for ch in p['vector_entry_ids'] for e in ch)
    return dict(**g.raw_book(book), active_original_ids=[active],
        inactive_original_ids=[i for i, n in enumerate(book['lengths']) if not n],
        vectors_by_original_entry=g.books.vectors(book), selected_original_id_counts={str(k): v for k, v in sorted(usage.items())},
        declared_multiplicand_count=len(book['multiplicands']), all_declared_lookup_values_retained=True,
        codewords_msb=[None if not n else '0' for n in book['lengths']],
        intended_public_setup_path=('map1_dec_type2' if book['lookup_type'] == 1 else
            'map2_dec_type3' if book['dimensions'] == 16 else 'map2_dec_type1'), intended_setup_path_only_not_observed=True)


def carrier_fixture(wrong_granule=False, serial=0x53470001):
    book = g.configurations()[0]
    packets = [g.base.identification(8, 11, 192000).data(), g.base.comment().data(), g.setup(book).data()] + [g.audio(book, p).data() for p in range(14)]
    sizes = [2048 if m else 256 for m in w.MODES]
    frames = [0] + [(a + b) // 4 for a, b in zip(sizes, sizes[1:])]
    granules = [0, 0, 0]; total = 0
    for n in frames:
        total += n; granules.append(total)
    encoded = list(granules)
    if wrong_granule:
        encoded[-1] += 1
    raw = b''.join(g.base.page(p, serial, i, encoded[i], 2 if i == 0 else 4 if i == 16 else 0)
                   for i, p in enumerate(packets))
    return raw, packets, granules


class ConstructionControls(unittest.TestCase):
    def reject(self, reason, action):
        with self.assertRaisesRegex(ValueError, '^' + reason + '$'):
            action()

    def test_all_eight_complete_setups(self):
        for b in g.configurations():
            actual, evidence, report = w.parse_setup(g.setup(b).data(), b['id'])
            self.assertEqual(actual, g.raw_book(b))
            self.assertEqual(evidence['active_original_id'], g.active_id(b))
            w.compare_field_report(report, g.setup(b).report())

    def test_all_112_complete_audio_packets(self):
        for b in g.configurations():
            for p in range(14):
                bits = g.audio(b, p)
                actual, fields = w.parse_audio(bits.data(), w.expected_book(b['id']), p)
                self.assertEqual(actual, g.packet_intention(b, p))
                w.compare_field_report(fields, bits.report())

    def test_dense_singleton_both_bits_return_original_zero(self):
        b = g.configurations()[4]
        actual, _ = w.parse_audio(g.audio(b, 0).data(), w.expected_book(b['id']), 0)
        self.assertEqual(actual['single_entry_wire_bits'], [[0], [1]])
        self.assertEqual(actual['vector_entry_ids'], [[0], [0]])

    def test_sparse_singleton_both_bits_return_original_four(self):
        b = g.configurations()[6]
        actual, _ = w.parse_audio(g.audio(b, 0).data(), w.expected_book(b['id']), 0)
        self.assertEqual(actual['single_entry_wire_bits'], [[0], [1]])
        self.assertEqual(actual['vector_entry_ids'], [[4], [4]])

    def test_singleton_length_two_rejected(self):
        self.reject('single_active_codeword_must_have_length1', lambda: w.singleton_id([0, 2, 0]))

    def test_no_active_codeword_rejected(self):
        self.reject('single_active_codeword_must_have_length1', lambda: w.singleton_id([0, 0]))

    def test_two_active_entries_are_not_singleton(self):
        self.reject('single_active_codeword_must_have_length1', lambda: w.singleton_id([1, 1]))

    def test_all_original_map2_rows_include_holes(self):
        for b in g.configurations()[:4]:
            values = w.table(w.expected_book(b['id']))
            self.assertEqual(len(values), 4)
            self.assertEqual(len({tuple(row) for row in values}), 4)
            self.assertNotEqual(values[0], values[2])

    def test_missing_map2_hole_multiplicands_rejected(self):
        b = copy.deepcopy(g.configurations()[0]); b['multiplicands'] = b['multiplicands'][8:12]
        self.reject('all_declared_lookup_multiplicands_required', lambda: g.setup(b))

    def test_map1_quantvals_uses_declared_entry_count(self):
        self.assertEqual(w.quantvals(6, 16), 1)
        self.assertEqual(w.quantvals(5, 2), 2)
        self.assertEqual(w.table(w.expected_book(w.IDS[6]))[4], [1] * 16)

    def test_exact_fraction_float_equations(self):
        self.assertEqual(w.unpack(0xE2800001), Fraction(-1))
        self.assertEqual(w.unpack(0x62800001), Fraction(1))
        self.assertEqual(w.unpack((787 << 21) | 1), Fraction(1, 2))

    def test_residue0_uses_partition_interleave(self):
        vectors = [[1, -1, 1, -1] for _ in range(4)]
        self.assertEqual(w.interleave0(vectors, 4), [1] * 4 + [-1] * 4 + [1] * 4 + [-1] * 4)
        self.assertNotEqual(w.interleave0(vectors, 4), sum(vectors, []))

    def test_three_d16_encodings_have_equal_spectra_and_wires(self):
        configs = g.configurations()
        for indices in ((2, 4, 6), (3, 5, 7)):
            all_proofs = [proof(configs[i]) for i in indices]
            for packets in all_proofs[1:]:
                self.assertEqual([p['residue_vectors'] for p in packets], [p['residue_vectors'] for p in all_proofs[0]])
                self.assertEqual([p['single_entry_wire_bits'] for p in packets], [p['single_entry_wire_bits'] for p in all_proofs[0]])
            wires = [b''.join(g.audio(configs[i], p).data() for p in range(14)) for i in indices]
            self.assertEqual(wires, [wires[0]] * 3)

    def test_sequence_flag_changes_actual_spectrum(self):
        configs = g.configurations()
        for a, b in ((0, 1), (2, 3), (4, 5), (6, 7)):
            self.assertNotEqual(proof(configs[a])[0]['residue_vectors'], proof(configs[b])[0]['residue_vectors'])

    def test_wire_length_field_corruption_rejected(self):
        b = g.configurations()[0]; bits = g.setup(b)
        raw = changed_field(bits, 'book[1].entry[2].length_minus_1', 1)
        self.reject('actual_original_vector_book_fields', lambda: w.parse_setup(raw, b['id']))

    def test_inactive_original_lookup_row_corruption_rejected(self):
        b = g.configurations()[2]; bits = g.setup(b)
        raw = changed_field(bits, 'book[1].multiplicand[0]', 1)
        self.reject('actual_original_vector_book_fields', lambda: w.parse_setup(raw, b['id']))

    def test_residue_type_must_be_zero(self):
        b = g.configurations()[0]; bits = g.setup(b)
        raw = changed_field(bits, 'residue[0].type', 1)
        self.reject('complete_floor1_residue0_mapping_modes_suffix', lambda: w.parse_setup(raw, b['id']))

    def test_missing_token_byte_rejected(self):
        b = g.configurations()[0]
        self.reject('bounded_bit_read', lambda: w.parse_audio(g.audio(b, 0).data()[:-1], g.raw_book(b), 0))

    def test_zero_bit_singleton_interpretation_rejected(self):
        b = g.configurations()[0]; bits = g.audio(b, 0)
        shortened = g.base.Bits(); shortened.bits = bits.bits[:38]
        self.reject('bounded_bit_read', lambda: w.parse_audio(shortened.data(), g.raw_book(b), 0, check_wire_pattern=False))

    def test_extra_audio_byte_rejected(self):
        b = g.configurations()[4]
        self.reject('exact_bytes_and_padding_length', lambda: w.parse_audio(g.audio(b, 0).data() + b'\0', g.raw_book(b), 0))

    def test_nonzero_padding_rejected(self):
        b = g.configurations()[4]; raw = bytearray(g.audio(b, 2).data()); raw[-1] |= 0x80
        self.reject('zero_padding', lambda: w.parse_audio(raw, g.raw_book(b), 2))

    def test_changed_singleton_wire_pattern_detected(self):
        b = g.configurations()[0]; bits = g.audio(b, 0)
        raw = changed_field(bits, 'residue[0].entry[0]=2', 1)
        self.reject('actual_singleton_wire_pattern', lambda: w.parse_audio(raw, g.raw_book(b), 0))

    def test_changed_mode_rejected(self):
        b = g.configurations()[0]; raw = changed_field(g.audio(b, 0), 'mode', 1)
        self.reject('audio_mode', lambda: w.parse_audio(raw, g.raw_book(b), 0))

    def test_changed_scalar_classword_rejected(self):
        b = g.configurations()[0]; raw = changed_field(g.audio(b, 0), 'classword[0]', 1)
        self.reject('both_classwords_before_tokens', lambda: w.parse_audio(raw, g.raw_book(b), 0))

    def test_wrong_active_original_index_metadata_rejected(self):
        b = g.configurations()[6]; observed = proof(b); declared = audit(b, observed); declared['active_original_ids'] = [0]
        self.reject('metadata_original_active_indices', lambda: w.compare_audit(g.raw_book(b), declared, observed))

    def test_unused_original_vector_metadata_rejected(self):
        b = g.configurations()[0]; observed = proof(b); declared = audit(b, observed); declared['vectors_by_original_entry'][0][0] = 99
        self.reject('metadata_all_original_vectors', lambda: w.compare_audit(g.raw_book(b), declared, observed))

    def test_metadata_packet_consumption_rejected(self):
        b = g.configurations()[4]; bits = g.audio(b, 0); _, actual = w.parse_audio(bits.data(), g.raw_book(b), 0)
        declared = bits.report(); declared['used_bits'] -= 1
        self.reject('metadata_bit_lengths', lambda: w.compare_field_report(actual, declared))

    def test_complete_carrier_seventeen_pages(self):
        raw, packets, granules = carrier_fixture()
        self.assertEqual(len(w.carrier(raw, packets, granules, 0x53470001)), 17)
        self.assertEqual(w.crc(b'123456789'), 0x89A1897F)

    def test_carrier_crc_corruption_rejected(self):
        raw, packets, granules = carrier_fixture(); raw = bytearray(raw); raw[-1] ^= 1
        self.reject('ogg_crc', lambda: w.carrier(raw, packets, granules, 0x53470001))

    def test_valid_CRC_wrong_granule_rejected(self):
        raw, packets, granules = carrier_fixture(wrong_granule=True)
        self.reject('ogg_exact_granule', lambda: w.carrier(raw, packets, granules, 0x53470001))

    def test_valid_CRC_wrong_serial_rejected(self):
        raw, packets, granules = carrier_fixture(serial=0x53470002)
        self.reject('ogg_serial_sequence', lambda: w.carrier(raw, packets, granules, 0x53470001))


if __name__ == '__main__':
    unittest.main()
