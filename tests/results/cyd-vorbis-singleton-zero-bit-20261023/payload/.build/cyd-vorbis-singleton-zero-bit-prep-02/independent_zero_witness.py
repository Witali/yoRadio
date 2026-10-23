"""Independent preferred-zero wire witness; no new-generator imports or PCM claims."""
import argparse
import copy
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from support import HERE, IDS, MANIFEST_SHA, MATRIX_SHA, HOST_REPORT_SHA, need, sha, load, originals, source_closure, fresh_output

prior = load('zero_control_independent_prior_witness', 'independent_witness.py',
             '1e5095929f19f68b627bc51fee369943e13f7e9bc5069ff817a6865cf39ee6ef')


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


def witness(generated, manifest_sha, readiness):
    before = source_closure(readiness); old_cases, old_fields, original_raw = originals()
    generated = generated.resolve()
    need(generated.is_relative_to(HERE.parent) and not generated.is_relative_to(HERE), 'bounded_comparison_root')
    raw_manifest = (generated / 'manifest.json').read_bytes(); need(sha(raw_manifest) == manifest_sha, 'comparison_manifest_pin')
    manifest = json.loads(raw_manifest)
    need(manifest['schema'] == 'singleton-zero-bit-generated-manifest-v1' and manifest['source_inputs'] == before, 'comparison_source_manifest')
    names = [x['path'] for x in manifest['files']]
    need(len(names) == len(set(names)) == 43 and
         {p.relative_to(generated).as_posix() for p in generated.rglob('*') if p.is_file()} == set(names) | {'manifest.json'},
         'complete_comparison_file_set')
    raw_files = {}
    for x in manifest['files']:
        p = (generated / x['path']).resolve(); need(p.is_relative_to(generated), 'bounded_comparison_member')
        raw = p.read_bytes(); need(len(raw) == x['bytes'] and sha(raw) == x['sha256'], 'comparison_raw_manifest_identity')
        raw_files[x['path']] = raw
    matrix = json.loads(raw_files['matrix.json']); fields = json.loads(raw_files['bitfields.json'])
    validate_matrix_status(matrix)
    need(matrix['schema'] == 'vorbis-singleton-zero-bit-comparison-v1' and matrix['case_count'] == 8 and matrix['raw_packet_count'] == 112
         and [c['id'] for c in matrix['cases']] == list(IDS) + [n + '_wire0' for n in IDS], 'exact_eight_comparison_cases')
    pairs = [[n, n + '_wire0'] for n in IDS]
    need(matrix['expected_Xiph_PCM_equal_pairs'] == matrix['expected_same_decoder_pcm_equal_groups'] == pairs and
         matrix['expected_same_decoder_pcm_different_pairs'] == [], 'four_proposed_PCM_equal_pairs')
    need(matrix['readiness_sha256'] == readiness and matrix['original_generation_manifest_sha256'] == MANIFEST_SHA and
         matrix['original_generation_matrix_sha256'] == MATRIX_SHA and matrix['original_host_NONPASS_report_sha256'] == HOST_REPORT_SHA,
         'original_history_pins')
    need(all(matrix[k] is False for k in ('independent_reference_run', 'independent_witness_executed', 'actual_PCM_equality_verified',
         'actual_nonzero_PCM_observed', 'target_run', 'native_outcome_or_cause_assumed', 'original_both_bit_tolerance_cases_replaced')),
         'no_assumed_native_target_or_PCM_outcome')
    need(set(fields) == set(IDS) | {n + '_wire0' for n in IDS}, 'exact_eight_bitfield_cases')
    reports, all_changes = [], {}
    for index, original in enumerate(old_cases):
        old, new = matrix['cases'][index], matrix['cases'][index + 4]
        name = original['id']; new_name = name + '_wire0'
        validate_field_report_keys(fields[new_name], fields[name])
        need(old == original and fields[name] == old_fields[name], 'all_original_case_metadata_unchanged')
        old_data, new_data = {}, {}
        for k in ('identification', 'comment', 'setup', 'audio', 'ogg'):
            need(raw_files[old[k]] == original_raw[original[k]], 'all_original_raw_case_bytes_unchanged')
            need(new[k] == f'cases/{new_name}/' + ('reference.ogg' if k == 'ogg' else k + '.bin'), 'new_control_raw_paths')
            old_data[k], new_data[k] = raw_files[old[k]], raw_files[new[k]]
            if k in ('identification', 'comment', 'setup'):
                need(old_data[k] == new_data[k], 'identification_comment_setup_byteequal')
        book, book_evidence, setup_report = prior.parse_setup(old_data['setup'], name)
        prior.compare_field_report(setup_report, fields[name]['setup'])
        prior.compare_field_report(prior.parse_identification(old_data['identification']), fields[name]['identification'])
        prior.compare_field_report(prior.parse_comment(old_data['comment']), fields[name]['comment'])
        need({k: fields[new_name][k] for k in ('identification', 'comment', 'setup')} ==
             {k: fields[name][k] for k in ('identification', 'comment', 'setup')}, 'all_header_field_reports_identical')
        offsets = original['offsets']
        need(len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(old_data['audio']) == len(new_data['audio'])
             and new['offsets'] == offsets, 'all_audio_offsets_lengths_unchanged')
        old_packets = [old_data['audio'][a:b] for a, b in zip(offsets, offsets[1:])]
        new_packets = [new_data['audio'][a:b] for a, b in zip(offsets, offsets[1:])]
        new_syntax, old_syntax, edits = [], [], []
        need(len(fields[new_name]['audio']) == 14, 'fourteen_zero_audio_field_reports')
        for packet, (a, b) in enumerate(zip(old_packets, new_packets)):
            prior_syntax, prior_fields = prior.parse_audio(a, book, packet)  # Original alternating policy only.
            zero_syntax, zero_fields, positions = parse_zero_audio(b, book, packet)
            prior.compare_field_report(prior_fields, fields[name]['audio'][packet])
            prior.compare_field_report(zero_fields, fields[new_name]['audio'][packet])
            need(fields[new_name]['audio'][packet] == zero_field_report(fields[name]['audio'][packet], positions),
                 'all_non_token_field_metadata_identical')
            expected_syntax = copy.deepcopy(prior_syntax); expected_syntax['single_entry_wire_bits'] = [[0], [0]]
            need(zero_syntax == expected_syntax, 'all_spectra_original_indices_classwords_and_consumption_identical')
            changed = unchanged_except_tokens(a, b, positions)
            edits.append(dict(packet=packet, original_id=name, changed_bit_offsets=changed, consumed_zero_tokens=2))
            new_syntax.append(zero_syntax); old_syntax.append(prior_syntax)
        need(old['packet_syntax'] == old_syntax, 'all_original_packet_metadata_matches_actual')
        prior.compare_audit(book, old['vector_book'], old_syntax)
        expected = copy.deepcopy(original); expected['id'] = new_name; expected['wire_zero_control_for'] = name
        need(expected['features'].count('both_singleton_wire_bits') == 1, 'exact_original_both_bit_feature')
        expected['features'] = ['singleton_wire_bits_all_zero' if f == 'both_singleton_wire_bits' else f for f in expected['features']]
        expected['features'].append('preferred_zero_singleton_tokens'); expected['packet_syntax'] = new_syntax
        for k in old_data:
            expected[k] = f'cases/{new_name}/' + ('reference.ogg' if k == 'ogg' else k + '.bin')
        expected['files'] = {k: dict(bytes=len(raw), sha256=sha(raw)) for k, raw in new_data.items()}
        expected['raw_sha256'] = {k: sha(raw) for k, raw in new_data.items() if k != 'ogg'}
        need(new == expected, 'exact_new_case_metadata_only_allowed_changes')
        granules = [0, 0, 0] + original['packet_granules']; serial = 0x53470000 + index + 5
        old_pages = prior.carrier(old_data['ogg'], [old_data[k] for k in ('identification', 'comment', 'setup')] + old_packets, granules, serial)
        new_pages = prior.carrier(new_data['ogg'], [new_data[k] for k in ('identification', 'comment', 'setup')] + new_packets, granules, serial)
        need(all({k: page[k] for k in page if k != 'checksum'} == {k: other[k] for k in other if k != 'checksum'}
                 for page, other in zip(old_pages, new_pages)), 'all_carrier_fields_except_necessary_CRC_unchanged')
        for a, b in zip(old_pages, new_pages):
            old_start, new_start = a['offset'], b['offset']
            old_header = bytearray(old_data['ogg'][old_start:old_start + 27 + old_data['ogg'][old_start + 26]])
            new_header = bytearray(new_data['ogg'][new_start:new_start + 27 + new_data['ogg'][new_start + 26]])
            old_header[22:26] = new_header[22:26] = b'\0' * 4
            need(old_header == new_header, 'all_raw_carrier_header_and_lacing_bytes_except_CRC_unchanged')
        reports.append(dict(original_id=name, zero_id=new_name, original_row_proof=book_evidence,
            zero_tokens=28, comparison_tokens=56, cleared_one_bits=14, changes=edits,
            original_pages=old_pages, zero_pages=new_pages, actual_spectra_equal=True, actual_PCM_equality_verified=False))
        all_changes[new_name] = edits
    checks = json.loads(raw_files['construction.json'])
    need(checks['schema'] == 'singleton-zero-bit-construction-v1' and
         checks['source_inputs_before'] == checks['source_inputs_after'] == before and checks['changes'] == all_changes and
         checks['original_cases_copied_byteexact'] == checks['additive_zero_cases'] == 4 and
         checks['new_zero_token_count'] == 112 and checks['comparison_token_count'] == 224 and checks['changed_original_one_bits'] == 56 and
         checks['normal_pinned_page_helper_no_rebinding'] is True and checks['decoder_reference_unit_SDK_compiler_QEMU_Git_executed'] is False,
         'exact_actual_edit_accounting_and_construction_scope')
    need(matrix['expected_total_s16le_bytes'] == sum(c['expected_s16le_bytes'] for c in matrix['cases']), 'expected_PCM_size_metadata')
    need(all((generated / n).read_bytes() == raw for n, raw in raw_files.items()) and
         (generated / 'manifest.json').read_bytes() == raw_manifest and
         {p.relative_to(generated).as_posix() for p in generated.rglob('*') if p.is_file()} == set(names) | {'manifest.json'},
         'all_comparison_bytes_and_file_set_unchanged')
    after = source_closure(readiness); need(before == after, 'all_sources_original_cases_and_failure_history_unchanged')
    return dict(schema='singleton-zero-bit-independent-witness-v1', result='FINITE_ZERO_BIT_COMPARISON_WITNESSED',
        cases=8, old_map1_cases=4, new_zero_cases=4, audio_packets=112, zero_tokens=112, comparison_tokens=224,
        cleared_original_one_bits=56, actual_spectral_equal_pairs=pairs, expected_Xiph_PCM_equal_pairs=pairs,
        all_non_token_bits_fields_offsets_and_padding_unchanged=True, independent_CRC_and_full_carrier_fields_checked=True,
        source_inputs_before=before, source_inputs_after=after, reports=reports,
        generated_manifest_sha256=manifest_sha, readiness_sha256=readiness,
        actual_PCM_equality_verified=False, actual_nonzero_PCM_observed=False, native_outcome_or_cause_assumed=False,
        original_both_bit_tolerance_cases_replaced=False, decoder_reference_unit_SDK_compiler_QEMU_Git_executed=False,
        target_qualified=False, full_G6_qualified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generated', type=Path, required=True); parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--readiness-sha256', required=True); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); output = fresh_output(args.output)
    need(not output.is_relative_to(args.generated.resolve()), 'witness_receipt_separate_from_corpus')
    result = witness(args.generated, args.manifest_sha256, args.readiness_sha256)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps(dict(result=result['result'], cases=8, zero_tokens=112, receipt_sha256=sha(output.read_bytes()),
                         reference_and_native_outcome_pending=True)))
