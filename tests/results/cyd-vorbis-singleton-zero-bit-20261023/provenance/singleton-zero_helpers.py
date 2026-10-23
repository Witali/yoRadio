"""Exact pure zero-witness functions; no source loading or current-file fallback."""
import copy
from dependency import need
import raw_helpers as prior

def parse_zero_audio(raw, book, packet):
    """Adapted explicit-zero parser; original parse_audio stays unchanged/original-only."""
    r = prior.Reader(raw); r.exact(1, 0, 'audio_packet_type'); r.exact(1, prior.MODES[packet], 'audio_mode')
    if prior.MODES[packet]:
        r.exact(1, prior.MODES[packet - 1], 'previous_window'); r.exact(1, prior.MODES[packet + 1], 'next_window')
    for _ in range(2):
        r.exact(1, 1, 'floor_present'); r.exact(8, 255, 'floor_y0'); r.exact(8, 255, 'floor_y1')
    classes = [r.take(1) for _ in range(2)]
    need(classes == [(packet + c) % 2 for c in range(2)], 'both_classwords_before_tokens')
    need(book['lookup_type'] == 1 and book['dimensions'] == 16, 'exact_zero_control_map1_shape')
    entry = prior.singleton_id(book['lengths']); token_first = r.position
    wires, selected, residues, positions = [], [], [], []
    values = prior.table(book)
    for _ in range(2):
        positions.append(r.position)
        wire = r.exact(1, 0, 'preferred_singleton_token_must_be_zero')
        wires.append([wire]); selected.append([entry])
        residues.append(prior.interleave0([values[entry]], 16))
    used = r.position
    need(used == 40 + 2 * prior.MODES[packet], 'one_bit_per_singleton_token')
    report = r.finish()
    need(all(any(v) and max(map(abs, v)) <= 16 for v in residues), 'actual_bounded_nonzero_spectrum')
    return dict(classwords=classes, vector_entry_ids=selected, residue_vectors=residues,
        one_bit_per_single_entry=True, used_bits=used, token_bits=used - token_first, token_count=2,
        padding_bits=report['padding_bits'], single_entry_wire_bits=wires), report, positions


def unchanged_except_tokens(old, new, positions):
    need(len(old) == len(new) and len(positions) == len(set(positions)) == 2, 'same_packet_bytes_two_token_positions')
    changes = []
    for bit in range(len(old) * 8):
        a, b = (old[bit // 8] >> (bit % 8)) & 1, (new[bit // 8] >> (bit % 8)) & 1
        if bit in positions:
            need(b == 0, 'actual_zero_token_bits')
            if a != b:
                changes.append(bit)
        else:
            need(a == b, 'all_non_token_bits_unchanged')
    need(len(changes) == 1, 'one_original_one_bit_cleared_per_packet')
    return changes


def zero_field_report(old, positions):
    expected = copy.deepcopy(old)
    selected = [f for f in expected['fields'] if f['offset'] in positions]
    need(len(selected) == 2 and all(f['width'] == 1 for f in selected), 'actual_token_fields_in_metadata')
    for f in selected:
        f['value'] = 0
    return expected


def validate_matrix_status(matrix):
    need(matrix['status'] == 'CONSTRUCTED_INDEPENDENT_WITNESS_AND_REFERENCE_PENDING', 'exact_pending_construction_status')


def validate_field_report_keys(new, old):
    need(set(old) == {'identification', 'comment', 'setup', 'audio'} and set(new) == set(old), 'exact_new_case_field_report_keys')
