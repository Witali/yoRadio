"""Attribute existing phase/window medians without changing their acceptance rules."""
from collections import defaultdict
import math

from runtime_evidence import finite, integer, require
from runtime_trend import analyze_trend


COUNTERS = ('tcp_consumed_bytes', 'unclassified_consumed_bytes', 'tcp_blocks', 'unclassified_blocks',
            'pcbs', 'segments', 'pbufs', 'time_wait_pcbs', 'unregistered_pcbs')


def average(values):
    """Match the original median's integer/half-integer arithmetic exactly."""
    require(len(values) in (1, 2), 'A median has one or two central observations')
    return values[0] if len(values) == 1 else sum(values) / 2


def central_components(rows, expected_median):
    """Use the same free-heap order statistics for every additive component."""
    ordered = sorted(rows, key=lambda row: (row['free_bytes'], row['guest_seconds'], row['cycle']))
    count = len(ordered)
    positions = [count // 2] if count % 2 else [count // 2 - 1, count // 2]
    centers = [ordered[position] for position in positions]
    median = average([row['free_bytes'] for row in centers])
    require(median == expected_median, 'Attribution does not use the original free-heap median')
    central_values = [row['free_bytes'] for row in centers]
    candidates = [row for row in ordered if row['free_bytes'] in central_values]
    if any(not row['tcp']['observed'] for row in candidates):
        return {'status': 'unavailable_busy_samples', 'samples': count,
                'observed_samples': sum(row['tcp']['observed'] for row in rows),
                'central_candidate_samples': len(candidates),
                'central_observed_samples': sum(row['tcp']['observed'] for row in candidates),
                'original_free_median_bytes': median}
    tcp = average([row['tcp']['tcp_consumed_bytes'] for row in centers])
    other = average([row['tcp']['unclassified_consumed_bytes'] for row in centers])
    total = median + tcp + other
    totals = {row['free_bytes'] + row['tcp']['tcp_consumed_bytes'] + row['tcp']['unclassified_consumed_bytes']
              for row in candidates}
    require(totals == {total}, 'Central observations do not share a constant accounted capacity')
    choices = [[row for row in ordered if row['free_bytes'] == value] for value in central_values]
    if len(choices) == 2 and central_values[0] == central_values[1]:
        # Two central observations must be distinct. Choosing the same minimum
        # twice would invent an attribution that no actual median can have.
        values = sorted(row['tcp']['tcp_consumed_bytes'] for row in choices[0])
        lower, upper = average(values[:2]), average(values[-2:])
    else:
        lower = average([min(row['tcp']['tcp_consumed_bytes'] for row in group) for group in choices])
        upper = average([max(row['tcp']['tcp_consumed_bytes'] for row in group) for group in choices])
    require(lower <= tcp <= upper, 'Unbalanced central attribution')
    return {'status': 'complete', 'samples': count,
            'observed_samples': sum(row['tcp']['observed'] for row in rows),
            'central_candidate_samples': len(candidates), 'central_observed_samples': len(candidates),
            'original_free_median_bytes': median,
            'tcp_central_average_bytes': tcp, 'unclassified_central_average_bytes': other,
            'accounted_capacity_bytes': total,
            'tcp_component_range_bytes': [lower, upper],
            'unclassified_component_range_bytes': [total - median - upper, total - median - lower],
            'component_split_unique': lower == upper,
            'equal_free_candidates': [len(group) for group in choices],
            'central_observations': [{'cycle': row['cycle'], 'guest_seconds': row['guest_seconds'],
                                      'free_bytes': row['free_bytes'],
                                      **{key: row['tcp'][key] for key in COUNTERS}}
                                     for row in centers]}


def component_change(earlier, later, expected_loss):
    """Keep signed component changes and their tie ambiguity exactly additive."""
    if earlier['status'] != 'complete' or later['status'] != 'complete':
        return {'status': 'unavailable_busy_samples', 'original_retained_loss_bytes': expected_loss}
    require(earlier['accounted_capacity_bytes'] == later['accounted_capacity_bytes'], 'Heap capacity changed across windows')
    tcp = later['tcp_central_average_bytes'] - earlier['tcp_central_average_bytes']
    other = later['unclassified_central_average_bytes'] - earlier['unclassified_central_average_bytes']
    require(tcp + other == expected_loss, 'Component changes do not equal the original retained loss')
    first, last = earlier['tcp_component_range_bytes'], later['tcp_component_range_bytes']
    bounds = [last[0] - first[1], last[1] - first[0]]
    return {'status': 'complete', 'original_retained_loss_bytes': expected_loss,
            'tcp_growth_bytes': tcp, 'unclassified_growth_bytes': other,
            'tcp_growth_range_bytes': bounds,
            'unclassified_growth_range_bytes': [expected_loss - bounds[1], expected_loss - bounds[0]],
            'component_split_unique': bounds[0] == bounds[1]}


def attribute_trend(series, tcp_series, start, end, warmup=3600, window=3600, phase_period=20):
    """Annotate every original window/phase; busy rows never change its median."""
    finite(start, 'trend start')
    finite(end, 'trend end')
    require(end >= start and len(series) == len(tcp_series) and bool(series), 'Missing paired attribution series')
    paired, previous_time, previous_cycle, capacity = [], None, -2, None
    for row, tcp in zip(series, tcp_series):
        when, cycle = finite(row['guest_seconds'], 'snapshot time'), row['cycle']
        require(type(cycle) is int and cycle == previous_cycle + 1, 'Missing/reordered attribution cycle')
        require(start <= when <= end and (previous_time is None or when > previous_time), 'Unordered/outside attribution time')
        free = integer(row['free_bytes'], 'free heap', 1)
        require(tcp['guest_seconds'] == when and tcp['heap_free_bytes'] == free and
                tcp['label'] == ('ready' if cycle == -1 else 'cycle-' + str(cycle)) and
                type(tcp['observed']) is bool, 'TCP sample belongs to another workload snapshot')
        if tcp['observed']:
            for key in COUNTERS:
                integer(tcp[key], key)
            total = free + tcp['tcp_consumed_bytes'] + tcp['unclassified_consumed_bytes']
            require(capacity is None or capacity == total, 'Free + classified + unclassified capacity changed')
            capacity = total
        else:
            require(isinstance(tcp.get('reason'), str) and tcp['reason'], 'Busy observation lacks its reason')
            require(not any(key in tcp for key in COUNTERS), 'Busy observation falsely supplies numeric attribution')
        paired.append({'guest_seconds': when, 'cycle': cycle, 'free_bytes': free, 'tcp': tcp})
        previous_time, previous_cycle = when, cycle
    original = analyze_trend(series, start, end, warmup, window, phase_period)
    bins = defaultdict(lambda: defaultdict(list))
    for row in paired:
        elapsed = row['guest_seconds'] - start - warmup
        if row['cycle'] >= 0 and elapsed >= 0:
            index = math.floor(elapsed / window)
            if index < original['complete_windows_expected']:
                bins[index][row['cycle'] % phase_period].append(row)
    windows, by_index = [], {}
    for old in original['windows']:
        index = old['index']
        require(set(bins[index]) == set(map(int, old['phases'])), 'Workload phase assignment differs')
        phases = {}
        for phase, summary in old['phases'].items():
            rows = bins[index][int(phase)]
            require(len(rows) == summary['samples'] and min(row['free_bytes'] for row in rows) == summary['minimum'] and
                    max(row['free_bytes'] for row in rows) == summary['maximum'], 'Original phase observations differ')
            phases[phase] = central_components(rows, summary['median'])
        current = {'index': index, 'complete_phase_coverage': old['complete_phase_coverage'], 'phases': phases}
        windows.append(current)
        by_index[index] = current
    usable = [row for row in original['windows'] if row['complete_phase_coverage']]
    phases = {}
    for phase, summary in original['phases'].items():
        selected = [by_index[row['index']]['phases'][phase] for row in usable]
        changes = []
        for position in range(1, len(selected)):
            loss = usable[position - 1]['phases'][phase]['median'] - usable[position]['phases'][phase]['median']
            changes.append({'from_window': usable[position - 1]['index'], 'to_window': usable[position]['index'],
                            **component_change(selected[position - 1], selected[position], loss)})
        phases[phase] = {'original_reasons': summary['reasons'],
                         'all_usable_windows_attributed': all(row['status'] == 'complete' for row in selected),
                         'retained': component_change(selected[0], selected[-1], summary['retained_loss_bytes']),
                         'changes': changes}
    complete = bool(phases) and all(row['all_usable_windows_attributed'] for row in phases.values())
    return {'schema_version': 1, 'original_trend': original,
            'attribution_status': 'insufficient_steady_state_data' if not phases else
                'complete_for_original_usable_windows' if complete else 'partial_busy_observations',
            'accounted_capacity_bytes': capacity, 'paired_snapshots': len(paired),
            'busy_snapshots': sum(not row['tcp']['observed'] for row in paired),
            'windows': windows, 'phases': phases, 'h10_checks_passed': False,
            'all_functionality_verified': False,
            'limitations': ['The original warmup, phase coverage, flags and acceptance criteria are unchanged.',
                'Component changes use the identical central snapshots, not independent component medians.',
                'Equal-free-heap ties can leave more than one valid component split; ranges retain that ambiguity.',
                'Busy samples remain in the original free-heap statistics; unknown central/tied components are not filled with zero.',
                'Unclassified memory is not proved to be a leak or a cache, and TCP ownership is not a waiver.',
                'This is a diagnostic annotation, not proof of 8-hour, 24-hour, hardware or firmware acceptance.']}
