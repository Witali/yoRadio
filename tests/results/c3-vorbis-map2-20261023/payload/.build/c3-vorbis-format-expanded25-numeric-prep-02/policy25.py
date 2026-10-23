"""Explicit expanded25/declaredbooks16 project policy; original metrics unchanged."""
from pcm_metrics import need, relations

CASE_IDS = ('ordered_lattice_d2_seq0', 'unordered_lattice_d2_seq0', 'sparse_lattice_d2_seq0', 'ordered_lattice_d2_seq1', 'ordered_explicit_d2_seq0', 'unordered_explicit_d2_seq1', 'sparse_explicit_d4_seq0', 'sparse_explicit_d4_seq1', 'sparse_explicit_d16_seq0', 'dense_active_d16_seq0', 'sparse_explicit_d16_seq1', 'dense_active_d16_seq1', 'single_explicit_d2_seq0', 'dense_twin_d2_seq0', 'single_explicit_d2_seq1', 'dense_twin_d2_seq1', 'floor1-r0-s64-l256', 'floor1-r0-s256-l2048', 'floor1-r0-s64-l2048', 'floor0-even6-r0-s64-l256', 'floor0-even6-r0-s256-l2048', 'floor0-even6-r0-s64-l2048', 'floor0-odd5-r0-s64-l256', 'floor0-odd5-r0-s256-l2048', 'floor0-odd5-r0-s64-l2048')


def relations8(pcm_by_id, declared):
    need(len(declared) == 8, 'Exact old4 plus new4 relations required')
    need(set(pcm_by_id) == set(CASE_IDS[:16]), 'All declared16 book PCM values required')
    return relations(pcm_by_id, declared[:4]) + relations(pcm_by_id, declared[4:])


def selected_policy(cases, metamorphic, max_abs_error, expected_ids, scope):
    need(max_abs_error is None or type(max_abs_error) is int and max_abs_error == 2,
         'Only the separately predeclared project threshold2 is supported')
    need(tuple(row['id'] for row in cases) == expected_ids and
         tuple(row['case'] for row in cases) == tuple(range(len(expected_ids))) and
         set(metamorphic) == {'xiph', 'target'} and all(len(rows) == 8 for rows in metamorphic.values()),
         'Exact complete scope and eight relations per decoder required')
    if max_abs_error is None:
        return None, False
    numeric = all(row['comparison']['zero_lag_direct_LR']['max_abs_error'] <= max_abs_error for row in cases)
    nonzero = all(all(channel['reference_nonzero_samples'] > 0 and channel['target_nonzero_samples'] > 0
                      for channel in row['comparison']['channels']) for row in cases)
    transition_nonzero = all(set(row[key]) == {'SS','SL','LS','LL'} and
        all(len(counts) == 2 and all(type(value) is int and value > 0 for value in counts)
            for counts in row[key].values())
        for row in cases for key in ('reference_transition_channel_nonzero','target_transition_channel_nonzero'))
    relation_ok = all(row['expected_relation_observed'] for rows in metamorphic.values() for row in rows)
    policy = dict(purpose='bounded-corpus-regression-not-standard-conformance', scope=scope,
        max_abs_error=max_abs_error, selected_before_target_measurement=True, threshold_fitted_to_output=False,
        alignment='Every original zero-lag L/R sample and packet; no trim, gain fit, shift, swap or resampling',
        max_abs_error_within_bound=numeric, both_channels_nonzero=nonzero,
        both_channels_nonzero_each_transition=transition_nonzero,
        all_eight_relations_per_decoder=relation_ok, required_cases=len(expected_ids))
    return policy, numeric and nonzero and transition_nonzero and relation_ok


def bounded_policy25(cases, metamorphic, max_abs_error):
    return selected_policy(cases, metamorphic, max_abs_error, CASE_IDS, 'full_expanded25')


def bounded_policy_books16(cases, metamorphic, max_abs_error):
    return selected_policy(cases, metamorphic, max_abs_error, CASE_IDS[:16], 'declared_books16_subgroup_only')
