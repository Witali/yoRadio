"""Add four all-zero singleton-wire controls; preserve four original map1 cases."""
import argparse
import copy
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from support import HERE, IDS, MANIFEST_SHA, MATRIX_SHA, HOST_REPORT_SHA, need, sha, load, originals, source_closure, fresh_output

prior = load('zero_control_pinned_generator', 'generate_singletons.py',
             'e45d936eae0297ed9e169d5966e6c505ae281d15c232fc3a9a63b582c5627762')


def zero_packet(raw, report, packet, original_id):
    mode = prior.MODES[packet]
    fields = copy.deepcopy(report)
    tokens = [f for f in fields['fields'] if re.fullmatch(r'residue\[[01]\]\.entry\[0\]=[04]', f['name'])]
    need(len(tokens) == 2 and [f['name'].split(']')[0] for f in tokens] == ['residue[0', 'residue[1'], 'two_original_singleton_fields')
    data = bytearray(raw); changed = []
    for channel, f in enumerate(tokens):
        need(f['width'] == 1 and f['offset'] == 38 + 2 * mode + channel and f['value'] == (packet + channel) % 2,
             'actual_original_token_field_shape')
        position = f['offset']; need(position < len(raw) * 8, 'bounded_original_token_offset')
        need((raw[position // 8] >> (position % 8)) & 1 == f['value'], 'actual_original_token_value')
        if f['value']:
            data[position // 8] &= ~(1 << (position % 8)); changed.append(position)
        f['value'] = 0
    need(report['bytes'] == len(raw) and report['used_bits'] == 40 + 2 * mode and report['padding_bits'] == (-report['used_bits']) % 8,
         'unchanged_packet_lengths_and_padding')
    return bytes(data), fields, dict(packet=packet, original_id=original_id, changed_bit_offsets=changed, consumed_zero_tokens=2)


def build_case(case, field_reports, payloads):
    old = case['id']; new = old + '_wire0'; copied = copy.deepcopy(case); fields = copy.deepcopy(field_reports[old])
    audio = payloads[case['audio']]; offsets = case['offsets']; packets, changes = [], []
    need(len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(audio), 'original_audio_offsets')
    for p, (a, b) in enumerate(zip(offsets, offsets[1:])):
        raw, report, edit = zero_packet(audio[a:b], fields['audio'][p], p, old)
        packets.append(raw); fields['audio'][p] = report; changes.append(edit)
        copied['packet_syntax'][p]['single_entry_wire_bits'] = [[0], [0]]
    data = {k: payloads[case[k]] for k in ('identification', 'comment', 'setup')}
    data['audio'] = b''.join(packets)
    pages = prior.base.read_pages(payloads[case['ogg']]); full = [data['identification'], data['comment'], data['setup']] + packets
    need(len(pages) == 17, 'original_seventeen_page_carrier')
    data['ogg'] = b''.join(prior.base.page(raw, p['serial'], i, p['granule'], p['flags']) for i, (p, raw) in enumerate(zip(pages, full)))
    copied['id'] = new; copied['wire_zero_control_for'] = old; copied['features'].append('preferred_zero_singleton_tokens')
    for k in ('identification', 'comment', 'setup', 'audio', 'ogg'):
        copied[k] = f'cases/{new}/' + ('reference.ogg' if k == 'ogg' else k + '.bin')
    copied['files'] = {k: dict(bytes=len(raw), sha256=sha(raw)) for k, raw in data.items()}
    copied['raw_sha256'] = {k: sha(raw) for k, raw in data.items() if k != 'ogg'}
    need(sum(len(x['changed_bit_offsets']) for x in changes) == 14, 'exact_fourteen_one_bits_cleared_per_case')
    return copied, fields, {copied[k]: raw for k, raw in data.items()}, changes


def generate(output, readiness):
    before = source_closure(readiness); output = fresh_output(output)
    cases, old_fields, payloads = originals(); cases = copy.deepcopy(cases)
    fields = {c['id']: copy.deepcopy(old_fields[c['id']]) for c in cases}
    edits, pairs, new_cases = {}, [], []
    for case in cases:
        new, report, new_payloads, changes = build_case(case, old_fields, payloads)
        new_cases.append(new); fields[new['id']] = report; payloads.update(new_payloads)
        edits[new['id']] = changes; pairs.append([case['id'], new['id']])
    cases += new_cases
    after = source_closure(readiness); need(before == after, 'all_original_and_source_bytes_unchanged')
    matrix = dict(schema='vorbis-singleton-zero-bit-comparison-v1', status='CONSTRUCTED_INDEPENDENT_WITNESS_AND_REFERENCE_PENDING',
        cases=cases, case_count=8, raw_packet_count=112, expected_total_s16le_bytes=sum(c['expected_s16le_bytes'] for c in cases),
        expected_same_decoder_pcm_equal_groups=pairs, expected_Xiph_PCM_equal_pairs=pairs,
        expected_same_decoder_pcm_different_pairs=[], original_generation_manifest_sha256=MANIFEST_SHA,
        original_generation_matrix_sha256=MATRIX_SHA, original_host_NONPASS_report_sha256=HOST_REPORT_SHA,
        readiness_sha256=readiness, independent_reference_run=False, independent_witness_executed=False,
        actual_PCM_equality_verified=False, actual_nonzero_PCM_observed=False, target_run=False,
        native_outcome_or_cause_assumed=False, original_both_bit_tolerance_cases_replaced=False)
    checks = dict(schema='singleton-zero-bit-construction-v1', source_inputs_before=before, source_inputs_after=after,
        original_cases_copied_byteexact=4, additive_zero_cases=4, new_zero_token_count=112,
        comparison_token_count=224, changed_original_one_bits=56, changes=edits,
        normal_pinned_page_helper_no_rebinding=True, decoder_reference_unit_SDK_compiler_QEMU_Git_executed=False)
    for name, value in (('matrix.json', matrix), ('bitfields.json', fields), ('construction.json', checks)):
        payloads[name] = (json.dumps(value, indent=2) + '\n').encode()
    manifest = dict(schema='singleton-zero-bit-generated-manifest-v1', source_inputs=before,
        files=[dict(path=n, bytes=len(raw), sha256=sha(raw)) for n, raw in sorted(payloads.items())])
    payloads['manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in payloads.items():
        p = output / name; p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as stream:
            stream.write(raw)
    print(json.dumps(dict(result='ZERO_BIT_COMPARISON_CONSTRUCTED_REFERENCE_PENDING', cases=8, additive_cases=4,
        manifest_sha256=sha(payloads['manifest.json']), native_outcome_unknown=True)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True); parser.add_argument('--readiness-sha256', required=True)
    args = parser.parse_args(); generate(args.output, args.readiness_sha256)
