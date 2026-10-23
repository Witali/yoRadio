"""Predeclared full21 raw-channel zero-lag bound2; no output-dependent policy fitting."""
from pcm_metrics import need

RATES = (8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000)
CASE_IDS = tuple('uncoupled-c' + str(channels) + '-r' + str(rate)
                 for rate in RATES for channels in (1, 2)) + (
    'coupled-c2-r48000', 'submaps-c2-r48000', 'residue2-c2-r48000')
CHANNELS = (1, 2) * 9 + (2, 2, 2)
CASE_RATES = tuple(rate for rate in RATES for unused in (1, 2)) + (48000, 48000, 48000)
FRAMES = (0, 128, 576, 1024, 1024, 576, 576, 576, 128, 128, 576, 1024, 576, 128)
DECODERS = ('vorbis', 'libvorbis')
MAX_ABS_ERROR = 2


def whole(comparison, channels):
    return comparison['zero_lag_direct_mono' if channels == 1 else 'zero_lag_direct_LR']


def bounded_policy(cases, max_abs_error=MAX_ABS_ERROR):
    need(type(max_abs_error) is int and max_abs_error == 2, 'Only fixed predeclared bound2 is supported')
    need(tuple(row['id'] for row in cases) == CASE_IDS and
         [row['case'] for row in cases] == list(range(21)) and
         tuple(row['channels'] for row in cases) == CHANNELS, 'Exact complete21 ordered mono/stereo cases required')
    numeric = {decoder: True for decoder in DECODERS}
    nonzero = {decoder: True for decoder in DECODERS}
    transitions = {decoder: True for decoder in DECODERS}
    for row, channels, rate in zip(cases, CHANNELS, CASE_RATES):
        need(tuple(row['frames']) == FRAMES and row['bits'] == 16 and row['rate'] == rate and
             row['packet_bytes'] == [n * channels * 2 for n in FRAMES] and
             row['pcm_bytes'] == 7040 * channels * 2 and set(row['references']) == set(DECODERS),
             'Exact full21 frames/real-channel PCM/reference geometry required')
        for decoder in DECODERS:
            ref = row['references'][decoder]
            comparison = ref['comparison']
            need(comparison['frames'] == 7040 and len(comparison['channels']) == channels and
                 len(comparison['packets']) == 14 and
                 [packet['packet'] for packet in comparison['packets']] == list(range(14)) and
                 [packet['bytes'] for packet in comparison['packets']] == row['packet_bytes'] and
                 [packet['frames'] for packet in comparison['packets']] == list(FRAMES) and
                 all(len(packet['channels']) == channels for packet in comparison['packets']) and
                 whole(comparison, channels)['samples'] == 7040 * channels and
                 all(channel['samples'] == 7040 for channel in comparison['channels']),
                 'Complete unchanged mono/stereo measurement sample/packet counts required')
            numeric[decoder] = numeric[decoder] and whole(comparison, channels)['max_abs_error'] <= max_abs_error
            nonzero[decoder] = nonzero[decoder] and all(
                channel['reference_nonzero_samples'] > 0 and channel['target_nonzero_samples'] > 0
                for channel in comparison['channels'])
            for name in ('reference_transition_nonzero', 'target_transition_nonzero'):
                counts = ref[name]
                transitions[decoder] = transitions[decoder] and set(counts) == {'SS', 'SL', 'LS', 'LL'} and all(
                    len(values) == channels and all(type(n) is int and n > 0 for n in values)
                    for values in counts.values())
    policy = dict(purpose='bounded-corpus-regression-not-standard-conformance', scope='exact_mono_mapping21',
        max_abs_error=2, required_cases=21, required_reference_comparisons=42,
        selected_before_target_measurement=True, threshold_fitted_to_output=False,
        both_existing_reference_decoders_required=True, zero_lag_original_channels_only=True,
        applied_trim=False, applied_gain_fit=False, applied_shift=False, applied_channel_swap=False,
        applied_resampling=False, applied_mono_duplication=False, applied_padding=False,
        max_abs_error_within_bound_by_reference=numeric, every_actual_channel_nonzero_by_reference=nonzero,
        every_actual_channel_nonzero_each_transition_by_reference=transitions,
        bounded_by_reference={decoder: numeric[decoder] and nonzero[decoder] and transitions[decoder]
                              for decoder in DECODERS},
        original_dual_reference_scope='only-existing-mono21-campaign', previous_unrelated_NONPASS_reinterpreted=False)
    return policy, all(policy['bounded_by_reference'].values())
