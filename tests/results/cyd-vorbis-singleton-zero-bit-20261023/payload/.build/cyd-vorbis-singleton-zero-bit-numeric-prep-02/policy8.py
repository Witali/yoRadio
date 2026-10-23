"""Predeclared full8/mixed12 zero-lag bound2 and four original/preferred-zero relations."""
from pcm_metrics import need
from protocol import CASE_IDS

FRAMES = (0, 128, 576, 1024, 1024, 576, 576, 576, 128, 128, 576, 1024, 576, 128)
GROUPS = tuple((CASE_IDS[index], CASE_IDS[index + 4]) for index in range(4))
MAX_ABS_ERROR = 2


def relations(values):
    need(set(values) == set(CASE_IDS) and all(type(v) is bytes and len(v) == 28160 for v in values.values()),
         'All8 complete original stereo PCM streams required for relations')
    return [dict(kind='equal', cases=list(group), observed_byte_equal=values[group[0]] == values[group[1]],
                 expected_relation_observed=values[group[0]] == values[group[1]]) for group in GROUPS]


def bounded_policy(cases, metamorphic, max_abs_error=MAX_ABS_ERROR):
    need(type(max_abs_error) is int and max_abs_error == 2, 'Only unchanged fixed project bound2 is supported')
    need(tuple(row['id'] for row in cases) == CASE_IDS and [row['case'] for row in cases] == list(range(8)),
         'Exact complete8 original4 then preferred-zero4 required')
    need(set(metamorphic) == {'xiph', 'target'} and all(
        [row['cases'] for row in group] == [list(pair) for pair in GROUPS] and all(row['kind'] == 'equal' for row in group)
        for group in metamorphic.values()), 'Exactly four declared equality pairs per Xiph/target required')
    bounded = {name: [] for name in ('libvorbis', 'vorbis')}
    numeric = {name: [] for name in bounded}
    nonzero = {name: [] for name in bounded}
    transitions = {name: [] for name in bounded}
    comparisons = 0
    for index, row in enumerate(cases):
        native = index >= 4
        decoders = ('libvorbis', 'vorbis') if native else ('libvorbis',)
        need(row['channels'] == 2 and row['rate'] == 192000 and row['bits'] == 16 and
             tuple(row['frames']) == FRAMES and row['packet_bytes'] == [n * 4 for n in FRAMES] and
             row['pcm_bytes'] == 28160 and set(row['references']) == set(decoders) and
             row['native_compared'] is native and row['native_packet_decode_failure'] is (not native) and
             row['native_lookup2_refusal'] is False and row['native_cause_diagnosed'] is False and
             row['native_actual_returncode'] == (0 if native else 4294967295),
             'Exact original4 refusal/new4 acceptance and full stereo geometry required')
        for decoder in decoders:
            measured = row['references'][decoder]
            comparison = measured['comparison']
            whole = comparison['zero_lag_direct_LR']
            need(comparison['frames'] == 7040 and whole['samples'] == 14080 and len(comparison['channels']) == 2 and
                 all(channel['samples'] == 7040 for channel in comparison['channels']) and
                 len(comparison['packets']) == 14 and
                 [packet['packet'] for packet in comparison['packets']] == list(range(14)) and
                 [packet['bytes'] for packet in comparison['packets']] == row['packet_bytes'] and
                 [packet['frames'] for packet in comparison['packets']] == list(FRAMES) and
                 all(len(packet['channels']) == 2 for packet in comparison['packets']),
                 'Complete unchanged signed-S16 samples and every packet required')
            within = whole['max_abs_error'] <= 2
            nz = all(channel['reference_nonzero_samples'] > 0 and channel['target_nonzero_samples'] > 0
                     for channel in comparison['channels'])
            tx = all(set(measured[name]) == {'SS', 'SL', 'LS', 'LL'} and
                     all(len(values) == 2 and all(type(n) is int and n > 0 for n in values)
                         for values in measured[name].values())
                     for name in ('reference_transition_nonzero', 'target_transition_nonzero'))
            numeric[decoder].append(within); nonzero[decoder].append(nz); transitions[decoder].append(tx)
            bounded[decoder].append(within and nz and tx)
            comparisons += 1
    need(comparisons == 12 and len(bounded['libvorbis']) == 8 and len(bounded['vorbis']) == 4,
         'Exactly12 available-reference comparisons required; no invented native original PCM')
    groups = {name: all(row['expected_relation_observed'] is True and row['observed_byte_equal'] is True for row in group)
              for name, group in metamorphic.items()}
    primary = all(bounded['libvorbis']) and all(bounded['vorbis']) and all(groups.values())
    policy = dict(purpose='bounded-corpus-regression-not-standard-conformance', scope='exact_singleton_zero8_mixed_reference12',
        max_abs_error=2, selected_before_target_measurement=True, threshold_fitted_to_output=False,
        required_cases=8, required_reference_comparisons=12, reference_scopes=dict(libvorbis='all8', vorbis='new_zero4_only'),
        original4_native_packet_refusals=4, full8_dual_reference_passed=False, native_cause_diagnosed=False,
        zero_lag_original_LR_only=True, applied_trim=False, applied_gain_fit=False, applied_shift=False,
        applied_channel_swap=False, applied_resampling=False, applied_padding=False,
        max_abs_error_within_bound_by_reference={name: all(rows) for name, rows in numeric.items()},
        both_channels_nonzero_by_reference={name: all(rows) for name, rows in nonzero.items()},
        both_channels_nonzero_each_transition_by_reference={name: all(rows) for name, rows in transitions.items()},
        bounded_by_reference=dict(libvorbis_all8=all(bounded['libvorbis']), vorbis_zero4=all(bounded['vorbis'])),
        bounded_original4_Xiph=all(bounded['libvorbis'][:4]),
        bounded_new_zero4_both_references=all(bounded['libvorbis'][4:]) and all(bounded['vorbis']),
        four_equal_pairs_by_decoder=groups, prior_other_numeric_NONPASS_record_only=True,
        prior_numeric_NONPASS_requalified=False)
    return policy, primary
