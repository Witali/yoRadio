"""Bind exact8 selected raw cases to actual qualified Xiph records; no decoder."""
import hashlib
import json
from pathlib import Path

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
        need(expected is None or row['sha256'] == expected, 'reference_fact_SHA')
        need(size is None or row['bytes'] == size, 'reference_fact_size')
        (facts if Path(row['path']).is_relative_to(ROOT) else external)[row['path']] = row
        return row
    refs = pins['reference']
    for row in refs.values():
        observed(ROOT / row['path'], row['sha256'], row['bytes'])
    q = json.loads((ROOT / refs['qualification']['path']).read_bytes())
    host = json.loads((ROOT / refs['host']['path']).read_bytes())
    outer = json.loads((ROOT / refs['host_outer']['path']).read_bytes())
    qterminal = json.loads((ROOT / refs['qualification_terminal']['path']).read_bytes())
    witness = json.loads((ROOT / refs['witness']['path']).read_bytes())
    need(witness['result'] == 'FINITE_RAW_SINGLETONS_WITNESSED' and witness['cases'] == 8 and witness['packets'] == 112
         and witness['Ogg_pages'] == 136 and witness['generated_manifest_sha256'] == refs['manifest']['sha256']
         and witness['actual_PCM_equality_verified'] is False and witness['actual_nonzero_PCM_observed'] is False
         and witness['target_qualified'] is False and witness['full_G6_qualified'] is False
         and witness['source_inputs_before'] == witness['source_inputs_after'], 'actual_complete_raw_singleton_witness_scope')
    for name in ('generation_outer', 'witness_outer', 'controls_outer'):
        receipt = json.loads((ROOT / refs[name]['path']).read_bytes())
        need(receipt['status'] == 'TERMINAL' and type(receipt['returncode']) is int and receipt['returncode'] == 0 and
             type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0 and
             receipt.get('timed_out', False) is False and receipt.get('interrupted', False) is False and
             not receipt.get('error_type'), 'actual_generation_and_witness_terminal0')
    need(q['completed'] is True and q['reference_corpus_qualified'] is True and q['xiph_reference_qualified'] is True and
         q['dual_reference_qualified'] is False and q['original_dual_reference_passed'] is False and
         q['result'] == 'XIPH_QUALIFIED_DUAL_NONPASS' and q['profile'] == 'singletons8' and
         (q['xiph_cases'], q['native_compared'], q['native_lookup2_refusals'], q['native_packet_decode_failures'], q['paired_raw_packets'], q['expected_pcm_bytes']) ==
         (8, 0, 4, 4, 112, 225280), 'actual_complete8_Xiph_reference_qualification')
    need(q['original_report_sha256'] == refs['host']['sha256'] and
         q['original_outer_receipt_sha256'] == refs['host_outer']['sha256'] and
         outer['status'] == 'TERMINAL' and outer['returncode'] == 1 and
         host['completed'] is True and host['xiph_reference_qualified'] is True and host['dual_reference_qualified'] is False and
         len(host['cases']) == len(host['failures']) == 8 and len(host['commands']) == 16, 'preserve_actual_host_dual_NONPASS')
    if qterminal.get('schema') == 'direct-exec-tool-terminal-v1':
        need(qterminal['exit_code'] == 0 and qterminal['report_sha256'] == refs['qualification']['sha256'] and
             qterminal['entrypoint_sha256'] == pins['qualifier_sha256'], 'actual_qualifier_direct_terminal_binding')
    else:
        need(qterminal['status'] == 'TERMINAL' and qterminal['returncode'] == 0 and
             type(qterminal['owned_pid']) is int and qterminal['owned_pid'] > 0 and
             qterminal.get('timed_out', False) is False and qterminal.get('interrupted', False) is False and
             not qterminal.get('error_type'), 'actual_qualifier_wrapper_terminal')
    for item in q['validated_inputs'].values():
        observed(item['path'], item['sha256'], item['bytes'])
    for receipt in (outer, qterminal):
        for path, row in receipt.get('logs', {}).items():
            observed(path, row['sha256'], row['bytes'])
    need(q['validated_inputs']['qualifier/script']['sha256'] == pins['qualifier_sha256'] and
         q['validated_inputs']['qualifier/pins']['sha256'] == pins['qualifier_pins_sha256'], 'reviewed_qualifier_source_identity')
    matrix = json.loads((ROOT / refs['comparison']['path']).read_bytes())
    need(matrix['expected_same_decoder_pcm_equal_groups'] == pins['expected_equal_groups'] and
         matrix['expected_same_decoder_pcm_different_pairs'] == pins['expected_different_pairs'] and
         q['xiph_metamorphic_checks'] == [dict(decoder='libvorbis', kind=kind, cases=group, passed=True)
             for kind, groups in (('equal', pins['expected_equal_groups']), ('different', pins['expected_different_pairs']))
             for group in groups], 'actual_two_equal_triples_and_four_different_pairs')
    need(len(contract['model']['cases']) == len(mapping['cases']) == len(matrix['cases']) == 8 and
         [row['id'] for row in contract['model']['cases']] == pins['expected_case_ids'], 'exact_full8_order')
    rows = []
    for index, (model, origin, source) in enumerate(zip(contract['model']['cases'], mapping['cases'], matrix['cases'])):
        need(origin['case'] == index and model['id'] == origin['id'] == source['id'] and
             source == origin['original_case_fields'] == origin['selected_case_fields'] and origin['fields_changed'] == [], 'unchanged_selected_case_fields')
        rid = '0-' + model['id']
        raw = [row for row in host['cases'] if row['id'] == rid]
        accepted = [row for row in q['cases'] if row['id'] == rid]
        need(len(raw) == len(accepted) == 1, 'unique_real_reference_case')
        raw, accepted = raw[0], accepted[0]
        need(raw['input'] == source and raw['source_matrix_sha256'] == refs['comparison']['sha256'] and
             Path(raw['source_matrix']).resolve() == (ROOT / refs['comparison']['path']).resolve() and
             accepted['xiph_qualified'] is True and accepted['native_lookup2_refusal'] is (index < 4) and
             accepted['native_packet_decode_failure'] is (index >= 4) and accepted['native_cause_diagnosed'] is False and
             accepted['native_actual_returncode'] == (3199971767 if index < 4 else 4294967295) and
             accepted['frames'] == model['frames'][1:] and accepted['pcm_bytes'] == model['total_pcm'] and
             (accepted['rate'], accepted['channels'], accepted['bits']) == (model['rate'], 2, 16) and
             accepted['pcm_sha256'] == raw['decoded']['libvorbis']['pcm_sha256'], 'actual_reference_raw_and_PCM_binding')
        for kind, pair in origin['files'].items():
            for role in ('original', 'selected'):
                item = pair[role]
                observed(item['path'], item['sha256'], item['bytes'])
            need(pair['original']['sha256'] == pair['selected']['sha256'], 'selected_raw_bytes_unchanged')
        need(model['raw_sha256'] == {kind: origin['files'][kind]['original']['sha256']
                                    for kind in ('identification', 'setup', 'audio')}, 'model_raw_SHA_binding')
        rows.append(dict(case=index, id=model['id'], original_group=origin['original_group'], original_reference_id=rid,
            qualification_sha256=refs['qualification']['sha256'], original_host_report_sha256=refs['host']['sha256'],
            original_host_receipt_sha256=refs['host_outer']['sha256'], original_host_returncode=1,
            raw_sha256=model['raw_sha256'], frames=model['frames'], pcm_bytes=model['total_pcm'], rate=model['rate'], channels=2,
            reference_pcm_sha256=accepted['pcm_sha256'], reference_wav_sha256=raw['decoded']['libvorbis']['wav_sha256'],
            native_compared=False, native_lookup2_refusal=index < 4, native_packet_decode_failure=index >= 4,
            native_failure_kind=accepted['native_failure_kind'], native_actual_returncode=accepted['native_actual_returncode'],
            native_cause_diagnosed=False, xiph_qualified_existing=True))
    for item in list(facts.values()) + list(external.values()):
        need(fact(item['path']) == item, 'reference_fact_changed')
    return dict(schema='more-singletons8-recorded-reference-binding-v1', completed=True,
        contract_sha256=contract['contract_sha256'], cases=rows,
        source_scopes=[dict(name='actual_more_singletons8', qualification_path=refs['qualification']['path'],
            qualification_sha256=refs['qualification']['sha256'], host_path=refs['host']['path'],
            host_sha256=refs['host']['sha256'], receipt_path=refs['host_outer']['path'],
            receipt_sha256=refs['host_outer']['sha256'], original_returncode=1, totals=[8, 0, 4, 4, 112, 225280])],
        proof_facts=sorted(facts.values(), key=lambda row: row['path']), external_reference_tool_identities=list(external.values()),
        expected_equal_groups=pins['expected_equal_groups'], expected_different_pairs=pins['expected_different_pairs'],
        native_lookup2_refusals=4, native_packet_decode_failures=4, native_cause_diagnosed=False,
        new_reference_commands_executed=False, aggregate_reference_campaign_exists=False,
        actual_single_scope_reference_campaign_exists=True, dual_reference_passed=False,
        target_executed=False, target_numeric_comparison_performed=False, full_G6_qualified=False)


def verify(contract, mapping, binding):
    need(derive(contract, mapping) == binding, 'recorded_reference_binding_changed')
    return binding
