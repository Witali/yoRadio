"""Exact pure transition function; no numerical entrypoint or filesystem startup."""
from pcm_metrics import need

def transition_counts(pcm, case, offsets):
    channels = case['channels']
    need(channels in (1, 2) and len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(pcm) and
         [b - a for a, b in zip(offsets, offsets[1:])] == case['pcm'], 'Full real-channel packet offsets required')
    result = {name: [0] * channels for name in ('SS', 'SL', 'LS', 'LL')}
    for packet in range(1, 14):
        name = 'SL'[case['modes'][packet - 1]] + 'SL'[case['modes'][packet]]
        first, stop = offsets[packet:packet + 2]
        for channel in range(channels):
            result[name][channel] += sum(pcm[i:i + 2] != b'\0\0' for i in range(first + 2 * channel, stop, channels * 2))
    return result

