"""Full31 policy: unchanged project bound2 and fourteen exact source relations."""
from pcm_metrics import need, samples, errors
from policy25 import CASE_IDS as OLD25_IDS, relations8

CASE_IDS = ('ordered_lattice_d2_seq0', 'unordered_lattice_d2_seq0', 'sparse_lattice_d2_seq0', 'ordered_lattice_d2_seq1', 'ordered_explicit_d2_seq0', 'unordered_explicit_d2_seq1', 'sparse_explicit_d4_seq0', 'sparse_explicit_d4_seq1', 'sparse_explicit_d16_seq0', 'dense_active_d16_seq0', 'sparse_explicit_d16_seq1', 'dense_active_d16_seq1', 'single_explicit_d2_seq0', 'dense_twin_d2_seq0', 'single_explicit_d2_seq1', 'dense_twin_d2_seq1', 'floor1-r0-s64-l256', 'floor1-r0-s256-l2048', 'floor1-r0-s64-l2048', 'floor0-even6-r0-s64-l256', 'floor0-even6-r0-s256-l2048', 'floor0-even6-r0-s64-l2048', 'floor0-odd5-r0-s64-l256', 'floor0-odd5-r0-s256-l2048', 'floor0-odd5-r0-s64-l2048', 'floor0-even6-r0-minp1-s64-l256', 'floor0-even6-r0-minp1-s256-l2048', 'floor0-even6-r0-minp1-s64-l2048', 'floor0-odd5-r0-minp1-s64-l256', 'floor0-odd5-r0-minp1-s256-l2048', 'floor0-odd5-r0-minp1-s64-l2048')
FLOOR_PAIRS = tuple((CASE_IDS[19 + index], CASE_IDS[25 + index]) for index in range(6))


def relations14(pcm_by_id, books, floors):
    need(tuple(pcm_by_id) == CASE_IDS and len(pcm_by_id) == 31, 'All31 original ordered PCM values required')
    need(tuple(tuple(row) for row in floors) == FLOOR_PAIRS, 'Exact six original19..24/new25..30 floor0 pairs required')
    result = relations8({name: pcm_by_id[name] for name in OLD25_IDS[:16]}, books)
    for original, equivalent in FLOOR_PAIRS:
        first, second = pcm_by_id[original], pcm_by_id[equivalent]
        need(type(first) is bytes and type(second) is bytes and len(first) == len(second) and len(first) > 0,
             'Full equal-length floor0 relation PCM required')
        equal = first == second
        result.append(dict(kind='equal', cases=[original, equivalent], observed_byte_equal=equal,
            expected_relation_observed=equal, comparisons=[dict(first=original, second=equivalent,
                **errors(samples(first), samples(second)))]))
    need(len(result) == 14, 'All8books plus6floor0 relations required')
    return result


def bounded_policy31(cases, metamorphic, max_abs_error):
    need(max_abs_error is None or type(max_abs_error) is int and max_abs_error == 2,
         'Only the separately predeclared project threshold2 is supported')
    need(tuple(row['id'] for row in cases) == CASE_IDS and tuple(row['case'] for row in cases) == tuple(range(31)) and
         set(metamorphic) == {'xiph', 'target'} and all(len(rows) == 14 for rows in metamorphic.values()),
         'Exact complete31 scope and14 relations per decoder required')
    if max_abs_error is None:
        return None, False
    numeric = all(row['comparison']['zero_lag_direct_LR']['max_abs_error'] <= max_abs_error for row in cases)
    nonzero = all(all(channel['reference_nonzero_samples'] > 0 and channel['target_nonzero_samples'] > 0
        for channel in row['comparison']['channels']) for row in cases)
    transitions = all(set(row[key]) == {'SS', 'SL', 'LS', 'LL'} and
        all(len(counts) == 2 and all(type(value) is int and value > 0 for value in counts) for counts in row[key].values())
        for row in cases for key in ('reference_transition_channel_nonzero', 'target_transition_channel_nonzero'))
    relation_ok = all(row['expected_relation_observed'] for rows in metamorphic.values() for row in rows)
    policy = dict(purpose='bounded-corpus-regression-not-standard-conformance', scope='full_expanded31',
        max_abs_error=max_abs_error, selected_before_target_measurement=True, threshold_fitted_to_output=False,
        alignment='Every original zero-lag L/R sample and packet; no trim, gain fit, shift, swap or resampling',
        max_abs_error_within_bound=numeric, both_channels_nonzero=nonzero,
        both_channels_nonzero_each_transition=transitions, all_fourteen_relations_per_decoder=relation_ok, required_cases=31)
    return policy, numeric and nonzero and transitions and relation_ok
