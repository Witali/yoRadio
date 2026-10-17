"""Exercise complete evidence rejection and phase-aware runtime trend analysis."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from analyze_runtime import analyze
from runtime_evidence import audit_run, decode, journal_evidence, sha
from runtime_run_guard import inspect_uart
from runtime_state import RuntimeJournal
from runtime_trend import analyze_trend

BOOT = b'ESP-ROM:esp32c2-eco4-20240515\r\nBuild:May 15 2024\r\n'


def snapshot(label, when, free=90000):
    """Model the observer ABI, including a constant cumulative SDK minimum."""
    return {'label': label, 'guest_seconds': when,
            'weather': {'worker_state': 0, 'valid': True, 'humidity': 67, 'generation': round((when - 25) / 60) + 1},
            'heap': {'caps': 4, 'free_bytes': free, 'minimum_free_bytes': 50000,
                     'heaps': [{'caps': 6158, 'free_bytes': free, 'minimum_free_bytes': 50000,
                                'pool_size': 160000}]},
            'tasks': [{'name': 'settings', 'recorded_stack_span_bytes': 2045,
                       'stack_high_water_free_bytes': 480}]}


class RunFixture:
    """Produce real journal-writer output; the auditor must recompute its summary."""
    def __init__(self, root, cycles=4, interval=60, requested=None):
        self.root, self.folder = root, root / 'run'
        self.folder.mkdir()
        (self.folder / 'vm').mkdir()
        files = {}
        for name, data in [('small_tv_reconstructed.elf', b'matched ELF'),
                           ('qemu-system-riscv32.exe', b'test emulator'),
                           ('esp32c2_rev200_rom.elf', b'ROM'), ('rgb-420.jpg', b'x' * 4097),
                           ('guard.py', b'guard identity'), ('runtime_qemu.py', b'workload identity'),
                           ('runtime_weather.py', b'weather observer identity')]:
            path = root / name
            path.write_bytes(data)
            files[name] = path
        app = root / 'app.bin'
        app.write_bytes(b'\0' * 176 + bytes.fromhex(sha(files['small_tv_reconstructed.elf'])))
        files['app.bin'] = app
        self.report = {'schema_version': 4, 'passed': True, 'inputs_unchanged': True, 'no_panic': True,
            'app_sha256': sha(app), 'native_elf_sha256': sha(files['small_tv_reconstructed.elf']),
            'qemu_sha256': sha(files['qemu-system-riscv32.exe']),
            'inputs_sha256': {str(path): sha(path) for path in files.values()},
            'outage_every_cycles': 2, 'duration_requested_guest_seconds': requested,
            'workload_start_guest_seconds': 25, 'workload_end_guest_seconds': 25 + cycles * interval,
            'elapsed_guest_seconds': cycles * interval, 'completed_cycles': cycles,
            'radio_clock_wraps': int((25 + cycles * interval) * 1e6) // 2**32,
            'rom_counter_crosscheck': {'checks': (cycles + 1) * 2,
                                     'rom_elf_sha256': sha(files['esp32c2_rev200_rom.elf'])}}
        self.report.update(weather_coverage_passed=True,
            weather_layout={'elf_sha256': self.report['native_elf_sha256']},
            weather_fixture={'requests': cycles + 1, 'responses_ok': cycles + 1,
                             'all_synthetic_locations': True, 'all_synthetic_keys': True},
            weather_observation={'snapshots': cycles + 1, 'quiescent_samples': cycles + 1,
                'valid_samples': cycles + 1, 'distinct_valid_generations': cycles + 1,
                'first_fresh_guest_seconds': 25, 'last_fresh_guest_seconds': 25 + cycles * interval,
                'maximum_fresh_gap_guest_seconds': interval})
        journal = RuntimeJournal(self.folder / 'events.jsonl')
        journal.append('snapshot', snapshot('ready', 25))
        for cycle in range(cycles):
            for path in ['/setclocktype', '/setgifvalue', '/updateCity']:
                journal.append('http', {'path': path, 'status': 200, 'guest_seconds': .1})
            journal.append('http', {'paths': ['/getsettings', '/get_checkbox_state'],
                                    'request_count': 2, 'guest_seconds': .2})
            if cycle % 4 == 2:
                for path in ['/start_upload', '/upload_chunk', '/upload_chunk', '/finish_upload']:
                    journal.append('http', {'path': path, 'status': 200, 'guest_seconds': .1})
            if (cycle + 1) % 2 == 0:
                journal.append('outage', {'offline_started_guest_seconds': 26 + cycle * interval,
                    'requested_offline_guest_seconds': 1, 'recovered_guest_seconds': 28 + cycle * interval,
                    'ap_online_after': True, 'guest_disconnected': True, 'guest_reconnected': True})
            journal.append('snapshot', snapshot('cycle-' + str(cycle), 25 + (cycle + 1) * interval,
                                                 90000 - (cycle % 20) * 16))
        journal.close()
        self.report['summary'] = journal.summary()
        self.report['journal'] = {'file': 'events.jsonl', 'sha256': sha(self.folder / 'events.jsonl')}
        (self.folder / 'vm/uart.log').write_bytes(BOOT)
        self.save(self.folder / 'vm/session.json', {'name': 'test-vm'})
        self.save(self.folder / 'uptime-guard.json', {'status': 'complete', 'passed': True,
            'workload_passed': True, 'vm_name': 'test-vm', 'last_observation': inspect_uart(BOOT)})
        self.start = root / 'start.json'
        self.save(self.start, {**{key: self.report[key] for key in
            ('app_sha256', 'native_elf_sha256', 'qemu_sha256', 'inputs_sha256')},
            'guard': {'source_file': 'guard.py', 'source_sha256': sha(files['guard.py'])}})
        self.write_report()

    @staticmethod
    def save(path, value):
        """Write an isolated test artifact with actual JSON newlines."""
        path.write_text(json.dumps(value), encoding='utf-8')

    def write_report(self):
        """Persist deliberate fixture mutations before invoking the reader."""
        self.save(self.folder / 'report.json', self.report)

    def audit(self, **kwargs):
        """Bind this run to its independently captured start identities."""
        self.write_report()
        return audit_run(self.folder, self.root, self.start, **kwargs)

    def change_event(self, mutate):
        """Rehash deliberate event corruption so semantic checks must catch it."""
        path = self.folder / 'events.jsonl'
        events = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        mutate(events)
        path.write_text(''.join(json.dumps(row) + '\n' for row in events), encoding='utf-8')
        self.report['journal']['sha256'] = sha(path)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run = RunFixture(Path(self.temp.name))

    def test_complete_short_run_is_audited_but_not_24h(self):
        self.assertEqual(self.run.audit()['evidence']['cycles'], 4)
        result = analyze(self.run.folder, self.run.root, self.run.start)
        self.assertFalse(result['h10_checks_passed'])
        self.assertFalse(result['checks']['observed_at_least_24h'])

    def test_changed_input_even_with_success_flag(self):
        (self.run.root / 'runtime_qemu.py').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Changed runtime input'):
            self.run.audit()

    def test_rehashed_input_cannot_replace_captured_start(self):
        path = self.run.root / 'runtime_qemu.py'
        path.write_bytes(b'changed')
        self.run.report['inputs_sha256'][str(path)] = sha(path)
        with self.assertRaisesRegex(ValueError, 'captured start'):
            self.run.audit()

    def test_journal_digest_and_summary_are_independent_checks(self):
        for field in ['digest', 'summary']:
            with self.subTest(field=field):
                saved = deepcopy(self.run.report)
                if field == 'digest':
                    self.run.report['journal']['sha256'] = '0' * 64
                else:
                    self.run.report['summary']['http_requests'] -= 1
                with self.assertRaisesRegex(ValueError, 'digest|aggregates'):
                    self.run.audit()
                self.run.report = saved

    def test_missing_upload_chunk_rejected_before_aggregate_comparison(self):
        def remove(events):
            events.remove(next(row for row in events if row['kind'] == 'http' and
                               row['data'].get('path') == '/upload_chunk'))
        self.run.change_event(remove)
        with self.assertRaisesRegex(ValueError, 'Incomplete cycle'):
            self.run.audit()

    def test_repeated_cycle_and_invalid_heap_total(self):
        path = self.run.folder / 'events.jsonl'
        original = path.read_bytes()
        for field, value, message in [('label', 'cycle-2', 'cycle'),
                                       ('heap', {'caps': 4, 'free_bytes': 1, 'minimum_free_bytes': 2,
                                                 'heaps': []}, 'heap')]:
            with self.subTest(field=field):
                path.write_bytes(original)
                def change(events):
                    next(row['data'] for row in events if row['kind'] == 'snapshot' and
                         row['data']['label'] == 'cycle-0')[field] = value
                self.run.change_event(change)
                with self.assertRaisesRegex(ValueError, message):
                    self.run.audit()

    def test_guest_reconnect_must_be_real_and_precede_snapshot(self):
        path = self.run.folder / 'events.jsonl'
        original = path.read_bytes()
        for field, value, message in [('guest_disconnected', False, 'disconnect'),
                                      ('recovered_guest_seconds', 100000, 'recovery')]:
            with self.subTest(field=field):
                path.write_bytes(original)
                self.run.change_event(lambda rows: next(row['data'] for row in rows
                    if row['kind'] == 'outage').update({field: value}))
                with self.assertRaisesRegex(ValueError, message):
                    self.run.audit()

    def test_elapsed_wraps_and_rom_calls_cannot_be_forged(self):
        for key, value, message in [('elapsed_guest_seconds', 86400, 'duration'),
                                     ('radio_clock_wraps', 20, 'wrap'),
                                     ('rom_counter_crosscheck', {'checks': 2}, 'crosscheck')]:
            with self.subTest(key=key):
                saved = self.run.report[key]
                self.run.report[key] = value
                with self.assertRaisesRegex(ValueError, message):
                    self.run.audit()
                self.run.report[key] = saved

    def test_silent_reset_overrules_workload_success(self):
        (self.run.folder / 'vm/uart.log').write_bytes(BOOT * 2)
        with self.assertRaisesRegex(ValueError, 'UART'):
            self.run.audit()

    def test_missing_or_torn_weather_observation_is_rejected(self):
        path = self.run.folder / 'events.jsonl'
        original = path.read_bytes()
        for change, message in [(lambda row: row.pop('weather'), 'Missing weather'),
                (lambda row: row['weather'].update(worker_state=1), 'Cache read'),
                (lambda row: row['weather'].update(humidity=41), 'not parsed')]:
            with self.subTest(message=message):
                path.write_bytes(original)
                self.run.change_event(lambda rows: change(rows[0]['data']))
                with self.assertRaisesRegex(ValueError, message):
                    self.run.audit()

    def test_successful_http_without_parsed_weather_is_not_coverage(self):
        self.run.report['weather_fixture']['responses_ok'] = 0
        with self.assertRaisesRegex(ValueError, 'weather responses'):
            self.run.audit()

    def test_failed_guard_overrules_good_uart(self):
        self.run.save(self.run.folder / 'uptime-guard.json', {'status': 'failed', 'vm_name': 'test-vm',
                                                            'last_observation': {'passed': False}})
        with self.assertRaisesRegex(ValueError, 'guard failed'):
            self.run.audit()

    def test_old_preflight_without_guard_is_not_promoted(self):
        (self.run.folder / 'uptime-guard.json').unlink()
        self.assertFalse(self.run.audit()['terminal_guard_verified'])
        self.assertFalse(analyze(self.run.folder, self.run.root, self.run.start)['h10_checks_passed'])

    def test_live_prefix_can_only_be_diagnostic(self):
        del self.run.report['journal'], self.run.report['inputs_unchanged']
        self.run.save(self.run.folder / 'uptime-guard.json', {'status': 'running', 'vm_name': 'test-vm',
                                                           'last_observation': inspect_uart(BOOT)})
        with self.assertRaisesRegex(ValueError, 'not finished'):
            self.run.audit()
        result = analyze(self.run.folder, self.run.root, self.run.start, diagnostic=True)
        self.assertEqual(result['status'], 'pending')
        self.assertFalse(result['h10_checks_passed'])

    def test_truncated_line_and_duplicate_json_fields_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            decode('{"passed":false,"passed":true}')
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            decode('{"time":NaN}')
        path = self.run.folder / 'events.jsonl'
        with path.open('ab') as stream:
            stream.write(b'{"kind":')
        with self.assertRaisesRegex(ValueError, 'Truncated'):
            journal_evidence(path, 2, 2)
        self.assertGreater(journal_evidence(path, 2, 2, allow_partial=True)['trailing_partial_bytes'], 0)


class TrendTests(unittest.TestCase):
    @staticmethod
    def series(loss=lambda hour: 0):
        """Repeat each of 20 phases three times an hour with deterministic jitter."""
        return [{'cycle': cycle, 'guest_seconds': (cycle + 1) * 60,
                 'free_bytes': 90000 - cycle % 20 * 16 + (cycle // 20 % 3 - 1) * 4 - loss(cycle // 60),
                 'sdk_minimum_bytes': 50000} for cycle in range(24 * 60)]

    def test_equal_phases_remove_large_theme_gif_variation(self):
        result = analyze_trend(self.series(), 0, 86400)
        self.assertEqual(result['status'], 'no_decline_flagged_at_observed_resolution')
        self.assertEqual(result['usable_windows'], 23)

    def test_declining_free_heap_with_constant_sdk_minimum_is_flagged(self):
        result = analyze_trend(self.series(lambda hour: hour * 4), 0, 86400)
        self.assertEqual(result['status'], 'retained_loss_requires_explanation')
        self.assertTrue(any('every_steady_window_declines' in row['reasons'] for row in result['flags']))

    def test_one_retained_step_requires_investigation(self):
        result = analyze_trend(self.series(lambda hour: 1024 if hour >= 12 else 0), 0, 86400)
        self.assertTrue(result['flags'])

    def test_warmup_transient_does_not_masquerade_as_a_steady_leak(self):
        result = analyze_trend(self.series(lambda hour: -4096 if hour == 0 else 0), 0, 86400)
        self.assertFalse(result['flags'])

    def test_sparse_or_short_observations_are_insufficient(self):
        for rows, end in [(self.series()[:100], 6000), (self.series()[::20], 86400)]:
            with self.subTest(end=end):
                self.assertEqual(analyze_trend(rows, 0, end)['status'], 'insufficient_steady_state_data')

    def test_outage_phase_is_included_in_hourly_comparisons(self):
        result = analyze_trend(self.series(), 0, 86400, phase_period=60)
        self.assertEqual(result['phase_period_cycles'], 60)
        self.assertFalse(result['flags'])
        self.assertEqual(result['usable_windows'], 23)

    def test_complete_synthetic_day_needs_every_acceptance_condition(self):
        with tempfile.TemporaryDirectory() as temp:
            run = RunFixture(Path(temp), cycles=1440, requested=86400)
            self.assertTrue(analyze(run.folder, run.root, run.start)['h10_checks_passed'])
            self.assertFalse(analyze(run.folder, run.root)['h10_checks_passed'])
            (run.folder / 'uptime-guard.json').unlink()
            self.assertFalse(analyze(run.folder, run.root, run.start)['h10_checks_passed'])

    def test_legacy_day_without_weather_proof_is_not_promoted(self):
        with tempfile.TemporaryDirectory() as temp:
            run = RunFixture(Path(temp), cycles=1440, requested=86400)
            run.report['schema_version'] = 3
            run.write_report()
            self.assertFalse(analyze(run.folder, run.root, run.start)['checks']['weather_refreshed_throughout_workload'])

    def test_a_valid_but_stale_weather_cache_is_not_a_day_of_refreshes(self):
        with tempfile.TemporaryDirectory() as temp:
            run = RunFixture(Path(temp), cycles=1440, requested=86400)
            run.change_event(lambda rows: [row['data']['weather'].update(
                generation=1 if row['data']['label'] == 'ready' else 2)
                for row in rows if row['kind'] == 'snapshot'])
            run.report['summary']['first_snapshot']['weather']['generation'] = 1
            for row in run.report['summary']['snapshot_tail']:
                row['weather']['generation'] = 2
            run.report['weather_observation'].update(distinct_valid_generations=2,
                last_fresh_guest_seconds=85, maximum_fresh_gap_guest_seconds=60)
            run.write_report()
            result = analyze(run.folder, run.root, run.start)
            self.assertFalse(result['h10_checks_passed'])
            self.assertFalse(result['checks']['weather_refreshed_throughout_workload'])


if __name__ == '__main__':
    unittest.main()
