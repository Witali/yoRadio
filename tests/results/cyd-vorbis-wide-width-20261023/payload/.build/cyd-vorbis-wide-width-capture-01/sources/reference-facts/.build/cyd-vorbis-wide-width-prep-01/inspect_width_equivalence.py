"""Independent stdlib raw-bit/Fraction witness; never import a writer or codec."""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PINS_SHA = '75cb073a50c88b93086ebddf18a83108cdda69b46a96f3f7c1a29dadad97db96'
IDS = ('sparse_explicit_d16_seq0', 'dense_active_d16_seq0', 'sparse_explicit_d16_seq1', 'dense_active_d16_seq1')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(value):
    path = PurePosixPath(value)
    need(value and not path.is_absolute() and '..' not in path.parts and ':' not in value, 'unsafe_relative_path')
    return path.as_posix()


class Reader:
    def __init__(self, data):
        self.data, self.position = data, 0

    def take(self, width):
        need(type(width) is int and width >= 0 and self.position + width <= len(self.data) * 8, 'truncated_bitfield')
        value = 0
        for shift in range(width):
            bit = self.position + shift
            value |= ((self.data[bit // 8] >> (bit % 8)) & 1) << shift
        self.position += width
        return value


def bit_slice(data, start, end):
    return [(data[i // 8] >> (i % 8)) & 1 for i in range(start, end)]


def unpack(word):
    mantissa = word & ((1 << 21) - 1)
    if word >> 31:
        mantissa = -mantissa
    exponent = ((word >> 21) & 0x3ff) - 788
    return Fraction(mantissa) * Fraction(2) ** exponent


def read_book(r):
    start = r.position
    need(r.take(24) == 0x564342, 'codebook_sync')
    dimensions, entries, ordered = r.take(16), r.take(24), bool(r.take(1))
    need(1 <= dimensions <= 16 and 1 <= entries <= 6, 'bounded_selected_book')
    lengths = []
    if ordered:
        length = r.take(5) + 1
        while len(lengths) < entries:
            need(length <= 32, 'ordered_tree_length')
            count = r.take((entries - len(lengths)).bit_length())
            need(count <= entries - len(lengths), 'ordered_tree_count')
            lengths.extend([length] * count)
            length += 1
    else:
        sparse = r.take(1)
        for _ in range(entries):
            used = r.take(1) if sparse else 1
            lengths.append(r.take(5) + 1 if used else 0)
    need(sum((Fraction(1, 1 << length) for length in lengths if length), Fraction()) == 1,
         'complete_huffman_tree')
    lookup = r.take(4)
    result = dict(dimensions=dimensions, entries=entries, ordered=ordered, lengths=lengths, lookup_type=lookup)
    spans = dict(start=start)
    if lookup:
        need(lookup == 2, 'selected_explicit_lookup2')
        minimum_word, delta_word = r.take(32), r.take(32)
        spans['value_bits_offset'] = r.position
        width, sequence = r.take(4) + 1, r.take(1)
        spans['quant_start'] = r.position
        values = [r.take(width) for _ in range(entries * dimensions)]
        spans['quant_end'] = r.position
        result.update(minimum_word=minimum_word, delta_word=delta_word, minimum=unpack(minimum_word),
            delta=unpack(delta_word), value_bits=width, sequence_p=sequence, multiplicands=values)
    spans['end'] = r.position
    return result, spans


def setup(data):
    r = Reader(data)
    need(r.take(8) == 5 and bytes(r.take(8) for _ in range(6)) == b'vorbis' and r.take(8) == 1,
         'setup_prefix_and_two_books')
    scalar, scalar_spans = read_book(r)
    need(scalar == dict(dimensions=1, entries=2, ordered=False, lengths=[1, 1], lookup_type=0), 'unchanged_scalar_book')
    vector, spans = read_book(r)
    suffix_start = r.position
    # Public finite floor1/residue1/mapping0/two-mode suffix. These constants
    # describe wire fields and do not depend on writer field reports.
    fields = ((6, 0), (16, 0), (6, 0), (16, 1), (5, 0), (2, 0), (4, 10),
        (6, 0), (16, 1), (24, 0), (24, 16), (24, 15), (6, 1), (8, 0),
        (3, 1), (1, 0), (3, 1), (1, 0), (8, 1), (8, 1),
        (6, 0), (16, 0), (1, 0), (1, 0), (2, 0), (8, 0), (8, 0), (8, 0), (6, 1),
        (1, 0), (16, 0), (16, 0), (8, 0), (1, 1), (16, 0), (16, 0), (8, 0), (1, 1))
    for index, (width, expected) in enumerate(fields):
        need(r.take(width) == expected, 'complete_setup_suffix_field:' + str(index))
    used = r.position
    padding = len(data) * 8 - used
    need(0 <= padding < 8 and r.take(padding) == 0, 'exact_setup_zero_padding')
    return dict(book=vector, scalar=scalar, spans=spans, used_bits=used, padding_bits=padding,
        unchanged_prefix_bits=bit_slice(data, 0, spans['value_bits_offset']),
        suffix_bits=bit_slice(data, suffix_start, used))


def vectors(book):
    result = []
    for entry in range(book['entries']):
        previous, row = Fraction(), []
        for coordinate in range(book['dimensions']):
            value = (book['multiplicands'][entry * book['dimensions'] + coordinate] * book['delta'] +
                     book['minimum'] + previous)
            row.append(value)
            previous = value if book['sequence_p'] else Fraction()
        result.append(row)
    return result


def equivalent(original, changed, width):
    need(changed['value_bits'] == width and original['value_bits'] == 2 and width in (9, 16), 'expected_quant_width')
    for name in ('dimensions', 'entries', 'ordered', 'lengths', 'lookup_type', 'minimum_word', 'delta_word',
                 'minimum', 'delta', 'sequence_p', 'multiplicands'):
        need(original[name] == changed[name], 'unchanged_vector_book_field:' + name)
    need(changed['dimensions'] == 16 and changed['minimum'] == -1 and changed['delta'] == 1 and
         set(changed['multiplicands']) <= {0, 1, 2, 3}, 'finite_unsigned_multiplicand_contract')
    need(vectors(original) == vectors(changed), 'exact_fraction_vectors')


def crc(data):
    result = 0
    for byte in data:
        result ^= byte << 24
        for _ in range(8):
            result = ((result << 1) ^ (0x04c11db7 if result & 0x80000000 else 0)) & 0xffffffff
    return result


def pages(data):
    result, offset = [], 0
    while offset < len(data):
        need(data[offset:offset+5] == b'OggS\0' and len(data) - offset >= 27, 'complete_carrier_page_header')
        count = data[offset+26]
        laces = data[offset+27:offset+27+count]
        size = 27 + count + sum(laces)
        raw = data[offset:offset+size]
        need(len(laces) == count and count and laces[-1] < 255 and len(raw) == size, 'complete_one_packet_page')
        version, flags, granule, serial, sequence = struct.unpack_from('<BBQII', raw, 4)
        need(version == 0 and sequence == len(result), 'carrier_version_sequence')
        need(struct.unpack_from('<I', raw, 22)[0] == crc(raw[:22] + bytes(4) + raw[26:]), 'carrier_crc')
        result.append(dict(raw=raw, packet=raw[27+count:], flags=flags, granule=granule, serial=serial))
        offset += size
    need(offset == len(data), 'complete_carrier_bytes')
    return result


def negative_controls(original, changed):
    controls = []
    def reject(name, candidate, expected, reason):
        try:
            equivalent(original, candidate, expected)
        except ValueError as error:
            need(str(error) == reason, 'wrong_construction_control_oracle:' + name)
        else:
            raise ValueError('accepted_construction_control:' + name)
        controls.append(dict(name=name, rejected=True, exact_reason=reason,
                             in_memory_only=True, target_input_emitted=False))
    reject('wrong_expected_width', copy.deepcopy(changed), 16, 'expected_quant_width')
    for name, field, value in (('minimum_changed', 'minimum_word', original['minimum_word'] ^ 1),
                                ('delta_changed', 'delta_word', original['delta_word'] ^ 1),
                                ('sequence_changed', 'sequence_p', 1 - original['sequence_p'])):
        candidate = copy.deepcopy(changed)
        candidate[field] = value
        reject(name, candidate, 9, 'unchanged_vector_book_field:' + field)
    candidate = copy.deepcopy(changed)
    candidate['multiplicands'][0] ^= 1
    reject('quant_value_changed', candidate, 9, 'unchanged_vector_book_field:multiplicands')
    return controls


def inspect(corpus, output):
    corpus, output = corpus.resolve(), output.resolve()
    need(corpus.is_relative_to(ROOT / '.build') and corpus.is_dir() and
         output.is_relative_to(ROOT / '.build') and not output.exists() and
         not output.is_relative_to(corpus) and not output.is_relative_to(HERE), 'independent_fresh_witness_output')
    pins_raw = (HERE / 'source-pins.json').read_bytes()
    need(sha(pins_raw) == SOURCE_PINS_SHA, 'frozen_source_pins_identity')
    pins = json.loads(pins_raw)
    manifest_raw = (corpus / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    need(manifest['schema'] == 'wide-width-construction-manifest-v1' and manifest['source_pins_sha256'] == SOURCE_PINS_SHA,
         'source_bound_generated_manifest')
    declared = {relative(row['path']): row for row in manifest['files']}
    need(len(declared) == len(manifest['files']), 'unique_generated_paths')
    values = {}
    for name, row in declared.items():
        data = (corpus / name).read_bytes()
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'generated_input_identity')
        values[name] = data
    need({p.relative_to(corpus).as_posix() for p in corpus.rglob('*') if p.is_file()} == set(declared) | {'manifest.json'},
         'complete_generated_file_inventory')
    compared = json.loads(values['comparison12/matrix.json'])
    added = json.loads(values['additions8/matrix.json'])
    expected_ids = list(IDS) + [name + f'_qbits{width}' for width in (9, 16) for name in IDS]
    groups = [[name, name + '_qbits9', name + '_qbits16'] for name in IDS]
    need([row['id'] for row in compared['cases']] == expected_ids and
         [row['id'] for row in added['cases']] == expected_ids[4:] and
         compared['expected_same_decoder_pcm_equal_groups'] == groups and
         added['expected_same_decoder_pcm_equal_groups'] == [row[1:] for row in groups], 'explicit_12_and_additive_8_groups')
    by_id, observations = {}, []
    for index, case in enumerate(compared['cases']):
        name = case['id']
        original_id = IDS[index % 4]
        original = pins['selected_original_cases'][index % 4]
        width = 2 if index < 4 else 9 if index < 8 else 16
        data = {kind: values['comparison12/' + relative(case[kind])] for kind in ('identification', 'comment', 'setup', 'audio', 'ogg')}
        old = {kind: (HERE / f"originals/{original_id}/{Path(original[kind]).name}").read_bytes()
               for kind in data}
        for kind, value in old.items():
            need(len(value) == original['files'][kind]['bytes'] and sha(value) == original['files'][kind]['sha256'], 'original_raw_identity')
        for kind, value in data.items():
            need(case['files'][kind] == dict(bytes=len(value), sha256=sha(value)), 'per_case_file_identity')
            if kind not in ('setup', 'ogg'):
                need(value == old[kind], 'unchanged_ID_comment_audio:' + kind)
            if index < 4:
                need(value == old[kind], 'original_four_copied_verbatim')
            else:
                need(value == values['additions8/' + relative(added['cases'][index-4][kind])], 'additions_comparison_raw_copy')
        before, after = setup(old['setup']), setup(data['setup'])
        need(after['book']['value_bits'] == width, 'actual_quant_width')
        for field in ('dimensions', 'entries', 'ordered', 'lengths', 'lookup_type', 'minimum', 'delta',
                      'value_bits', 'sequence_p', 'multiplicands'):
            need(case['vector_book'][field] == after['book'][field], 'matrix_actual_book_field:' + field)
        need(case['raw_sha256'] == {kind: sha(value) for kind, value in data.items() if kind != 'ogg'},
             'matrix_actual_raw_hashes')
        if width != 2:
            equivalent(before['book'], after['book'], width)
        else:
            need(after == before, 'original_setup_unchanged')
        need(after['unchanged_prefix_bits'] == before['unchanged_prefix_bits'] and
             after['suffix_bits'] == before['suffix_bits'] and after['padding_bits'] == before['padding_bits'],
             'only_quant_width_and_reencoded_multiplicand_bits')
        need(after['spans']['quant_end'] - after['spans']['quant_start'] == width * after['book']['entries'] * 16,
             'all_original_rows_with_exact_quant_width')
        packet_data = [data['audio'][a:b] for a, b in zip(case['offsets'], case['offsets'][1:])]
        need(case['offsets'] == original['offsets'] and case['mode_flags'] == original['mode_flags'] and
             case['packet_count'] == len(packet_data) == 14 and case['expected_packet_frames'] == original['expected_packet_frames'] and
             case['expected_packet_pcm_bytes'] == original['expected_packet_pcm_bytes'] and
             (case['rate'], case['channels'], case['short'], case['long']) ==
             (original['rate'], original['channels'], original['short'], original['long']), 'unchanged_packet_geometry_and_metadata')
        for field in ('bits_per_sample', 'expected_raw_samples', 'expected_s16le_bytes', 'expected_packet_samples',
                      'expected_packet_s16le_bytes', 'packet_granules', 'long_window_flags'):
            need(case[field] == original[field], 'unchanged_complete_case_metadata:' + field)
        old_pages, new_pages = pages(old['ogg']), pages(data['ogg'])
        need(len(new_pages) == len(old_pages) == 3 + len(packet_data) and
             [row['packet'] for row in new_pages] == [data['identification'], data['comment'], data['setup']] + packet_data and
             [row['granule'] for row in new_pages] == [0, 0, 0] + original['packet_granules'] and
             [row['flags'] for row in new_pages] == [2] + [0] * (len(new_pages)-2) + [4], 'complete_carrier_packets_granules_flags')
        need(all(a['serial'] == b['serial'] and a['flags'] == b['flags'] and a['granule'] == b['granule'] and
                 (page == 2 or a['raw'] == b['raw']) for page, (a, b) in enumerate(zip(old_pages, new_pages))),
             'carrier_only_setup_page_changed')
        fraction_rows = [[[value.numerator, value.denominator] for value in row] for row in vectors(after['book'])]
        observations.append(dict(id=name, original_id=original_id, quant_width=width,
            original_entries=after['book']['entries'], dimensions=16,
            multiplicands=after['book']['multiplicands'], all_original_rows_retained=True,
            fraction_vectors_by_original_entry=fraction_rows, codeword_lengths=after['book']['lengths'],
            setup_span=after['spans'], setup_used_bits=after['used_bits'],
            original_setup_sha256=sha(old['setup']), setup_sha256=sha(data['setup']),
            ID_comment_audio_unchanged=True, carrier_only_setup_page_changed=True))
        by_id[name] = after['book']
    for matrix in (added, compared):
        need(matrix['case_count'] == len(matrix['cases']) and
             matrix['raw_packet_count'] == sum(row['packet_count'] for row in matrix['cases']) and
             matrix['expected_total_s16le_bytes'] == sum(row['expected_s16le_bytes'] for row in matrix['cases']), 'derived_scope_counts')
    need((added['case_count'], compared['case_count']) == (8, 12), 'scope_counts')
    controls = negative_controls(by_id[IDS[0]], by_id[IDS[0] + '_qbits9'])
    report = dict(schema='wide-width-independent-raw-witness-v1', construction_witness_completed=True,
        manifest_sha256=sha(manifest_raw), source_pins_sha256=SOURCE_PINS_SHA,
        cases=observations, additions=added['case_count'], comparison=compared['case_count'],
        expected_three_width_equality_groups=groups, all_original_quant_rows_and_fraction_vectors_equal=True,
        exact_construction_negative_controls=controls, writer_or_codec_imported=False,
        actual_PCM_read_or_compared=False, independent_codec_reference_run=False, target_run=False,
        numeric_qualified=False, format_conformance_qualified=False, full_G6_qualified=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(witness_completed=True, additions=8, comparison=12, output=str(output), numeric_qualified=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    inspect(args.corpus, args.output)
