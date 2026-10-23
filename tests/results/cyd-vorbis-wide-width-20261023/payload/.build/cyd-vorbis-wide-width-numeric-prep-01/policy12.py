"""Predeclared exact12 numerical policy and source-derived equivalence relations."""
from pcm_metrics import need
CASE_IDS = ('sparse_explicit_d16_seq0', 'dense_active_d16_seq0', 'sparse_explicit_d16_seq1', 'dense_active_d16_seq1', 'sparse_explicit_d16_seq0_qbits9', 'dense_active_d16_seq0_qbits9', 'sparse_explicit_d16_seq1_qbits9', 'dense_active_d16_seq1_qbits9', 'sparse_explicit_d16_seq0_qbits16', 'dense_active_d16_seq0_qbits16', 'sparse_explicit_d16_seq1_qbits16', 'dense_active_d16_seq1_qbits16')
TRIPLES = [['sparse_explicit_d16_seq0', 'sparse_explicit_d16_seq0_qbits9', 'sparse_explicit_d16_seq0_qbits16'], ['dense_active_d16_seq0', 'dense_active_d16_seq0_qbits9', 'dense_active_d16_seq0_qbits16'], ['sparse_explicit_d16_seq1', 'sparse_explicit_d16_seq1_qbits9', 'sparse_explicit_d16_seq1_qbits16'], ['dense_active_d16_seq1', 'dense_active_d16_seq1_qbits9', 'dense_active_d16_seq1_qbits16']]
SHAPE_PAIRS = [['sparse_explicit_d16_seq0', 'dense_active_d16_seq0'], ['sparse_explicit_d16_seq1', 'dense_active_d16_seq1'], ['sparse_explicit_d16_seq0_qbits9', 'dense_active_d16_seq0_qbits9'], ['sparse_explicit_d16_seq1_qbits9', 'dense_active_d16_seq1_qbits9'], ['sparse_explicit_d16_seq0_qbits16', 'dense_active_d16_seq0_qbits16'], ['sparse_explicit_d16_seq1_qbits16', 'dense_active_d16_seq1_qbits16']]


def relations(values, groups):
    need(set(values) == set(CASE_IDS), 'All12 named PCM values required')
    result = []
    for group in groups:
        need(len(group) in (2, 3) and all(name in values for name in group), 'Complete predeclared relation members required')
        equal = all(values[name] == values[group[0]] for name in group[1:])
        result.append(dict(kind='equal', cases=group, observed_byte_equal=equal, expected_relation_observed=equal))
    return result


def bounded_policy(cases, metamorphic, max_abs_error):
    need(max_abs_error is None or type(max_abs_error) is int and max_abs_error == 2, 'Only predeclared bound2 is supported')
    need(tuple(row['id'] for row in cases) == CASE_IDS and [row['case'] for row in cases] == list(range(12)), 'Exact complete12 case order required')
    need(set(metamorphic) == {'xiph_triples', 'target_triples', 'xiph_shape_pairs', 'target_shape_pairs'} and
         all(len(metamorphic[name]) == (4 if name.endswith('triples') else 6) for name in metamorphic), 'Exact declared relation inventory')
    if max_abs_error is None:
        return None, False
    numeric = all(row['comparison']['zero_lag_direct_LR']['max_abs_error'] <= 2 for row in cases)
    nonzero = all(all(item['reference_nonzero_samples'] > 0 and item['target_nonzero_samples'] > 0
                     for item in row['comparison']['channels']) for row in cases)
    transitions = all(set(row[name]) == {'SS', 'SL', 'LS', 'LL'} and all(len(v) == 2 and all(n > 0 for n in v)
                      for v in row[name].values()) for row in cases for name in ('reference_transition_nonzero', 'target_transition_nonzero'))
    equal = all(row['expected_relation_observed'] for rows in metamorphic.values() for row in rows)
    policy = dict(purpose='bounded-corpus-regression-not-standard-conformance', scope='exact_wide_width12',
        max_abs_error=2, selected_before_target_measurement=True, threshold_fitted_to_output=False,
        zero_lag_original_LR_only=True, applied_trim=False, applied_gain_fit=False, applied_shift=False, applied_channel_swap=False,
        max_abs_error_within_bound=numeric, both_channels_nonzero=nonzero,
        both_channels_nonzero_each_transition=transitions, all_predeclared_relations=equal,
        required_cases=12, three_width_groups_per_decoder=4, source_derived_sparse_dense_pairs_per_decoder=6)
    return policy, numeric and nonzero and transitions and equal
