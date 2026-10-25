"""Check additive median attribution without weakening the original trend rules."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import statistics
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from runtime_tcp_trend import COUNTERS, attribute_trend, central_components
from runtime_trend import analyze_trend


def fixture(assign=None, windows=3, samples=2, period=20, tail=0, start=0):
    """Build explicitly synthetic paired counters with a constant 100000-byte capacity."""
    assign = assign or (lambda window, phase, within: (90000 - phase * 4 - window * 16 + within * 4, 80 + window * 4))
    memory = [{'cycle': -1, 'guest_seconds': start, 'free_bytes': 90000, 'sdk_minimum_bytes': 50000}]
    tcp = []
    interval = 120 / (samples * period)
    for cycle in range(windows * samples * period + tail):
        window, offset = divmod(cycle, samples * period)
        within, phase = divmod(offset, period)
        free, network = assign(window, phase, within)
        memory.append({'cycle': cycle, 'guest_seconds': start + (cycle + .5) * interval,
                       'free_bytes': free, 'sdk_minimum_bytes': 50000})
    for row in memory:
        cycle = row['cycle']
        if cycle < 0:
            network = 80
        else:
            window, offset = divmod(cycle, samples * period)
            within, phase = divmod(offset, period)
            _, network = assign(window, phase, within)
        tcp.append({'label': 'ready' if cycle < 0 else 'cycle-' + str(cycle),
                    'guest_seconds': row['guest_seconds'], 'heap_free_bytes': row['free_bytes'], 'observed': True,
                    'tcp_consumed_bytes': network, 'unclassified_consumed_bytes': 100000 - row['free_bytes'] - network,
                    'tcp_blocks': 1, 'unclassified_blocks': 3, 'pcbs': 1, 'segments': 0, 'pbufs': 0,
                    'time_wait_pcbs': 0, 'unregistered_pcbs': 0})
    return memory, tcp, start, start + windows * 120 + tail * interval


def busy(row):
    """Keep the real free-heap sample while making its TCP attribution unknown."""
    row['observed'], row['reason'] = False, 'tcpip-running'
    for key in COUNTERS:
        row.pop(key)


class AttributionTests(unittest.TestCase):
    """Retain original flags, windows, missing coverage and signed byte changes."""
    def analyze(self, data=None, **parameters):
        """Use short windows only in declared mathematical fixtures, never in CLI acceptance."""
        memory, tcp, start, end = data or fixture()
        parameters = {'warmup': 0, 'window': 120, 'phase_period': 20} | parameters
        result = attribute_trend(memory, tcp, start, end, **parameters)
        self.assertEqual(result['original_trend'], analyze_trend(memory, start, end, **parameters))
        self.assertFalse(result['h10_checks_passed'])
        self.assertFalse(result['all_functionality_verified'])
        return result

    def test_original_flags_statistics_and_windows_are_unchanged(self):
        result = self.analyze()
        self.assertTrue(result['original_trend']['flags'])
        self.assertEqual(result['attribution_status'], 'complete_for_original_usable_windows')
        self.assertEqual(result['phases']['0']['retained']['original_retained_loss_bytes'], 32)

    def test_independent_component_medians_are_not_added(self):
        data = fixture(lambda w, p, i: ([89900, 90000, 90100][i], [80, 1080, 80][i]), samples=3)
        result = self.analyze(data)
        center = result['windows'][0]['phases']['0']
        self.assertEqual(center['tcp_central_average_bytes'], 1080)
        self.assertEqual(center['unclassified_central_average_bytes'], 8920)
        unrelated_tcp_median = statistics.median([80, 1080, 80])
        unrelated_other_median = statistics.median([10020, 8920, 9820])
        self.assertNotEqual(unrelated_tcp_median + unrelated_other_median, 10000)
        self.assertEqual(center['original_free_median_bytes'] + center['tcp_central_average_bytes'] +
                         center['unclassified_central_average_bytes'], 100000)

    def test_signed_growth_can_include_tcp_release(self):
        data = fixture(lambda w, p, i: (90000 - w * 6, 292 if w == 0 else 80))
        change = self.analyze(data)['phases']['0']['retained']
        self.assertEqual(change['original_retained_loss_bytes'], 12)
        self.assertEqual(change['tcp_growth_bytes'], -212)
        self.assertEqual(change['unclassified_growth_bytes'], 224)

    def test_even_median_uses_two_actual_central_observations(self):
        data = fixture(lambda w, p, i: (89900 + i * 200, 80 + i * 212))
        row = self.analyze(data)['windows'][0]['phases']['0']
        self.assertEqual(row['original_free_median_bytes'], 90000)
        self.assertEqual(row['tcp_central_average_bytes'], 186)
        self.assertEqual(len(row['central_observations']), 2)
        self.assertTrue(row['component_split_unique'])

    def test_odd_equal_free_ties_preserve_attribution_range(self):
        data = fixture(lambda w, p, i: (90000, [80, 292, 504][i]), samples=3)
        row = self.analyze(data)['windows'][0]['phases']['0']
        self.assertEqual(row['tcp_central_average_bytes'], 292)
        self.assertEqual(row['tcp_component_range_bytes'], [80, 504])
        self.assertFalse(row['component_split_unique'])

    def test_even_equal_free_ties_require_distinct_observations(self):
        data = fixture(lambda w, p, i: (90000, [80, 120, 212, 504][i]), samples=4)
        row = self.analyze(data)['windows'][0]['phases']['0']
        self.assertEqual(row['tcp_central_average_bytes'], 166)
        self.assertEqual(row['tcp_component_range_bytes'], [100, 358])
        self.assertEqual(row['equal_free_candidates'], [4, 4])

    def test_two_different_central_values_have_separate_tie_groups(self):
        data = fixture(lambda w, p, i: ([85000, 86000, 86000, 87000, 87000, 88000][i],
                                       [80, 80, 120, 292, 504, 80][i]), samples=6)
        row = self.analyze(data)['windows'][0]['phases']['0']
        self.assertEqual(row['original_free_median_bytes'], 86500)
        self.assertEqual(row['tcp_central_average_bytes'], 206)
        self.assertEqual(row['tcp_component_range_bytes'], [186, 312])

    def test_retained_growth_ranges_do_not_hide_tie_ambiguity(self):
        data = fixture(lambda w, p, i: (90000 - w * 6, [80, 120, 212, 504][i] + w * 8), samples=4)
        row = self.analyze(data)['phases']['0']['retained']
        self.assertEqual(row['tcp_growth_bytes'], 16)
        self.assertEqual(row['unclassified_growth_bytes'], -4)
        self.assertEqual(row['tcp_growth_range_bytes'], [-242, 274])
        self.assertEqual(row['unclassified_growth_range_bytes'], [-262, 254])
        self.assertFalse(row['component_split_unique'])

    def test_busy_central_sample_is_not_replaced_with_zero(self):
        data = fixture(lambda w, p, i: (89900 + i * 100, 80), samples=3)
        busy(data[1][21])  # cycle20: middle of phase0 in window0.
        result = self.analyze(data)
        row = result['windows'][0]['phases']['0']
        self.assertEqual(result['attribution_status'], 'partial_busy_observations')
        self.assertEqual(row['status'], 'unavailable_busy_samples')
        self.assertNotIn('tcp_central_average_bytes', row)
        self.assertNotIn('tcp_growth_bytes', result['phases']['0']['retained'])

    def test_busy_equal_free_candidate_prevents_false_unique_split(self):
        data = fixture(lambda w, p, i: (90000, 80 + i * 4), samples=3)
        busy(data[1][1])
        row = self.analyze(data)['windows'][0]['phases']['0']
        self.assertEqual(row['central_candidate_samples'], 3)
        self.assertEqual(row['central_observed_samples'], 2)
        self.assertEqual(row['status'], 'unavailable_busy_samples')

    def test_busy_noncentral_sample_keeps_its_free_heap_without_hiding_known_centers(self):
        data = fixture(lambda w, p, i: (89900 + i * 100, 80), samples=3)
        busy(data[1][1])
        result = self.analyze(data)
        row = result['windows'][0]['phases']['0']
        self.assertEqual(result['busy_snapshots'], 1)
        self.assertEqual(row['observed_samples'], 2)
        self.assertEqual(row['samples'], 3)
        self.assertEqual(row['tcp_central_average_bytes'], 80)
        self.assertEqual(row['status'], 'complete')

    def test_all_busy_observations_still_preserve_original_flags(self):
        data = fixture()
        for row in data[1]:
            busy(row)
        result = self.analyze(data)
        self.assertIsNone(result['accounted_capacity_bytes'])
        self.assertEqual(result['attribution_status'], 'partial_busy_observations')
        self.assertTrue(result['original_trend']['flags'])

    def test_busy_sample_cannot_supply_fake_numeric_attribution(self):
        data = fixture()
        busy(data[1][1])
        data[1][1]['tcp_consumed_bytes'] = 0
        with self.assertRaisesRegex(ValueError, 'falsely supplies'):
            self.analyze(data)

    def test_warmup_and_exact_boundary_use_original_assignment(self):
        data = fixture(lambda w, p, i: (80000 if w == 0 else 90000, 80), windows=4)
        data[0][41]['guest_seconds'] = data[1][41]['guest_seconds'] = 120
        result = self.analyze(data, warmup=120)
        self.assertEqual(result['original_trend']['usable_windows'], 3)
        self.assertFalse(result['original_trend']['flags'])

    def test_final_incomplete_window_is_not_added_to_the_steady_comparison(self):
        result = self.analyze(fixture(windows=4, tail=20))
        self.assertEqual(result['paired_snapshots'], 181)
        self.assertEqual(len(result['windows']), 4)

    def test_original_missing_phase_coverage_is_not_promoted(self):
        result = self.analyze(window=30)
        self.assertEqual(result['original_trend']['status'], 'insufficient_steady_state_data')
        self.assertEqual(result['attribution_status'], 'insufficient_steady_state_data')

    def test_outage_phase_period_stays_sixty(self):
        result = self.analyze(fixture(period=60), phase_period=60)
        self.assertEqual(result['original_trend']['phase_period_cycles'], 60)
        self.assertEqual(len(result['phases']), 60)

    def test_unpaired_reordered_or_relabelled_observations_are_rejected(self):
        for case in ('missing', 'reordered', 'time', 'label', 'free', 'cycle'):
            data = fixture()
            if case == 'missing': data[1].pop()
            elif case == 'reordered': data[1][1], data[1][2] = data[1][2], data[1][1]
            elif case == 'time': data[1][1]['guest_seconds'] += 1
            elif case == 'label': data[1][1]['label'] = 'cycle-20'
            elif case == 'free': data[1][1]['heap_free_bytes'] += 4
            else: data[0][1]['cycle'] = 2
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.analyze(data)

    def test_accounting_capacity_cannot_drift(self):
        data = fixture()
        data[1][-1]['unclassified_consumed_bytes'] += 4
        with self.assertRaisesRegex(ValueError, 'capacity changed'):
            self.analyze(data)

    def test_invalid_numeric_inputs_are_not_accepted(self):
        for case in ('nan-time', 'boolean-free', 'negative-component', 'boolean-observed', 'outside-end'):
            data = fixture()
            if case == 'nan-time': data[0][1]['guest_seconds'] = float('nan')
            elif case == 'boolean-free': data[0][1]['free_bytes'] = True
            elif case == 'negative-component': data[1][1]['tcp_consumed_bytes'] = -4
            elif case == 'boolean-observed': data[1][1]['observed'] = 1
            else: data[0][-1]['guest_seconds'] = data[3] + 1
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.analyze(data)

    def test_direct_central_math_checks_accounting_not_only_its_own_sum(self):
        memory, tcp, _, _ = fixture(samples=2)
        selected = [{'cycle': memory[index]['cycle'], 'guest_seconds': memory[index]['guest_seconds'],
                     'free_bytes': memory[index]['free_bytes'], 'tcp': tcp[index]} for index in (1, 21)]
        selected[1]['tcp']['unclassified_consumed_bytes'] += 4
        with self.assertRaisesRegex(ValueError, 'constant accounted capacity'):
            central_components(selected, statistics.median(row['free_bytes'] for row in selected))

    def test_absolute_start_offset_does_not_change_the_phase_result(self):
        first = self.analyze(fixture())
        shifted = self.analyze(fixture(start=25))
        self.assertEqual(first['original_trend'], shifted['original_trend'])
        self.assertEqual(first['phases'], shifted['phases'])


def main():
    """Save actual mathematical test results without claiming VM or firmware acceptance."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    files = [Path(__file__), root / 'tools/runtime_tcp_trend.py', root / 'tools/runtime_trend.py',
             root / 'tools/runtime_evidence.py', root / 'tools/runtime_run_guard.py']
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    pins = {str(path): sha(path) for path in files}
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AttributionTests))
    unchanged = pins == {str(path): sha(path) for path in files}
    report = dict(passed=result.wasSuccessful() and unchanged, tests=result.testsRun,
                  inputs_sha256=pins, inputs_unchanged=unchanged, no_vm_or_hardware_access=True,
                  all_functionality_verified=False, h10_checks_passed=False,
                  scope='Synthetic paired mathematical fixtures; actual journal replay is a separate check.',
                  failures=[str(case) for case, _ in result.failures], errors=[str(case) for case, _ in result.errors])
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
