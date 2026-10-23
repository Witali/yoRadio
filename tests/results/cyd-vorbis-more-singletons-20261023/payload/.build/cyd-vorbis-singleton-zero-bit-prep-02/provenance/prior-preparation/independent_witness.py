"""Independent bounded LSb/Fraction/CRC witness; imports no generator or codec."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import struct

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tests/vorbis_format_corpus/generate_books.py').is_file())
MODES = tuple(int(c == 'L') for c in 'SSLLLSLSSSLLSS')
IDS = tuple([f'map2_sparse_single_d{d}_seq{s}' for d in (4, 16) for s in (0, 1)] +
            [f'map1_{kind}_single_d16_seq{s}' for kind in ('dense', 'sparse') for s in (0, 1)])


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Reader:
    def __init__(self, data):
        self.data, self.position, self.fields = bytes(data), 0, []

    def take(self, width):
        need(type(width) is int and 0 <= width <= 64 and self.position + width <= len(self.data) * 8,
             'bounded_bit_read')
        first, value = self.position, 0
        for bit in range(width):
            p = self.position + bit
            value |= ((self.data[p // 8] >> (p % 8)) & 1) << bit
        self.position += width
        self.fields.append((first, width, value))
        return value

    def exact(self, width, expected, reason):
        value = self.take(width)
        need(value == expected, reason)
        return value

    def finish(self):
        used, trace = self.position, list(self.fields)
        remaining = len(self.data) * 8 - used
        need(0 <= remaining < 8, 'exact_bytes_and_padding_length')
        need(self.take(remaining) == 0, 'zero_padding')
        return dict(bytes=len(self.data), used_bits=used, padding_bits=remaining, trace=trace)


def prefix(r, packet_type):
    r.exact(8, packet_type, 'header_packet_type')
    need(bytes(r.take(8) for _ in range(6)) == b'vorbis', 'header_signature')


def unpack(word):
    mantissa = word & ((1 << 21) - 1)
    if word & (1 << 31):
        mantissa = -mantissa
    exponent = ((word >> 21) & 1023) - 788
    return Fraction(mantissa) * Fraction(2) ** exponent


def quantvals(entries, dim):
    need(1 <= entries <= 6 and 1 <= dim <= 16, 'finite_lookup_bounds')
    return max(n for n in range(1, entries + 1) if n ** dim <= entries)


def singleton_id(lengths):
    active = [i for i, n in enumerate(lengths) if n]
    need(len(active) == 1 and lengths[active[0]] == 1, 'single_active_codeword_must_have_length1')
    return active[0]


def read_book(r):
    start = r.position
    r.exact(24, 0x564342, 'codebook_sync')
    dim, entries = r.take(16), r.take(24)
    need(1 <= dim <= 16 and 1 <= entries <= 6, 'finite_book_bounds')
    r.exact(1, 0, 'finite_unordered_book')
    sparse = r.take(1)
    lengths = []
    for _ in range(entries):
        used = r.take(1) if sparse else 1
        lengths.append(r.take(5) + 1 if used else 0)
    lookup = r.take(4)
    need(lookup in (0, 1, 2), 'lookup_type')
    result = dict(entries=entries, dimensions=dim, ordered=False, lengths=lengths, lookup_type=lookup)
    offsets = dict(start=start, lengths_end=r.position - 4, lookup_type_bit=r.position - 4)
    if lookup:
        minimum, delta = r.take(32), r.take(32)
        need(minimum == (0x80000000 | (788 << 21) | 1) and delta == ((788 << 21) | 1), 'exact_finite_packed_float_words')
        a, b = unpack(minimum), unpack(delta)
        need(a.denominator == b.denominator == 1, 'exact_integer_packed_values')
        result['minimum'], result['delta'] = int(a), int(b)
        result['value_bits'], result['sequence_p'] = r.take(4) + 1, r.take(1)
        count = quantvals(entries, dim) if lookup == 1 else entries * dim
        offsets['multiplicands_first_bit'] = r.position
        result['multiplicands'] = [r.take(result['value_bits']) for _ in range(count)]
        offsets['multiplicands_end_bit'] = r.position
    offsets['end'] = r.position
    return result, offsets


def expected_book(name):
    need(name in IDS, 'known_exact_case_id')
    match = re.fullmatch(r'map([12])_(dense|sparse)_single_d(4|16)_seq([01])', name)
    lookup, kind, dim, seq = int(match[1]), match[2], int(match[3]), int(match[4])
    if lookup == 2:
        active = [2, 0, 2, 0] if dim == 4 else [2] * 16
        lengths = [0, 0, 1, 0]
        values = [0] * dim + [1] * dim + active + [3] * dim
    else:
        lengths = [1] if kind == 'dense' else [0, 0, 0, 0, 1, 0]
        values = [2]
    return dict(entries=len(lengths), dimensions=dim, ordered=False, lengths=lengths, lookup_type=lookup,
                minimum=-1, delta=1, value_bits=2, sequence_p=seq, multiplicands=values)


def table(book):
    result = []
    dim, entries = book['dimensions'], book['entries']
    count = quantvals(entries, dim) if book['lookup_type'] == 1 else entries * dim
    need(len(book['multiplicands']) == count, 'all_declared_multiplicands_including_holes')
    for entry in range(entries):
        vector, last, divisor = [], Fraction(0), 1
        for coordinate in range(dim):
            offset = ((entry // divisor) % count if book['lookup_type'] == 1 else entry * dim + coordinate)
            value = Fraction(book['multiplicands'][offset]) * Fraction(book['delta']) + Fraction(book['minimum']) + last
            need(value.denominator == 1, 'finite_exact_integer_vector')
            vector.append(int(value))
            last = value if book['sequence_p'] else Fraction(0)
            divisor *= count
        result.append(vector)
    return result


def parse_setup(raw, name):
    r = Reader(raw); prefix(r, 5); r.exact(8, 1, 'exact_two_books')
    scalar, scalar_offsets = read_book(r)
    need(scalar == dict(entries=2, dimensions=1, ordered=False, lengths=[1, 1], lookup_type=0), 'actual_scalar_book')
    book, book_offsets = read_book(r)
    need(book == expected_book(name), 'actual_original_vector_book_fields')
    active = singleton_id(book['lengths'])
    suffix = ((6, 0), (16, 0), (6, 0), (16, 1), (5, 0), (2, 0), (4, 10),
        (6, 0), (16, 0), (24, 0), (24, 16), (24, 15), (6, 1), (8, 0),
        (3, 1), (1, 0), (3, 1), (1, 0), (8, 1), (8, 1),
        (6, 0), (16, 0), (1, 0), (1, 0), (2, 0), (8, 0), (8, 0), (8, 0), (6, 1),
        (1, 0), (16, 0), (16, 0), (8, 0), (1, 1), (16, 0), (16, 0), (8, 0), (1, 1))
    for width, value in suffix:
        r.exact(width, value, 'complete_floor1_residue0_mapping_modes_suffix')
    report = r.finish()
    return book, dict(active_original_id=active, book_offsets=[scalar_offsets, book_offsets],
                      vectors_by_original_entry=table(book)), report


def parse_identification(raw):
    r = Reader(raw); prefix(r, 1)
    for width, value in ((32, 0), (8, 2), (32, 192000), (32, 0), (32, 0), (32, 0), (4, 8), (4, 11), (1, 1)):
        r.exact(width, value, 'identification_fields')
    return r.finish()


def parse_comment(raw):
    r = Reader(raw); prefix(r, 3)
    vendor = b'yoRadio minimal block-format supplement v1'
    r.exact(32, len(vendor), 'comment_vendor_length')
    need(bytes(r.take(8) for _ in range(len(vendor))) == vendor, 'comment_vendor_bytes')
    r.exact(32, 0, 'comment_zero_user_comments'); r.exact(1, 1, 'comment_framing')
    return r.finish()


def interleave0(vectors, dimension):
    need(len(vectors) == 16 // dimension and all(len(v) == dimension for v in vectors), 'residue0_partition_shape')
    result = [0] * 16
    for step, vector in enumerate(vectors):
        for coordinate, value in enumerate(vector):
            result[step + coordinate * len(vectors)] += value
    return result


def parse_audio(raw, book, packet, check_wire_pattern=True):
    r = Reader(raw); r.exact(1, 0, 'audio_packet_type'); r.exact(1, MODES[packet], 'audio_mode')
    if MODES[packet]:
        r.exact(1, MODES[packet - 1], 'previous_window'); r.exact(1, MODES[packet + 1], 'next_window')
    for _ in range(2):
        r.exact(1, 1, 'floor_present'); r.exact(8, 255, 'floor_y0'); r.exact(8, 255, 'floor_y1')
    classes = [r.take(1) for _ in range(2)]
    need(classes == [(packet + channel) % 2 for channel in range(2)], 'both_classwords_before_tokens')
    entry = singleton_id(book['lengths']); step = 16 // book['dimensions']; token_first = r.position
    wires, selected, residues = [], [], []
    values = table(book)
    for channel in range(2):
        wire = [r.take(1) for _ in range(step)]  # Both branches map to the sole ORIGINAL entry.
        if check_wire_pattern:
            need(wire == [(packet + channel + vector) % 2 for vector in range(step)], 'actual_singleton_wire_pattern')
        wires.append(wire); selected.append([entry] * step)
        residues.append(interleave0([values[entry] for _ in range(step)], book['dimensions']))
    used = r.position
    need(used == 38 + 2 * MODES[packet] + 2 * step, 'one_bit_per_singleton_token')
    report = r.finish()
    need(all(any(v) and max(map(abs, v)) <= 16 for v in residues), 'actual_bounded_nonzero_spectrum')
    return dict(classwords=classes, vector_entry_ids=selected, residue_vectors=residues,
        one_bit_per_single_entry=True, used_bits=used, token_bits=used - token_first, token_count=2 * step,
        padding_bits=report['padding_bits'], single_entry_wire_bits=wires), report


def crc(raw):
    # Direct (non-reflected) CRC table, independently implemented here; no helper import.
    table_values = []
    for byte in range(256):
        n = byte << 24
        for _ in range(8):
            n = ((n << 1) ^ (0x04C11DB7 if n & 0x80000000 else 0)) & 0xFFFFFFFF
        table_values.append(n)
    value = 0
    for byte in raw:
        value = ((value << 8) & 0xFFFFFFFF) ^ table_values[(value >> 24) ^ byte]
    return value


def carrier(raw, packets, granules, serial):
    pages, position = [], 0
    while position < len(raw):
        need(len(raw) - position >= 27 and raw[position:position + 4] == b'OggS', 'ogg_capture_and_header')
        version, flags, granule, actual_serial, sequence, checksum, count = struct.unpack_from('<BBQIIIB', raw, position + 4)
        need(version == 0 and 1 <= count <= 255, 'ogg_version_lacing_count')
        start = position + 27; lace = raw[start:start + count]
        need(len(lace) == count and all(n == 255 for n in lace[:-1]) and lace[-1] < 255, 'one_complete_packet_per_page')
        end = start + count + sum(lace)
        need(end <= len(raw), 'ogg_page_bounds')
        page = bytearray(raw[position:end]); page[22:26] = b'\0' * 4
        need(crc(page) == checksum, 'ogg_crc')
        index = len(pages)
        need(index < 17 and actual_serial == serial and sequence == index, 'ogg_serial_sequence')
        need(flags == (2 if index == 0 else 4 if index == 16 else 0), 'ogg_BOS_EOS_no_continuation')
        need(granule == granules[index], 'ogg_exact_granule')
        payload = raw[start + count:end]
        need(payload == packets[index], 'ogg_exact_raw_packet')
        pages.append(dict(offset=position, bytes=end - position, packet_bytes=len(payload),
                          checksum=checksum, granule=granule, flags=flags, sequence=sequence))
        position = end
    need(len(pages) == 17 and position == len(raw), 'exact_seventeen_pages')
    return pages


def compare_field_report(actual, declared):
    need({k: declared[k] for k in ('bytes', 'used_bits', 'padding_bits')} ==
         {k: actual[k] for k in ('bytes', 'used_bits', 'padding_bits')}, 'metadata_bit_lengths')
    need([(f['offset'], f['width'], f['value']) for f in declared['fields']] == actual['trace'], 'every_metadata_field_matches_actual_parse')


def compare_audit(book, audit, observed):
    need(set(audit) == set(book) | {'active_original_ids', 'inactive_original_ids', 'vectors_by_original_entry',
         'selected_original_id_counts', 'declared_multiplicand_count', 'all_declared_lookup_values_retained',
         'codewords_msb', 'intended_public_setup_path', 'intended_setup_path_only_not_observed'}, 'exact_book_audit_keys')
    need({k: audit[k] for k in book} == book, 'metadata_actual_book_fields')
    active = singleton_id(book['lengths']); inactive = [i for i, n in enumerate(book['lengths']) if not n]
    need(audit['active_original_ids'] == [active] and audit['inactive_original_ids'] == inactive, 'metadata_original_active_indices')
    need(audit['vectors_by_original_entry'] == table(book), 'metadata_all_original_vectors')
    need(audit['declared_multiplicand_count'] == len(book['multiplicands']) and
         audit['all_declared_lookup_values_retained'] is True, 'metadata_all_original_multiplicands')
    need(audit['codewords_msb'] == [None if not n else '0' for n in book['lengths']], 'metadata_singleton_codewords')
    usage = Counter(e for p in observed for ch in p['vector_entry_ids'] for e in ch)
    need(audit['selected_original_id_counts'] == {str(k): v for k, v in sorted(usage.items())}, 'metadata_actual_original_usage')
    path = ('map1_dec_type2' if book['lookup_type'] == 1 else 'map2_dec_type3' if book['dimensions'] == 16 else 'map2_dec_type1')
    need(audit['intended_public_setup_path'] == path and audit['intended_setup_path_only_not_observed'] is True,
         'setup_path_remains_source_intention_only')


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(raw), sha256=sha(raw))


def check_prep(expected):
    need(sha((HERE / 'readiness.json').read_bytes()) == expected, 'reviewed_preparation_readiness')
    data = json.loads((HERE / 'readiness.json').read_bytes())
    need(data['schema'] == 'more-singletons-source-only-readiness-v1' and data['runtime_executed'] is False, 'source_only_readiness')
    files = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
    need(files == set(data['files']) | {'readiness.json'}, 'unchanged_preparation_file_set')
    for name, v in data['files'].items():
        p = (HERE / name).resolve()
        need(p.is_relative_to(HERE) and p.stat().st_size == v['bytes'] and sha(p.read_bytes()) == v['sha256'], 'unchanged_preparation_hashes')
    origins = json.loads((HERE / 'source-pins.json').read_bytes())['inputs']
    for x in origins:
        need(fact(Path(x['source']))['sha256'] == x['sha256'], 'unchanged_canonical_origins')
    return [fact(HERE / name) for name in sorted(files)] + [fact(Path(x['source'])) for x in origins]


def witness(generated, manifest_sha, readiness_sha):
    source_before = check_prep(readiness_sha)
    generated = generated.resolve()
    need(generated.is_relative_to(ROOT / '.build') and not generated.is_relative_to(HERE), 'bounded_generated_root')
    manifest_raw = (generated / 'manifest.json').read_bytes()
    need(sha(manifest_raw) == manifest_sha, 'actual_generated_manifest_pin')
    manifest = json.loads(manifest_raw)
    need(manifest['schema'] == 'more-singletons-generated-manifest-v1', 'generated_manifest_schema')
    names = [x['path'] for x in manifest['files']]
    need(len(names) == 43 and len(set(names)) == 43 and
         {p.relative_to(generated).as_posix() for p in generated.rglob('*') if p.is_file()} == set(names) | {'manifest.json'},
         'exact_generated_file_closure')
    raw_files = {}
    for x in manifest['files']:
        p = (generated / x['path']).resolve()
        need(p.is_relative_to(generated), 'bounded_generated_member')
        raw = p.read_bytes()
        need(len(raw) == x['bytes'] and sha(raw) == x['sha256'], 'generated_raw_manifest_hash')
        raw_files[x['path']] = raw
    matrix = json.loads(raw_files['matrix.json']); fields = json.loads(raw_files['bitfields.json'])
    need(matrix['schema'] == 'vorbis-more-singletons-candidates-v1' and matrix['readiness_sha256'] == readiness_sha and
         [c['id'] for c in matrix['cases']] == list(IDS) and matrix['case_count'] == 8 and matrix['raw_packet_count'] == 112,
         'exact_eight_case_matrix')
    need(matrix['status'] == 'CONSTRUCTED_INDEPENDENT_WITNESS_AND_REFERENCE_PENDING' and
         matrix['pure_spectral_relations_checked'] is True and set(fields) == set(IDS), 'construction_status_and_exact_field_cases')
    need(matrix['independent_witness_executed'] is False and matrix['independent_reference_run'] is False and
         matrix['target_run'] is False and matrix['actual_nonzero_PCM_observed'] is False and
         matrix['actual_PCM_equality_verified'] is False, 'no_prior_PCM_or_target_qualification_in_matrix')
    sizes = [256 if m == 0 else 2048 for m in MODES]
    frames = [0] + [(a + b) // 4 for a, b in zip(sizes, sizes[1:])]
    granules, total = [], 0
    for n in frames:
        total += n; granules.append(total)
    transitions = Counter('SL'[a] + 'SL'[b] for a, b in zip(MODES, MODES[1:]))
    neighbors = Counter((MODES[i - 1], MODES[i + 1]) for i in range(1, 13) if MODES[i])
    need(matrix['transitions'] == dict(transitions) and
         matrix['long_neighbor_states'] == {str(k): v for k, v in sorted(neighbors.items())}, 'all_transition_and_neighbor_counts')
    checks = json.loads(raw_files['pure-checks.json'])
    need(checks['schema'] == 'more-singletons-construction-checks-v1' and checks['cases'] == 8 and checks['packets'] == 112 and
         checks['source_inputs_before'] == checks['source_inputs_after'] == manifest['source_inputs'] == source_before,
         'construction_source_closure_matches_actual')
    need(all(checks[k] is True for k in ('normal_pinned_helpers_no_rebinding', 'complete_headers_floor1_residue0_and_14_packets',
         'bitfield_byte_roundtrips', 'singleton_one_bit_both_branches_intended', 'bounded_nonzero_spectrum_is_intention_only')) and
         checks['decoder_reference_unit_SDK_compiler_QEMU_Git_or_device_executed'] is False, 'construction_scope_flags')
    observed, reports = {}, []
    for index, case in enumerate(matrix['cases']):
        name = case['id']; folder = f'cases/{name}/'
        need(set(fields[name]) == {'identification', 'comment', 'setup', 'audio'} and len(fields[name]['audio']) == 14,
             'exact_header_and_audio_field_reports')
        need(set(case['files']) == {'identification', 'comment', 'setup', 'audio', 'ogg'}, 'exact_case_payload_kinds')
        data = {}
        for kind, filename in (('identification', 'identification.bin'), ('comment', 'comment.bin'),
                               ('setup', 'setup.bin'), ('audio', 'audio.bin'), ('ogg', 'reference.ogg')):
            need(case[kind] == folder + filename, 'exact_case_raw_paths')
            raw = raw_files[case[kind]]; data[kind] = raw
            need(case['files'][kind] == dict(bytes=len(raw), sha256=sha(raw)), 'case_raw_hash_metadata')
        need(case['raw_sha256'] == {k: sha(v) for k, v in data.items() if k != 'ogg'}, 'raw_sha256_metadata')
        book, book_proof, setup_fields = parse_setup(data['setup'], name)
        compare_field_report(parse_identification(data['identification']), fields[name]['identification'])
        compare_field_report(parse_comment(data['comment']), fields[name]['comment'])
        compare_field_report(setup_fields, fields[name]['setup'])
        offsets = case['offsets']
        need(len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(data['audio']) and
             all(type(a) is int and a < b for a, b in zip(offsets, offsets[1:])), 'exact_packet_offsets')
        packets = [data['audio'][a:b] for a, b in zip(offsets, offsets[1:])]
        packet_proofs, packet_reports = [], []
        for p, raw in enumerate(packets):
            syntax, actual_fields = parse_audio(raw, book, p)
            compare_field_report(actual_fields, fields[name]['audio'][p])
            packet_proofs.append(syntax); packet_reports.append({k: v for k, v in actual_fields.items() if k != 'trace'})
        need(case['packet_syntax'] == packet_proofs, 'every_packet_metadata_syntax_and_spectrum')
        compare_audit(book, case['vector_book'], packet_proofs)
        active = singleton_id(book['lengths'])
        need(case['features'] == ['floor1', 'residue0', 'singleton_errata20150226', 'both_singleton_wire_bits',
            'map' + str(book['lookup_type']), 'dimension' + str(book['dimensions']), 'sequence_p' + str(book['sequence_p']),
            'active_original_index' + str(active)], 'exact_declared_features_from_actual_fields')
        wires = Counter(w for p in packet_proofs for ch in p['single_entry_wire_bits'] for w in ch)
        need(set(wires) == {0, 1} and sum(wires.values()) == 14 * 2 * (16 // book['dimensions']), 'both_consumed_singleton_branches')
        fixed = dict(rate=192000, channels=2, bits_per_sample=16, short=256, long=2048, mode_flags=list(MODES),
            packet_count=14, expected_raw_samples=total, expected_s16le_bytes=total * 4,
            expected_packet_samples=frames, expected_packet_frames=frames, expected_packet_pcm_bytes=[n * 4 for n in frames],
            expected_packet_s16le_bytes=[n * 4 for n in frames], packet_granules=granules,
            long_window_flags=[None if m == 0 else dict(previous=MODES[i - 1], next=MODES[i + 1]) for i, m in enumerate(MODES)])
        need({k: case[k] for k in fixed} == fixed, 'all_frame_mode_window_and_PCM_size_intentions')
        pages = carrier(data['ogg'], [data['identification'], data['comment'], data['setup']] + packets,
                        [0, 0, 0] + granules, 0x53470000 + index + 1)
        observed[name] = dict(spectra=[p['residue_vectors'] for p in packet_proofs], audio=data['audio'])
        reports.append(dict(id=name, actual_book=book, original_row_proof=book_proof, actual_packet_count=14,
            actual_used_wire_bit_counts={str(k): v for k, v in sorted(wires.items())},
            packet_consumption=packet_reports, actual_pages=pages))
    equal = [[f'map2_sparse_single_d16_seq{s}', f'map1_dense_single_d16_seq{s}', f'map1_sparse_single_d16_seq{s}'] for s in (0, 1)]
    different = [[name, name[:-1] + '1'] for name in IDS if name.endswith('0')]
    need(matrix['expected_same_decoder_pcm_equal_groups'] == equal and matrix['expected_audio_wire_equal_groups'] == equal and
         matrix['expected_same_decoder_pcm_different_pairs'] == different, 'exact_proposed_metamorphic_relations')
    for group in equal:
        need(all(observed[n]['spectra'] == observed[group[0]]['spectra'] and observed[n]['audio'] == observed[group[0]]['audio']
                 for n in group), 'independent_actual_equal_spectra_and_wires')
    for a, b in different:
        need(observed[a]['spectra'] != observed[b]['spectra'], 'independent_actual_sequence_spectrum_difference')
    need(matrix['expected_total_s16le_bytes'] == total * 4 * 8, 'total_expected_PCM_size')
    need(all((generated / n).read_bytes() == raw for n, raw in raw_files.items()) and
         (generated / 'manifest.json').read_bytes() == manifest_raw, 'all_generated_bytes_unchanged_after_witness')
    need({p.relative_to(generated).as_posix() for p in generated.rglob('*') if p.is_file()} == set(names) | {'manifest.json'},
         'generated_file_closure_unchanged_after_witness')
    source_after = check_prep(readiness_sha); need(source_before == source_after, 'all_source_inputs_unchanged_after_witness')
    return dict(schema='more-singletons-independent-witness-v1', result='FINITE_RAW_SINGLETONS_WITNESSED',
        cases=8, packets=112, Ogg_pages=136, generated_manifest_sha256=manifest_sha, readiness_sha256=readiness_sha,
        setup_all_original_rows_and_lookup_fields_checked=True, both_singleton_wire_bits_consumed=True,
        exact_metadata_fields_and_offsets_checked=True, exact_fraction_vectors_and_residue0_checked=True,
        independent_CRC_raw_packets_granules_and_flags_checked=True, spectral_equal_groups=equal,
        spectral_different_pairs=different, source_inputs_before=source_before, source_inputs_after=source_after,
        reports=reports, decoder_reference_unit_SDK_compiler_QEMU_Git_or_device_executed=False,
        actual_PCM_equality_verified=False, actual_nonzero_PCM_observed=False, target_qualified=False, full_G6_qualified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generated', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--readiness-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    need(output.is_relative_to(ROOT / '.build') and not output.is_relative_to(HERE) and
         not output.is_relative_to(args.generated.resolve()) and not output.exists(), 'fresh_separate_witness_receipt')
    result = witness(args.generated, args.manifest_sha256, args.readiness_sha256)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(result=result['result'], cases=8, packets=112, receipt_sha256=sha(output.read_bytes()),
                         reference_and_target_pending=True)))
