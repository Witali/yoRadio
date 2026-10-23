"""Strict prospective owned-parser unit protocol; no SDK/process execution."""
import hashlib
import json
from pathlib import Path
import re

PREFIX = 'CYD_VORBIS_OWNED_BOOK_'
SETUP = '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
ABI = 'e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60'
IDS = ('ordered_lattice_d2_seq0', 'unordered_lattice_d2_seq0', 'sparse_lattice_d2_seq0',
       'ordered_lattice_d2_seq1', 'ordered_explicit_d2_seq0', 'unordered_explicit_d2_seq1',
       'sparse_explicit_d4_seq0', 'sparse_explicit_d4_seq1', 'sparse_explicit_d16_seq0',
       'dense_active_d16_seq0', 'sparse_explicit_d16_seq1', 'dense_active_d16_seq1',
       'single_explicit_d2_seq0', 'dense_twin_d2_seq0', 'single_explicit_d2_seq1', 'dense_twin_d2_seq1')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def contract_shape(value):
    model = value['model']
    need(value['contract_sha256'] == digest(json.dumps(model, sort_keys=True, separators=(',', ':')).encode()), 'contract_model_identity')
    need(model['schema'] == 'owned-book-unit-fixtures-v1' and model['case_count'] == len(model['cases']) == 16 and
         model['probe_count'] == sum(len(c['probes']) for c in model['cases']) == 61 and model['point'] == 0,
         'exact_original16_unit_shape')
    need(model['setup_sha256'] == SETUP and model['ABI_sha256'] == ABI and
         tuple(c['id'] for c in model['cases']) == IDS and model['wide_pairs'] == [[8, 9], [10, 11]], 'reviewed_source_and_cases')


def load_contract(path, *, expected_sha256):
    need(re.fullmatch('[0-9a-f]{64}', expected_sha256) is not None, 'independent_contract_file_hash_required')
    data = Path(path).read_bytes()
    need(digest(data) == expected_sha256, 'contract_file_identity')
    value = json.loads(data)
    contract_shape(value)
    return value


def validate_log(log, contract, *, returncode, timed_out, interrupted):
    contract_shape(contract)
    need(type(returncode) is int and returncode == 0 and timed_out is False and interrupted is False,
         'actual_terminal0_without_timeout_or_interruption_required')
    need(type(log) is str, 'text_log_required')
    need(not re.search(r'Guru Meditation|CORRUPT\s*HEAP|assert failed|abort\(\)|Brownout|Rebooting', log, re.I),
         'target_panic_or_reset')
    lines = []
    for line in log.replace('\r\n', '\n').splitlines():
        if PREFIX not in line:
            continue
        need(line.startswith(PREFIX), 'native_prefix_only')
        token, separator, rest = line[len(PREFIX):].partition(' ')
        need(separator and token != 'FAILURE', 'explicit_unit_failure_or_malformed_line')
        parts = rest.split(' ')
        need(all(re.fullmatch('[a-z_]+=[^\s=]+', part) for part in parts), 'strict_key_value_tokens')
        fields = dict(part.split('=', 1) for part in parts)
        need(len(fields) == len(parts), 'duplicate_fields')
        lines.append((token, fields))
    need(len(lines) == 97, 'all97_protocol_events_required')
    cursor = 0
    def event(kind, expected, extra=()):
        nonlocal cursor
        observed_kind, fields = lines[cursor]
        cursor += 1
        need(observed_kind == kind and set(fields) == set(expected) | set(extra), 'event_order_or_fields:' + kind)
        need(all(fields[key] == str(value) for key, value in expected.items()), 'event_value:' + kind)
        return fields
    model = contract['model']
    need(model['case_count'] == 16 and model['probe_count'] == 61 and tuple(c['id'] for c in model['cases']) == IDS,
         'complete_named_contract')
    event('BEGIN', dict(contract=contract['contract_sha256'], cases=16, probes=61, core=0))
    actual_fields, actual_vectors = {}, {}
    for index, case in enumerate(model['cases']):
        expected = dict(case=index, id=case['id'], dim=case['dim'], entries=case['entries'], used=case['used_entries'],
            maxlen=case['max_length'], nodeb=case['node_bytes'], leafw=case['leaf_words'], type=case['dec_type'],
            q_min=case['q_min'], q_minp=case['q_minp'], q_del=case['q_del'], q_delp=case['q_delp'], seq=case['sequence'],
            q_bits=case['q_bits'], q_pack=case['q_pack'], table_bytes=case['table_bytes'], qval_bytes=case['qval_bytes'],
            core=0, qval=case['qval_hex'] if case['qval_bytes'] else '-')
        fields = event('FIELDS', expected, ('table',))
        need(re.fullmatch('[0-9a-f]+', fields['table']) and len(fields['table']) == 2 * case['table_bytes'], 'actual_complete_table_bytes')
        if 8 <= index < 12:
            need(fields['table'] == '800181028283', 'wide_exact_public_table')
        actual_fields[index] = fields
        vectors = []
        for pi, probe in enumerate(case['probes']):
            values = ','.join(str(n) for n in probe['expected'])
            actual = event('VECTOR', dict(case=index, probe=pi, original=probe['original'], wire=probe['wire'],
                bits=probe['bits'], leaf=probe['leaf'], consumed=probe['bits'], core=0, values=values))
            vectors.append(actual['values'])
        actual_vectors[index] = vectors
        event('CASE', dict(case=index, id=case['id'], probes=len(case['probes']),
            parser_bits=case['book_end_bit'] - case['book_first_bit'], live=0, core=0))
    for seq, (first, second) in enumerate(model['wide_pairs']):
        need(actual_fields[first]['qval'] == actual_fields[second]['qval'] and
             actual_fields[first]['table'] == actual_fields[second]['table'] and
             actual_vectors[first] == actual_vectors[second], 'actual_wide_sparse_dense_equality')
        event('PAIR', dict(first=first, second=second, seq=seq, qval_equal=1, table_equal=1, vectors_equal=1, core=0))
    event('COMPLETE', dict(cases=16, probes=61, live=0, pairs=2, core=0))
    need(cursor == len(lines), 'no_trailing_protocol')
    return dict(schema='owned-book-unit-observed-v1', cases=16, active_codewords=59, vector_probes=61, wide_pairs=2,
        protocol_lines=97, actual_returncode=returncode, actual_timed_out=timed_out, actual_interrupted=interrupted,
        owned_parser_public_vector_qualified=True, vendor_backend_qualified=False, PCM_qualified=False,
        full_G6_qualified=False, physical_qualified=False)
