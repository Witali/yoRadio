"""Compare free heap in equal theme/GIF phases; SDK minima alone cannot show leaks."""
from collections import defaultdict
import math
import statistics


def analyze_trend(series, start, end, warmup=3600, window=3600, phase_period=20):
    """Report retained loss and sustained decline with measured first-window variation."""
    if not math.isfinite(warmup) or warmup < 0 or not math.isfinite(window) or window <= 0:
        raise ValueError('Invalid trend windows')
    if type(phase_period) is not int or phase_period < 20 or phase_period % 20:
        raise ValueError('Invalid workload phase period')
    bins = defaultdict(lambda: defaultdict(list))
    complete_windows = max(0, math.floor((end - start - warmup) / window))
    for row in series:
        when = row['guest_seconds'] - start - warmup
        if row['cycle'] >= 0 and when >= 0:
            index = math.floor(when / window)
            if index < complete_windows:
                bins[index][row['cycle'] % phase_period].append(row['free_bytes'])
    windows = []
    for index, phases in sorted(bins.items()):
        windows.append({'index': index, 'complete_phase_coverage': len(phases) == phase_period,
            'phases': {str(p): {'samples': len(values), 'median': statistics.median(values),
                               'minimum': min(values), 'maximum': max(values)} for p, values in sorted(phases.items())}})
    usable = [row for row in windows if row['complete_phase_coverage']]
    flags, phase_results = [], {}
    if len(usable) >= 3:
        for phase in map(str, range(phase_period)):
            rows = [row['phases'][phase] for row in usable]
            values = [row['median'] for row in rows]
            variation = rows[0]['maximum'] - rows[0]['minimum']
            loss = values[0] - values[-1]
            mean_x = statistics.mean(row['index'] for row in usable)
            mean_y = statistics.mean(values)
            slope = sum((row['index'] - mean_x) * (value - mean_y) for row, value in zip(usable, values)) / sum(
                (row['index'] - mean_x)**2 for row in usable)
            sustained = all(later < earlier for earlier, later in zip(values, values[1:]))
            reasons = []
            if sustained:
                reasons.append('every_steady_window_declines')
            if loss > variation:
                reasons.append('retained_loss_exceeds_initial_phase_variation')
            phase_results[phase] = {'first_median': values[0], 'last_median': values[-1],
                'initial_variation_bytes': variation, 'retained_loss_bytes': loss,
                'slope_bytes_per_guest_hour': slope * 3600 / window, 'reasons': reasons}
            if reasons:
                flags.append({'phase': int(phase), 'reasons': reasons})
    enough = len(usable) >= 3 and len(usable) == complete_windows
    return {'status': ('insufficient_steady_state_data' if not enough else
                       'retained_loss_requires_explanation' if flags else 'no_decline_flagged_at_observed_resolution'),
            'warmup_guest_seconds': warmup, 'window_guest_seconds': window,
            'complete_windows_expected': complete_windows, 'usable_windows': len(usable),
            'phase_period_cycles': phase_period, 'windows': windows, 'phases': phase_results, 'flags': flags,
            'limitations': ['Observed phase/window medians and variation do not prove absence of every possible leak.',
                'SDK minimum is cumulative; a constant minimum can coexist with declining current free heap.',
                'Retained changes require an explanation or a firmware fix before accepting the soak.']}
