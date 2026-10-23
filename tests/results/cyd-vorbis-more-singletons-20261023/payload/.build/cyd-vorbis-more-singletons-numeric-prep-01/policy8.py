"""Fixed predeclared project criterion for complete original singleton8 PCM."""
from pcm_metrics import need

CASE_IDS = ('map2_sparse_single_d4_seq0', 'map2_sparse_single_d4_seq1',
            'map2_sparse_single_d16_seq0', 'map2_sparse_single_d16_seq1',
            'map1_dense_single_d16_seq0', 'map1_dense_single_d16_seq1',
            'map1_sparse_single_d16_seq0', 'map1_sparse_single_d16_seq1')
TRIPLES = [['map2_sparse_single_d16_seq0', 'map1_dense_single_d16_seq0', 'map1_sparse_single_d16_seq0'],
           ['map2_sparse_single_d16_seq1', 'map1_dense_single_d16_seq1', 'map1_sparse_single_d16_seq1']]
DIFFERENT_PAIRS = [['map2_sparse_single_d4_seq0', 'map2_sparse_single_d4_seq1'],
                   ['map2_sparse_single_d16_seq0', 'map2_sparse_single_d16_seq1'],
                   ['map1_dense_single_d16_seq0', 'map1_dense_single_d16_seq1'],
                   ['map1_sparse_single_d16_seq0', 'map1_sparse_single_d16_seq1']]


def relations(values, groups, kind='equal'):
    need(set(values) == set(CASE_IDS), 'All8 named complete PCM values required')
    need((kind == 'equal' and groups == TRIPLES) or (kind == 'different' and groups == DIFFERENT_PAIRS), 'Exact predeclared relation set required')
    result = []
    for group in groups:
        equal = all(values[name] == values[group[0]] for name in group[1:])
        result.append(dict(kind=kind, cases=group, observed_byte_equal=equal,
                           expected_relation_observed=equal if kind == 'equal' else not equal))
    return result


def bounded_policy(cases, metamorphic, max_abs_error):
    need(type(max_abs_error) is int and max_abs_error == 2, 'Fixed predeclared bound2 required')
    need(tuple(row['id'] for row in cases) == CASE_IDS and [row['case'] for row in cases] == list(range(8)), 'Exact complete8 case order required')
    need(set(metamorphic) == {'xiph_triples', 'target_triples', 'xiph_different_pairs', 'target_different_pairs'}, 'Exact four relation inventories required')
    for name, rows in metamorphic.items():
        groups = TRIPLES if name.endswith('triples') else DIFFERENT_PAIRS
        kind = 'equal' if name.endswith('triples') else 'different'
        need([row['cases'] for row in rows] == groups and all(row['kind'] == kind for row in rows), 'Exact ordered predeclared relation inventory')
    numeric = all(row['comparison']['zero_lag_direct_LR']['max_abs_error'] <= 2 for row in cases)
    nonzero = all(all(item['reference_nonzero_samples'] > 0 and item['target_nonzero_samples'] > 0
                     for item in row['comparison']['channels']) for row in cases)
    transitions = all(set(row[name]) == {'SS', 'SL', 'LS', 'LL'} and all(len(v) == 2 and all(n > 0 for n in v)
                      for v in row[name].values()) for row in cases for name in ('reference_transition_nonzero', 'target_transition_nonzero'))
    relation_ok = all(row['expected_relation_observed'] for rows in metamorphic.values() for row in rows)
    policy = dict(purpose='bounded-corpus-regression-not-standard-conformance', scope='exact_original_singletons8',
        max_abs_error=2, selected_before_target_measurement=True, threshold_fitted_to_output=False,
        zero_lag_original_LR_only=True, applied_trim=False, applied_gain_fit=False, applied_shift=False,
        applied_channel_swap=False, applied_resampling=False, max_abs_error_within_bound=numeric,
        both_channels_nonzero=nonzero, both_channels_nonzero_each_transition=transitions,
        all_predeclared_relations=relation_ok, required_cases=8, required_packets=112, required_PCM_bytes=225280,
        equal_triples_per_decoder=2, different_pairs_per_decoder=4,
        original_dual_reference_NONPASS_preserved=True)
    return policy, numeric and nonzero and transitions and relation_ok
