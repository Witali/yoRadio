"""Strict mono signed-S16 measurements; no duplication, padding or fitted correction."""
import math
import struct

from pcm_metrics import errors, need


def samples(data, *, channels=1):
    need(type(channels) is int and channels == 1, 'Exactly one actual mono channel required')
    need(type(data) is bytes and len(data) % 2 == 0, 'Complete mono S16LE frames required')
    return struct.unpack('<' + 'h' * (len(data) // 2), data)


def compare(reference, target, packet_bytes, *, channels=1):
    need(type(reference) is bytes and type(target) is bytes and len(reference) == len(target),
         'Exact full mono PCM byte counts required; no truncation or padding')
    need(len(packet_bytes) == 14 and
         all(type(n) is int and n >= 0 and n % 2 == 0 for n in packet_bytes) and
         packet_bytes[0] == 0 and all(n > 0 for n in packet_bytes[1:]) and sum(packet_bytes) == len(reference),
         'Fourteen complete mono packet boundaries including zero primer required')
    a, b = samples(reference, channels=channels), samples(target, channels=channels)
    whole = errors(a, b, histogram=True)
    if whole['first_mismatch']:
        item = whole['first_mismatch']
        item.update(frame=item['sample'], channel=0)
    packets, cursor = [], 0
    for index, size in enumerate(packet_bytes):
        first, stop = cursor // 2, (cursor + size) // 2
        aa, bb = a[first:stop], b[first:stop]
        packets.append(dict(packet=index, byte_offset=cursor, bytes=size, frames=size // 2,
            all_samples=errors(aa, bb), channels=[errors(aa, bb)]))
        cursor += size
    need(cursor == len(reference), 'Complete mono packet coverage required')
    return dict(byte_equal=reference == target, frames=len(a), channels_count=1,
        unit='signed S16 integer LSB; error=target-reference', zero_lag_direct_mono=whole,
        channels=[errors(a, b)], packets=packets)


def alignment(reference, target, max_lag=8, *, channels=1):
    """Diagnostics only; all lags use the same interior mono frame range."""
    need(type(max_lag) is int and 0 <= max_lag <= 64, 'Diagnostic lag window 0..64 required')
    a, b = samples(reference, channels=channels), samples(target, channels=channels)
    need(len(a) == len(b) and len(a) > 2 * max_lag, 'Mono alignment frame shape')
    first, last = max_lag, len(a) - max_lag
    candidates = []
    for lag in range(-max_lag, max_lag + 1):
        squared = sum((b[i + lag] - a[i]) ** 2 for i in range(first, last))
        candidates.append(dict(target_lag_frames=lag, samples=last - first,
            sum_squared_error=squared, rms_error=math.sqrt(squared / (last - first))))
    minimum = min(item['sum_squared_error'] for item in candidates)
    return dict(diagnostic_only=True, applied_shift_frames=0, applied_channel_swap=False,
        fixed_reference_frame_range=[first, last], channel_pairs=[dict(reference_channel=0, target_channel=0,
            candidates=candidates, minimum_error_lags=[item['target_lag_frames'] for item in candidates
                                                     if item['sum_squared_error'] == minimum])],
        limitation='Finite/periodic signals may give ambiguous ties; no alignment correction is applied')
