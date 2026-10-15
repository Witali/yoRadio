"""Describe heap trends without mistaking three samples for a leak diagnosis.

Contiguous thirds are defined from the whole collection, rather than selecting
favorable time boundaries. Compare first/last thirds and retain the old three-sample
comparison. These are bounded statistical observations, not allocation tracing.
"""
import statistics

from common import require


def heap_trend(samples):
    require(len(samples) >= 6, 'Need six heap observations')
    times = [s['uptime_ms'] for s in samples]
    require(all(b > a for a, b in zip(times, times[1:])),
            'Heap observations must have increasing uptime')
    third = max(3, len(samples) // 3)
    result = dict(samples=len(samples), endpoint_samples=third, fields={})
    for key, tolerance in (('heap', 2048), ('largest', 4096)):
        values = [s[key] for s in samples]
        require(all(type(v) is int and v >= 0 for v in values),
                'Invalid heap observation: ' + key)
        first, last = values[:third], values[-third:]
        old_first, old_last = statistics.median(values[:3]), statistics.median(values[-3:])
        before, after = statistics.median(first), statistics.median(last)
        # A late sustained fall below the entire initial range must not be
        # hidden by a long final third. Keep the old three-sample sensitivity
        # for this case, while allowing repeated lows already seen initially.
        below_initial_range = min(first) - old_last
        result['fields'][key] = dict(tolerance=tolerance,
            first_median=before, last_median=after, median_loss=before-after,
            first_range=[min(first), max(first)], last_range=[min(last), max(last)],
            endpoint_loss=old_first-old_last,
            final_below_initial_range=below_initial_range,
            loss_detected=before-after > tolerance or below_initial_range > tolerance)
    return result
