"""Bind original4+preferred-zero4 to the exact existing mixed reference campaign."""
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import recorded_qualification as recorded
from protocol import CASE_IDS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def fact(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def qualification_gate(q):
    need(q['schema'] == 'public-vorbis-new-format-reference-qualification-v1' and q['profile'] == 'zero8' and
         q['result'] == 'XIPH_QUALIFIED_DUAL_NONPASS' and
         all(q[name] is True for name in ('completed', 'reference_corpus_qualified', 'xiph_reference_qualified')) and
         all(q[name] is False for name in ('dual_reference_qualified', 'original_dual_reference_passed',
             'native_cause_diagnosed', 'target_executed', 'production_changed', 'standard_conformance_qualified',
             'full_G6_qualified', 'physical_device')) and
         (q['xiph_cases'], q['native_compared'], q['native_lookup2_refusals'], q['native_packet_decode_failures'],
          q['paired_raw_packets'], q['expected_pcm_bytes']) == (8, 4, 0, 4, 112, 225280) and
         tuple(row['id'] for row in q['cases']) == tuple('0-' + name for name in CASE_IDS),
         'Complete exact zero8 mixed reference classification required; full8 dual pass prohibited')
    for index, row in enumerate(q['cases']):
        accepted = index >= 4
        need(row['xiph_qualified'] is True and row['native_compared'] is accepted and
             row['native_lookup2_refusal'] is False and row['native_packet_decode_failure'] is (not accepted) and
             row['native_outcome_kind'] == ('accepted' if accepted else 'packet_decode_failure_no_PCM') and
             type(row['native_actual_returncode']) is int and row['native_actual_returncode'] == (0 if accepted else 4294967295) and
             row['native_cause_diagnosed'] is False and
             (type(row['cross_reference_max_abs_error']) is int and 0 <= row['cross_reference_max_abs_error'] <= 2
              if accepted else row['cross_reference_max_abs_error'] is None),
             'Original4 packet refusals and new4 native acceptance remain separate and unexplained')


def derive(contract, mapping):
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    refs, facts, external = pins['reference'], {}, {}

    def observed(path, expected=None, size=None):
        row = fact(path)
        need(expected is None or row['sha256'] == expected, 'recorded_reference_SHA')
        need(size is None or row['bytes'] == size, 'recorded_reference_size')
        (facts if Path(row['path']).is_relative_to(ROOT) else external)[row['path']] = row
        return row

    for row in refs.values():
        observed(ROOT / row['path'], row['sha256'], row['bytes'])
    need(Path(recorded.__file__).resolve() == HERE / 'recorded_qualification.py' and
         fact(HERE / 'recorded_qualification.py')['sha256'] == pins['qualifier_sha256'] and
         fact(HERE / 'pins.json')['sha256'] == pins['qualifier_pins_sha256'] and
         fact(HERE / 'carrier.py')['sha256'] == pins['carrier_sha256'], 'normal_exact_recorded_qualifier_copies')
    q = json.loads((ROOT / refs['qualification']['path']).read_bytes())
    host = json.loads((ROOT / refs['host']['path']).read_bytes())
    outer = json.loads((ROOT / refs['host_outer']['path']).read_bytes())
    qterminal = json.loads((ROOT / refs['qualification_terminal']['path']).read_bytes())
    qualification_gate(q)
    recorded.terminal(outer, 1)
    recorded.terminal(qterminal, 0)
    need(q['original_report_sha256'] == refs['host']['sha256'] and
         q['original_outer_receipt_sha256'] == refs['host_outer']['sha256'] and
         len(host['cases']) == 8 and len(host['commands']) == 16 and len(host['failures']) == 4 and
         host['completed'] is host['xiph_reference_qualified'] is True and host['dual_reference_qualified'] is False,
         'actual_full8_host_dual_NONPASS_remains')
    # Exact normal helper replay verifies all16 child receipts/logs, all12
    # successful current WAV/framemd5 streams, four empty failed-native outputs,
    # original4 raw+full-Xiph equality to its predecessor and all four Xiph pairs.
    # qualify() is pure recorded I/O; its guarded CLI/main and any decoder never run.
    replay = copy.deepcopy(q)
    replay['cases'], replay['validated_inputs'] = [], {}
    recorded.qualify(SimpleNamespace(profile='zero8', repository=ROOT,
        campaign=(ROOT / refs['host']['path']).parent, outer=ROOT / refs['host_outer']['path']), replay, lambda: None)
    need({k: v for k, v in replay.items() if k != 'validated_inputs'} ==
         {k: v for k, v in q.items() if k != 'validated_inputs'}, 'complete_recorded_reference_replay_changed')
    need(set(replay['validated_inputs']) == set(q['validated_inputs']), 'complete_actual_reference_fact_roles')
    local_roles = {'qualifier/script': HERE / 'recorded_qualification.py', 'qualifier/pins': HERE / 'pins.json',
                   'qualifier/carrier': HERE / 'carrier.py'}
    for role, old in q['validated_inputs'].items():
        new = replay['validated_inputs'][role]
        need((new['bytes'], new['sha256']) == (old['bytes'], old['sha256']) and
             Path(new['path']).resolve() == local_roles.get(role, Path(old['path']).resolve()),
             'reference_replay_fact_identity_and_declared_helper_relocation')
        observed(old['path'], old['sha256'], old['bytes'])
        observed(new['path'], new['sha256'], new['bytes'])
    for receipt in (outer, qterminal):
        for path, row in receipt['logs'].items(): observed(path, row['sha256'], row['bytes'])
    matrix = json.loads((ROOT / refs['comparison']['path']).read_bytes())
    groups = matrix['expected_same_decoder_pcm_equal_groups']
    need(groups == pins['expected_equal_groups'] and matrix['expected_same_decoder_pcm_different_pairs'] == [] and
         q['xiph_metamorphic_checks'] == [dict(decoder='libvorbis', kind='equal', cases=group, passed=True) for group in groups] and
         len(groups) == 4 and len(q['original_map1_preservation']) == 4 and
         all(row['all_raw_bytes_equal'] is row['full_Xiph_PCM_bytes_equal'] is True for row in q['original_map1_preservation']),
         'original4_preservation_and_exact_four_existing_Xiph_equal_pairs')
    model = contract['model']
    need(len(model['cases']) == len(mapping['cases']) == len(matrix['cases']) == 8 and
         tuple(row['id'] for row in model['cases']) == CASE_IDS and
         (model['total_packets'], model['total_pcm'], model['case_mask']) == (112, 225280, 255), 'complete8_target_source_binding')
    rows = []
    for index, (case, origin, source, accepted, original) in enumerate(zip(
            model['cases'], mapping['cases'], matrix['cases'], q['cases'], host['cases'])):
        rid, native = '0-' + case['id'], index >= 4
        need(origin['case'] == index and case['id'] == origin['id'] == source['id'] and
             origin['original_case_fields'] == origin['selected_case_fields'] == source and origin['fields_changed'] == [] and
             original['id'] == accepted['id'] == rid and original['input'] == source and
             original['source_matrix_sha256'] == refs['comparison']['sha256'] and
             Path(original['source_matrix']).resolve() == ROOT / refs['comparison']['path'] and
             accepted['frames'] == case['frames'][1:] and accepted['pcm_bytes'] == case['total_pcm'] and
             (accepted['rate'], accepted['channels'], accepted['bits']) == (case['rate'], 2, 16) and
             accepted['pcm_sha256'] == original['decoded']['libvorbis']['pcm_sha256'], 'full_unchanged_raw_header_frame_reference_binding')
        for kind, pair in origin['files'].items():
            for role in ('original', 'selected'):
                item = pair[role]
                observed(item['path'], item['sha256'], item['bytes'])
            need(pair['original']['sha256'] == pair['selected']['sha256'], 'raw_selection_copy_changed')
        need(case['raw_sha256'] == {kind: origin['files'][kind]['original']['sha256']
                                    for kind in ('identification', 'setup', 'audio')}, 'model_raw_identification')
        rows.append(dict(case=index, id=case['id'], original_group='zero4' if native else 'original4',
            original_reference_id=rid, qualification_sha256=refs['qualification']['sha256'],
            original_host_report_sha256=refs['host']['sha256'], original_host_receipt_sha256=refs['host_outer']['sha256'],
            original_host_returncode=1, raw_sha256=case['raw_sha256'], frames=case['frames'], pcm_bytes=case['total_pcm'],
            rate=case['rate'], channels=2, reference_pcm_sha256=accepted['pcm_sha256'], reference_wav_sha256=accepted['wav_sha256'],
            native_compared=native, native_lookup2_refusal=False, native_packet_decode_failure=not native,
            native_outcome_kind=accepted['native_outcome_kind'], native_actual_returncode=accepted['native_actual_returncode'],
            cross_reference_max_abs_error=accepted['cross_reference_max_abs_error'], native_cause_diagnosed=False,
            xiph_qualified_existing=True))
    prior = json.loads((ROOT / refs['prior_numeric_record']['path']).read_bytes())
    need(prior['measurement_completed'] is True and prior['bounded_corpus_pcm_qualified'] is False and
         prior['result'] == 'BOUNDED_CORPUS_PCM_REJECTED', 'prior_original_singletons_numeric_NONPASS_record_unchanged')
    for item in list(facts.values()) + list(external.values()): need(fact(item['path']) == item, 'recorded_fact_changed')
    return dict(schema='singleton-zero8-recorded-reference-binding-v1', completed=True,
        contract_sha256=contract['contract_sha256'], cases=rows, proof_facts=sorted(facts.values(), key=lambda r: r['path']),
        external_reference_tool_identities=list(external.values()), source_scopes=[dict(name='actual_zero8',
            qualification_path=refs['qualification']['path'], qualification_sha256=refs['qualification']['sha256'],
            host_path=refs['host']['path'], host_sha256=refs['host']['sha256'], receipt_path=refs['host_outer']['path'],
            receipt_sha256=refs['host_outer']['sha256'], original_returncode=1, totals=[8, 4, 0, 4, 112, 225280])],
        expected_equal_groups=groups, expected_different_pairs=[], original_map1_preservation=q['original_map1_preservation'],
        native_compared=4, native_packet_decode_failures=4, native_lookup2_refusals=0, native_cause_diagnosed=False,
        successful_current_WAV_streams_replayed=12, actual_child_receipts_checked=16,
        new_reference_commands_executed=False, aggregate_reference_campaign_exists=False,
        actual_single_scope_reference_campaign_exists=True, dual_reference_passed=False,
        prior_original_singletons_numeric_record_only=True, prior_numeric_NONPASS_requalified=False,
        target_executed=False, target_numeric_comparison_performed=False, full_G6_qualified=False)


def verify(contract, mapping, binding):
    need(derive(contract, mapping) == binding, 'recorded_reference_binding_changed')
    return binding
