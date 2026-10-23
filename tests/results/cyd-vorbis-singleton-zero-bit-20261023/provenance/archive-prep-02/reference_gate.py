"""Exact finite mixed-reference scope gate; no filesystem startup."""
CASE_IDS = ('map1_dense_single_d16_seq0', 'map1_dense_single_d16_seq1', 'map1_sparse_single_d16_seq0', 'map1_sparse_single_d16_seq1', 'map1_dense_single_d16_seq0_wire0', 'map1_dense_single_d16_seq1_wire0', 'map1_sparse_single_d16_seq0_wire0', 'map1_sparse_single_d16_seq1_wire0')

def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


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

