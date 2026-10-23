"""Bind all21 unchanged mono/mapping inputs to the one actual dual-reference run."""
import hashlib
import json
from pathlib import Path
import struct

import recorded_qualification as recorded

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def fact(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def derive(contract, mapping):
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    facts, external = {}, {}

    def observed(path, expected=None, size=None):
        row = fact(path)
        need(expected is None or row['sha256'] == expected, 'reference_SHA')
        need(size is None or row['bytes'] == size, 'reference_size')
        (facts if Path(row['path']).is_relative_to(ROOT) else external)[row['path']] = row
        return row

    refs = pins['reference']
    for row in refs.values():
        observed(ROOT / row['path'], row['sha256'], row['bytes'])
    need(Path(recorded.__file__).resolve() == HERE / 'recorded_qualification.py' and
         fact(HERE / 'recorded_qualification.py')['sha256'] == pins['qualifier_sha256'] and
         fact(HERE / 'carrier.py')['sha256'] == pins['carrier_sha256'], 'unchanged_recorded_qualification_helpers')
    q = json.loads((ROOT / refs['qualification']['path']).read_bytes())
    host = json.loads((ROOT / refs['host']['path']).read_bytes())
    outer = json.loads((ROOT / refs['host_outer']['path']).read_bytes())
    qterminal = json.loads((ROOT / refs['qualification_terminal']['path']).read_bytes())
    recorded.terminal(outer, 0)
    recorded.terminal(qterminal, 0)
    need(qterminal['runner_sha256'] == outer['runner_sha256'] == pins['command_wrapper_sha256'],
         'actual_reference_wrapper_identity')
    need(q['schema'] == 'public-vorbis-new-format-reference-qualification-v1' and q['profile'] == 'mono21' and
         q['result'] == 'DUAL_REFERENCE_QUALIFIED' and
         all(q[k] is True for k in ('completed', 'reference_corpus_qualified', 'xiph_reference_qualified',
                                   'dual_reference_qualified', 'original_dual_reference_passed')) and
         all(q[k] is False for k in ('target_executed', 'production_changed', 'standard_conformance_qualified',
                                    'full_G6_qualified', 'physical_device')) and
         (q['xiph_cases'], q['native_compared'], q['native_lookup2_refusals'], q['paired_raw_packets'], q['expected_pcm_bytes']) ==
         (21, 21, 0, 294, 464640), 'actual_complete21_dual_reference_qualification')
    need(q['original_report_sha256'] == refs['host']['sha256'] and
         q['original_outer_receipt_sha256'] == refs['host_outer']['sha256'] and
         host['completed'] is host['xiph_reference_qualified'] is host['dual_reference_qualified'] is True and
         host['target_executed'] is host['production_changed'] is False and
         len(host['cases']) == 21 and len(host['commands']) == 42 and host['failures'] == [] and
         host['metamorphic_checks'] == q['xiph_metamorphic_checks'] == q['original_metamorphic_checks'] == [] and
         q['policy'] == dict(max_abs_error=2, predeclared=True, purpose='bounded-reference-crosscheck-not-standard-conformance'),
         'single_actual21_campaign_scope_and_predeclared_policy')
    for item in q['validated_inputs'].values():
        observed(item['path'], item['sha256'], item['bytes'])
    for receipt in (outer, qterminal):
        for path, row in receipt['logs'].items():
            observed(path, row['sha256'], row['bytes'])
    need(q['validated_inputs']['qualifier/script']['sha256'] == pins['qualifier_sha256'] and
         q['validated_inputs']['qualifier/pins']['sha256'] == pins['qualifier_pins_sha256'], 'actual_qualifier_source_identity')
    matrix_raw = (ROOT / refs['comparison']['path']).read_bytes()
    need(matrix_raw == (ROOT / refs['host_matrix']['path']).read_bytes(), 'canonical_matrix_identical_to_actual_reference_origin')
    matrix = json.loads(matrix_raw)
    model = contract['model']
    need(len(model['cases']) == len(mapping['cases']) == len(matrix['cases']) == 21 and
         [row['id'] for row in model['cases']] == pins['expected_case_ids'] and
         (model['total_packets'], model['total_pcm'], model['case_mask']) == (294, 464640, (1 << 21) - 1),
         'complete21_original_order_and_totals')
    host_root = (ROOT / refs['host']['path']).parent
    rows = []
    for index, (case, origin, source) in enumerate(zip(model['cases'], mapping['cases'], matrix['cases'])):
        need(origin['case'] == index and case['id'] == origin['id'] == source['id'] and
             source == origin['original_case_fields'] == origin['selected_case_fields'] and origin['fields_changed'] == [],
             'unchanged_original21_case_fields')
        rid = '0-' + case['id']
        raw = [row for row in host['cases'] if row['id'] == rid]
        qualified = [row for row in q['cases'] if row['id'] == rid]
        need(len(raw) == len(qualified) == 1, 'unique_actual_reference_case')
        raw, qualified = raw[0], qualified[0]
        need(raw['input'] == source and raw['source_matrix_sha256'] == refs['host_matrix']['sha256'] and
             Path(raw['source_matrix']).resolve() == (ROOT / refs['host_matrix']['path']).resolve() and
             qualified['xiph_qualified'] is qualified['native_compared'] is True and
             qualified['native_lookup2_refusal'] is False and raw['failures'] == [] and
             qualified['frames'] == case['frames'][1:] and qualified['pcm_bytes'] == case['total_pcm'] and
             (qualified['rate'], qualified['channels'], qualified['bits']) == (case['rate'], case['channels'], 16),
             'actual_reference_raw_metadata_frame_binding')
        decoded, pcms = {}, {}
        for decoder in ('vorbis', 'libvorbis'):
            receipt_path = host_root / 'cases' / rid / ('decode-' + decoder + '.json')
            receipt = json.loads(receipt_path.read_bytes())
            recorded.terminal(receipt, 0)
            role = 'receipt/cases/' + rid + '/decode-' + decoder
            need(fact(receipt_path) == q['validated_inputs'][role], 'actual_child_receipt_binding')
            wav_path = host_root / 'cases' / rid / (decoder + '.wav')
            md5_path = host_root / 'cases' / rid / ('decode-' + decoder + '.stdout.log')
            need(fact(wav_path) == q['validated_inputs']['wav/' + rid + '/' + decoder] and
                 fact(md5_path) == q['validated_inputs']['log/cases/' + rid + '/decode-' + decoder + '/decode-' + decoder + '.stdout.log'],
                 'actual_full_WAV_framemd5_identity')
            pcm, details = recorded.decoded_pcm(wav_path.read_bytes(), md5_path.read_bytes(),
                case['rate'], case['channels'], case['frames'], case['modes'])
            need(details == raw['decoded'][decoder] and len(pcm) == case['total_pcm'], 'complete_recorded42_PCM_replay')
            pcms[decoder], decoded[decoder] = pcm, details
        need(len(pcms['vorbis']) == len(pcms['libvorbis']) == case['total_pcm'], 'no_truncated_reference_crosscheck')
        pairs = zip(struct.iter_unpack('<h', pcms['vorbis']), struct.iter_unpack('<h', pcms['libvorbis']))
        maximum = max(abs(a[0] - b[0]) for a, b in pairs)
        need(maximum == raw['cross_reference_max_abs_error'] == qualified['cross_reference_max_abs_error'] and maximum <= 2,
             'actual_complete_dual_reference_error_bound2')
        need({k: v for k, v in qualified.items() if k not in ('id', 'xiph_qualified', 'native_compared',
             'native_lookup2_refusal', 'cross_reference_max_abs_error')} == decoded['libvorbis'], 'qualification_full_Xiph_metadata')
        for kind, pair in origin['files'].items():
            for role in ('original', 'selected'):
                item = pair[role]
                observed(item['path'], item['sha256'], item['bytes'])
            need(pair['original']['sha256'] == pair['selected']['sha256'], 'selected_raw_bytes_unchanged')
        need(case['raw_sha256'] == {kind: origin['files'][kind]['original']['sha256']
                                   for kind in ('identification', 'setup', 'audio')}, 'model_raw_SHA_binding')
        rows.append(dict(case=index, id=case['id'], original_group='mono21', original_reference_id=rid,
            qualification_sha256=refs['qualification']['sha256'], original_host_report_sha256=refs['host']['sha256'],
            original_host_receipt_sha256=refs['host_outer']['sha256'], original_host_returncode=0,
            raw_sha256=case['raw_sha256'], frames=case['frames'], pcm_bytes=case['total_pcm'],
            rate=case['rate'], channels=case['channels'], reference_pcm_sha256=qualified['pcm_sha256'],
            reference_wav_sha256=qualified['wav_sha256'], actual_reference_decoders=decoded,
            cross_reference_max_abs_error=maximum, native_compared=True, native_lookup2_refusal=False,
            xiph_qualified_existing=True))
    for item in list(facts.values()) + list(external.values()):
        need(fact(item['path']) == item, 'reference_fact_changed')
    return dict(schema='mono21-recorded-dual-reference-binding-v1', completed=True,
        contract_sha256=contract['contract_sha256'], cases=rows,
        source_scopes=[dict(name='actual_mono21', qualification_path=refs['qualification']['path'],
            qualification_sha256=refs['qualification']['sha256'], host_path=refs['host']['path'],
            host_sha256=refs['host']['sha256'], receipt_path=refs['host_outer']['path'],
            receipt_sha256=refs['host_outer']['sha256'], original_returncode=0, totals=[21, 21, 0, 294, 464640])],
        proof_facts=sorted(facts.values(), key=lambda row: row['path']), external_reference_tool_identities=list(external.values()),
        native_lookup2_refusals=0, new_reference_commands_executed=False,
        aggregate_reference_campaign_exists=False, actual_single_scope_reference_campaign_exists=True,
        dual_reference_passed=True, dual_reference_scope='only-existing-mono21-campaign',
        previous_unrelated_dual_NONPASS_reinterpreted=False,
        target_executed=False, target_numeric_comparison_performed=False, full_G6_qualified=False)


def verify(contract, mapping, binding):
    need(derive(contract, mapping) == binding, 'recorded_reference_binding_changed')
    return binding
