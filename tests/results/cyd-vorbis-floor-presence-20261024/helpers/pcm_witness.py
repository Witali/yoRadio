"""Pure predeclared floor-presence/overlap PCM16 witnesses; no decoder invocation."""


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def derive(case):
    """Independently derive silence envelopes from floor flags and block centers."""
    channels, modes, schedule = case['channels'], case['mode_flags'], case['schedule']
    need(type(channels) is int and channels in (1, 2) and len(modes) == len(schedule) == 14,
         'presence_witness_case_shape')
    need(all(type(x) is int and x in (0, 1) for x in modes) and
         all(type(x) is int and 0 <= x < 1 << channels for x in schedule), 'presence_witness_typed_masks_modes')
    need((case['short'], case['long']) == (256, 2048), 'presence_witness_frozen_block_geometry')
    blocks = [case['long'] if m else case['short'] for m in modes]
    result = []
    for packet, block in enumerate(blocks):
        if packet == 0:
            result.append(dict(packet=0, frames=0, channel_zero_spans=[[] for _ in range(channels)],
                channel_requires_nonzero=[False] * channels, reason='primer_emits_no_frames'))
            continue
        previous = blocks[packet - 1]; frames = (previous + block) // 4
        # Independent support-envelope derivation, rather than writer branches.
        previous_support = (0, min(previous // 2, frames))
        current_support = (max(0, (previous - block) // 4), frames)
        zeros, required = [], []
        for channel in range(channels):
            supports = []
            if schedule[packet - 1] & (1 << channel): supports.append(previous_support)
            if schedule[packet] & (1 << channel): supports.append(current_support)
            occupied = [any(start <= sample < end for start, end in supports) for sample in range(frames)]
            spans = []; start = None
            for sample, active in enumerate(occupied + [True]):
                if not active and start is None: start = sample
                if active and start is not None: spans.append([start, sample]); start = None
            zeros.append(spans); required.append(bool(supports))
        result.append(dict(packet=packet, frames=frames, channel_zero_spans=zeros,
            channel_requires_nonzero=required, previous_floor_mask=schedule[packet - 1],
            current_floor_mask=schedule[packet], reason='postfloor_zero_blocks_and_Vorbis_window_support'))
    need(result == case['packet_PCM_witnesses'], 'serialized_PCM_witnesses_match_independent_geometry')
    need([row['frames'] for row in result] == case['expected_packet_frames'] == case['expected_packet_samples'],
         'witness_frames_equal_packet_contract')
    need([row['frames'] * channels * 2 for row in result] == case['expected_packet_s16le_bytes'],
         'witness_frames_equal_PCM_contract')
    absent = [not any(mask & (1 << c) for mask in schedule) for c in range(channels)]
    need(case['always_absent_channel_silence_witness'] == absent and
         case['constant_all_absent_silence_witness'] == (case['schedule_kind'] == 'constant' and not any(schedule)),
         'separate_constant_and_absent_channel_witnesses')
    return result


def packet(pcm, channels, witness):
    need(len(pcm) == witness['frames'] * channels * 2, 'witness_full_PCM16_channel_frames')
    counts = []
    for channel in range(channels):
        samples = [pcm[(sample * channels + channel) * 2:(sample * channels + channel) * 2 + 2]
            for sample in range(witness['frames'])]
        for first, stop in witness['channel_zero_spans'][channel]:
            need(0 <= first < stop <= len(samples) and all(x == b'\0\0' for x in samples[first:stop]),
                 'guaranteed_silent_frame_span_channel:' + str(channel))
        count = sum(x != b'\0\0' for x in samples)
        need((count > 0) == witness['channel_requires_nonzero'][channel],
             'predeclared_packet_channel_zero_nonzero:' + str(channel))
        counts.append(count)
    return dict(nz_l=counts[0], nz_r=counts[1] if channels == 2 else 0)


def stream(pcm, case):
    witnesses = derive(case); offsets = [0]; rows = []
    for witness in witnesses:
        stop = offsets[-1] + witness['frames'] * case['channels'] * 2
        rows.append(packet(pcm[offsets[-1]:stop], case['channels'], witness)); offsets.append(stop)
    need(offsets[-1] == len(pcm) == case['expected_s16le_bytes'], 'complete_stream_PCM_witness')
    return dict(packet_offsets=offsets, packets=rows,
        constant_all_absent_witness=case['constant_all_absent_silence_witness'],
        always_absent_channels=case['always_absent_channel_silence_witness'])
