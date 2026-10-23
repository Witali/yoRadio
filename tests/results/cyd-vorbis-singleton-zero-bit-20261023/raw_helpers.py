"""Exact pure functions from reviewed original8 witness; filesystem startup omitted."""
from collections import Counter
from fractions import Fraction
import hashlib
import re
import struct

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
