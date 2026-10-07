"""Replay physical heap-owner observations without hiding failed load gates."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/results/esp32c3-heap-fragment-20261005'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from heap_fragment import analyze
from ota_diagnostic import serial_health
from summarize_codec_sequence import summarize


def read(path):
    data = path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix('.json.gz').read_bytes())
    return json.loads(data)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class HeapFragmentEvidence(unittest.TestCase):
    def test_exact_evidence_and_host_sanitizers(self):
        manifest = read(DATA / 'manifest.json')
        files = {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                 if p.is_file() and p.name != 'manifest.json'}
        self.assertEqual(files, set(manifest))
        for path, value in manifest.items():
            data = (DATA / path).read_bytes()
            self.assertEqual(len(data), value['bytes'], path)
            self.assertEqual(sha(data), value['sha256'], path)
        for name in ('host', 'host-initial'):
            report = read(DATA / name / 'report.json')
            self.assertTrue(report['passed'])
            for path, digest in report['source_sha256'].items():
                self.assertEqual(sha((DATA / name / 'sources' / path).read_bytes()), digest)
            self.assertIn('PASS arm/range/task/ISR/realloc-failure', (DATA / name / 'run.log').read_text())

    def test_complete_owner_snapshots_and_quiet_idle(self):
        for name, count, start, peak, events in (
                ('sequence', 14, 1, 57, 36850), ('idle', 29, 18, 57, 36850),
                ('rtc-sequence', 9, 1, 53, 24883)):
            result = analyze(read(DATA / name / 'performance.json'))
            self.assertEqual(result, read(DATA / name / 'owners.json'))
            snapshots = result['snapshots']
            self.assertEqual(len(snapshots), count)
            self.assertEqual(snapshots[0]['seq'], start)
            self.assertEqual(max(s['peak'] for s in snapshots), peak)
            for row in snapshots:
                self.assertEqual(row['live'], 0)
                self.assertEqual(row['rows'], 1)
                self.assertEqual(row['largest_raw_free'], 115616)
            self.assertEqual(snapshots[-1]['alloc_events'], events)
            self.assertEqual(snapshots[-1]['free_events'], events)
        idle = read(DATA / 'idle/report.json')
        quiet = idle['quiet_window']
        self.assertGreaterEqual(quiet['ended_at'] - quiet['started_at'], 130)
        self.assertEqual(quiet['http_polls'], 0)
        self.assertTrue(all(c['result'] == 'PASS' for c in idle['cases']))

    def test_failures_preserved_and_recovery_from_first_baseline(self):
        for folder, saved in (('sequence', 'sequence-summary.json'),
                              ('rtc-sequence', 'rtc-summary.json'),
                              ('opus-delivery', 'delivery-summary.json')):
            result = summarize(*(read(DATA / folder / n) for n in
                                 ('report.json', 'status.json', 'performance.json')))
            expected = read(DATA / saved)
            expected.pop('sender_runs', None)
            self.assertEqual(result, expected)
            for item in result['cases'].values():
                self.assertEqual(item['original_acceptance']['result'], 'FAIL')
                self.assertEqual(item['idle_after']['largest'], 114688)
                self.assertEqual(item['idle_after']['tasks'], 17)
                self.assertEqual(item['recovery_from_first']['result'], 'PASS')
                if folder == 'opus-delivery':
                    self.assertEqual(item['original_acceptance']['reason'], 'Incomplete CPU/heap evidence')
                    self.assertEqual(item['after_40_seconds']['result'], 'FAIL')
                else:
                    self.assertEqual(item['original_acceptance']['reason'], 'Progressive heap loss during continuous playback')
                    if folder == 'rtc-sequence' and 'mp3' in item['original_acceptance']['name']:
                        self.assertEqual(item['after_40_seconds'], dict(result='FAIL', reason='Progressive heap loss during continuous playback'))
                    else:
                        self.assertEqual(item['after_40_seconds']['result'], 'PASS')
            self.assertEqual(serial_health(read(DATA / folder / 'performance.json'))['result'], 'PASS')
        damaged = [r for r in read(DATA / 'opus-delivery/performance.json')
                   if 'PERF CPU:' in r['line'] and
                   set(re.findall(r'(busy|idle|heap|largest)=', r['line'])) != {'busy', 'idle', 'heap', 'largest'}]
        self.assertEqual(len(damaged), 1)
        self.assertIn('heapw=0', damaged[0]['line'])

    def test_images_layout_and_ota_restore(self):
        control = read(ROOT / 'firmware/development/esp32c3-custom-terminal/manifest.json')
        builds = []
        for folder, variant, rtc_extra, bss_extra in (
                ('verify', 'esp32c3-heap-fragment-probe', 3072, 56),
                ('verify-rtc', 'esp32c3-heap-fragment-rtc', 3128, 0)):
            build = read(DATA / folder / 'build.json')
            builds.append(build)
            artifact = ROOT / 'firmware/development' / variant
            app = (artifact / 'app.bin').read_bytes()
            self.assertEqual(sha(app), build['app_sha256'])
            self.assertEqual(app[176:208].hex(), build['elf_sha256'])
            self.assertEqual(sha((artifact / 'sdkconfig').read_bytes()), build['sdkconfig_sha256'])
            config = (artifact / 'sdkconfig').read_text()
            for key in ('YORADIO_HEAP_FRAGMENT_PROBE', 'HEAP_PLACE_FUNCTION_INTO_FLASH', 'HEAP_USE_HOOKS'):
                self.assertIn('CONFIG_' + key + '=y', config)
            self.assertNotIn('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y', config)
            for key in ('types', 'features'):
                self.assertEqual(build[key], control[key])
            for section in ('.iram0.text', '.dram0.data'):
                self.assertEqual(build['sections'][section], control['sections'][section])
            self.assertEqual(build['sections']['.dram0.bss'] - control['sections']['.dram0.bss'], bss_extra)
            self.assertEqual(build['sections']['.rtc.data'] - 2688, rtc_extra)
            self.assertEqual(len(build['fragment_probe_calls']), 6)
            for path, digest in build['source_sha256'].items():
                self.assertEqual(sha((DATA / folder / 'sources' / path).read_bytes()), digest)
            self.assertTrue(read(artifact / 'manifest.json')['hardware_tested'])
            self.assertFalse(read(artifact / 'manifest.json')['production_qualified'])
        layout = read(DATA / 'layout-comparison.json')
        for section in ('.iram0.text', '.dram0.data', '.dram0.bss'):
            self.assertEqual(layout['control'][section], layout['probe'][section])
        for folder, target in zip(('ota-probe', 'ota-rtc', 'ota-restore'), [*builds, control]):
            report = read(DATA / folder / 'report.json')
            self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
            evidence = report['cases'][0]['evidence']
            self.assertEqual(evidence['after']['app_elf_sha256'], target['elf_sha256'])
            for key in ('settings_unchanged', 'wifi_unchanged', 'playlist_unchanged'):
                self.assertTrue(evidence[key])
            health = serial_health(read(DATA / folder / 'performance.json'))
            if folder == 'ota-probe':
                self.assertEqual(health['result'], 'FAIL')
                self.assertEqual(len(health['evidence']['faults']), 1)
                self.assertIn('incomplete final line', health['evidence']['faults'][0]['line'])
            else:
                self.assertEqual(health['result'], 'PASS')
        final = read(DATA / 'board-final.json')
        self.assertEqual(final['image']['app_elf_sha256'], control['elf_sha256'])
        self.assertTrue(final['status']['audio'])

    def test_delivery_windows_account_for_completed_socket_writes(self):
        for folder, summaries in read(DATA / 'delivery-summary.json')['sender_runs'].items():
            events = read(DATA / folder / 'report.json')['server_events']
            self.assertEqual(len(events), len(summaries))
            for event, saved in zip(events, summaries):
                delivery = event['delivery']
                windows = delivery['windows']
                self.assertTrue(delivery['finished'])
                self.assertEqual(delivery['dropped_windows'], 0)
                self.assertEqual(sum(w['bytes'] for w in windows), event['sent'])
                self.assertEqual(saved['recorded_bytes'], event['sent'])
                self.assertEqual(saved['windows'], len(windows))
                self.assertEqual(saved['max_write_seconds'], max(w['max_write_seconds'] for w in windows))
                self.assertEqual(saved['max_late_seconds'], max(w['max_late_seconds'] for w in windows))
                self.assertEqual(event['pacing_ratio'], 1.02)
                for a, b in zip(windows, windows[1:]):
                    self.assertEqual(a['ended_at'], b['started_at'])
                    self.assertGreaterEqual(a['ended_at'], a['started_at'])
                    self.assertGreaterEqual(a['write_seconds'], a['max_write_seconds'])

    def test_runner_dependencies_retained_by_hash(self):
        used = ('common', 'run', 'diagnostic', 'heap_idle', 'heap_fragment', 'memory',
                'ota', 'ota_transition', 'ota_diagnostic', 'serial_lines', 'server', 'fixtures', 'generate_stress')
        for folder in ('ota-probe', 'sequence', 'idle', 'ota-rtc', 'rtc-sequence', 'ota-restore', 'opus-delivery'):
            for path, digest in read(DATA / folder / 'report.json')['test_sources_sha256'].items():
                if Path(path).stem in used:
                    self.assertEqual(sha((DATA / 'runner-sources' / digest / Path(path).name).read_bytes()), digest)


if __name__ == '__main__':
    unittest.main()
