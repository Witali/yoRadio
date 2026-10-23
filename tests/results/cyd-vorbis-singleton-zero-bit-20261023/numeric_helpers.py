"""Exact pure transition helper; no measurement startup or filesystem I/O."""
from pcm_metrics import need

def transition_counts(pcm, case, offsets):
    need(case['channels'] == 2 and len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(pcm) and
         [b - a for a, b in zip(offsets, offsets[1:])] == case['pcm'], 'Full stereo packet offsets required')
    result = {name: [0, 0] for name in ('SS', 'SL', 'LS', 'LL')}
    for packet in range(1, 14):
        name = 'SL'[case['modes'][packet - 1]] + 'SL'[case['modes'][packet]]
        first, stop = offsets[packet:packet + 2]
        for channel in (0, 1):
            result[name][channel] += sum(pcm[i:i + 2] != b'\0\0' for i in range(first + 2 * channel, stop, 4))
    return result

