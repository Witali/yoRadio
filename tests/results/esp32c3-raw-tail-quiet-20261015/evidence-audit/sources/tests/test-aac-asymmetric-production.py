"""Verify physical asymmetric-owner evidence; failed playback stays failed."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools/esp32c3_tests'), str(ROOT/'tools/codec_benchmark')]
from ota import image_info
from ota_diagnostic import serial_health
from summarize_load import summarize_load
from summarize_public_windows import inspect
from common import Failure, check_cpu, check_playback
from public_streams import no_runtime_faults
import run_aac_asymmetric_owner as qemu

EVIDENCE = ROOT/'tests/results/esp32c3-aac-asymmetric-production-20261004'
PRIOR = ROOT/'tests/results/esp32c3-aac-low-production-20261003/qemu'
FIRMWARE = ROOT/'firmware/development/esp32c3-aac-asymmetric-owner'
RUNS = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')
SUITES = ('baseline-load', 'baseline-load-retry', 'candidate-load', 'ota-transition',
          'ota-repeat', 'local', 'https', 'https-relocated', 'http', 'candidate-load-relocated')

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


class AsymmetricProductionTests(unittest.TestCase):
    def test_physical_artifact_and_only_one_configuration_change(self):
        manifest = read(FIRMWARE/'manifest.json')
        self.assertEqual(image_info((FIRMWARE/'app.bin').read_bytes()), manifest['image'])
        for name, value in manifest['files'].items():
            self.assertEqual(sha(FIRMWARE/name), value['sha256'])
            self.assertEqual((FIRMWARE/name).stat().st_size, value['bytes'])
        build = read(EVIDENCE/'build-verification.json')
        self.assertEqual(build['config_changes'], {'CONFIG_YORADIO_AAC_ASYMMETRIC_OWNER': [None, 'y']})
        self.assertEqual(build['elf_sha256'], manifest['image']['app_elf_sha256'])
        self.assertEqual(build['sdkconfig_sha256'], sha(FIRMWARE/'sdkconfig'))
        self.assertEqual(build['wrapper_disassembly_sha256'], sha(EVIDENCE/'physical-low-wrapper.asm'))
        self.assertFalse(build['native_symmetric_open_linked'])
        self.assertTrue(build['typed_open_linked'])
        physical = read(EVIDENCE/'physical-patch-audit.json')
        emulator = read(EVIDENCE/'qemu/audit.json')
        for key in ('compiler_layout', 'functions'):
            self.assertEqual(physical[key], emulator[key])
        config = (FIRMWARE/'sdkconfig').read_text()
        for flag in ('YORADIO_AAC_LOW_WORKSPACE', 'YORADIO_AAC_ASYMMETRIC_OWNER', 'YORADIO_AAC_PLUS'):
            self.assertIn('CONFIG_'+flag+'=y\n', config)
        for flag in ('YORADIO_QEMU', 'YORADIO_QEMU_AAC_POINTER_AUDIT', 'YORADIO_QEMU_AAC_LOW_WORKSPACE',
                     'YORADIO_QEMU_AAC_ASYMMETRIC_OWNER', 'YORADIO_DEEP_SLEEP_CLOCK', 'SPI_FLASH_AUTO_SUSPEND'):
            self.assertNotIn('CONFIG_'+flag+'=y\n', config)

    def test_all_unpoisoned_qemu_runs_and_complete_capture_equality(self):
        config = (EVIDENCE/'qemu/sdkconfig').read_text()
        self.assertIn('CONFIG_YORADIO_AAC_ASYMMETRIC_OWNER=y\n', config)
        for flag in ('YORADIO_QEMU_AAC_LOW_WORKSPACE', 'YORADIO_QEMU_AAC_ASYMMETRIC_OWNER'):
            self.assertNotIn('CONFIG_'+flag+'=y\n', config)
        for name in RUNS:
            folder = EVIDENCE/'qemu'/name
            result = read(folder/'result.json')
            for key, value in qemu.parse_log((folder/'qemu.log').read_text()).items():
                self.assertEqual(result[key], value)
            self.assertEqual(result['baseline_sha256'], sha(PRIOR/name/'result.json'))
            self.assertEqual(result['provenance']['sdkconfig_sha256'], sha(EVIDENCE/'qemu/sdkconfig'))
            self.assertEqual(result['provenance']['qemu_log_sha256'], sha(folder/'qemu.log'))
            self.assertTrue(result['production_storage_path'])
            self.assertFalse(result['transient_row_poisoning'])
            self.assertTrue(result['precision_pass'])
            self.assertEqual(result['pcm_vs_previous']['different'], 0)
            self.assertEqual(result['measured_owner_block_saving_bytes'], 4096)
            if name != 'synthetic':
                self.assertTrue(result['capture_identical'])
                previous = read(PRIOR/name/'result.json')['capture']
                for key in ('bytes', 'rate', 'channels', 'samples', 'frames', 'pcm_hash'):
                    self.assertEqual(result['capture'][key], previous[key])

    def test_exact_control_pcm_from_retained_samples(self):
        frames = []
        for path in (PRIOR/'control-candidate.wav.gz', EVIDENCE/'qemu/control-candidate.wav.gz'):
            with wave.open(io.BytesIO(gzip.decompress(path.read_bytes()))) as stream:
                self.assertEqual((stream.getnchannels(), stream.getsampwidth(), stream.getframerate()), (2, 2, 48000))
                self.assertEqual(stream.getnframes()*2, 657540)
                frames.append(stream.readframes(stream.getnframes()))
        self.assertEqual(frames[0], frames[1])

    def test_cpu_comparison_recomputed_and_timeouts_preserved(self):
        for name in ('baseline-load-retry', 'candidate-load'):
            folder = EVIDENCE/name
            report, status, perf = (read(folder/f) for f in ('report.json', 'status.json', 'performance.json'))
            self.assertEqual(summarize_load(report, status, perf), read(folder/'summary.json'))
            self.assertTrue(any(c['result'] == 'FAIL' for c in report['cases']))
            self.assertEqual(serial_health(perf)['result'], 'PASS')
        initial = read(EVIDENCE/'baseline-load/report.json')
        self.assertEqual([c['result'] for c in initial['cases']], ['PASS', 'FAIL', 'FAIL', 'FAIL'])
        failed = next(batch for batch in read(EVIDENCE/'candidate-load/status.json') if 'interrupted' in batch)
        self.assertEqual(failed['exception_chain'], [{'type': 'URLError'}, {'type': 'TimeoutError'}])
        self.assertLess(failed['elapsed_seconds'], 40)

    def test_ota_transition_target_and_settings(self):
        folder = EVIDENCE/'ota-transition'
        report = read(folder/'report.json')
        self.assertEqual(report['target_image'], read(FIRMWARE/'manifest.json')['image'])
        self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
        self.assertEqual(serial_health(read(folder/'performance.json'))['result'], 'PASS')
        for case in report['cases']:
            for field in ('wifi_unchanged', 'settings_unchanged', 'playlist_unchanged'):
                self.assertTrue(case['evidence'][field])
        folder = EVIDENCE/'ota-repeat'
        repeat = read(folder/'report.json')
        self.assertEqual(repeat['image'], read(FIRMWARE/'manifest.json')['image'])
        self.assertEqual({c['name'] for c in repeat['cases']}, {
            'ota:roundtrip:1', 'ota:roundtrip:2', 'ota:while-playing', 'restore-saved-station'})
        self.assertTrue(all(c['result'] == 'PASS' for c in repeat['cases']))
        self.assertEqual(serial_health(read(folder/'performance.json'))['result'], 'PASS')
        for case in repeat['cases']:
            for field in ('wifi_unchanged', 'settings_unchanged', 'playlist_unchanged'):
                self.assertTrue(case['evidence'][field])
        final = read(EVIDENCE/'final-board.json')
        self.assertEqual(final['board']['app_elf_sha256'], read(FIRMWARE/'manifest.json')['image']['app_elf_sha256'])
        self.assertTrue(final['status']['audio'])

    def test_complete_case_inventory_and_actual_public_outcomes(self):
        codecs = {'mp3-320': 'mp3', 'flac-level8': 'flac', 'vorbis-q10': 'vorbis', 'opus-510': 'opus',
                  'aac-lc-320': 'aac', 'lc-22050-mono': 'aac', 'he-44100-stereo': 'aac',
                  'he-48000-stereo': 'aac', 'hev2-44100-stereo': 'aac'}
        local = read(EVIDENCE/'local/report.json')
        names = {c['name'] for c in local['cases']}
        self.assertEqual(names, {'restore-board'} | {f'http:{n}:{h}' for n, c in codecs.items() for h in ('auto', c)})
        self.assertTrue(all(c['result'] == 'PASS' for c in local['cases']))
        no_runtime_faults(read(EVIDENCE/'local/performance.json'))
        for protocol in ('http', 'https'):
            folder = EVIDENCE/protocol
            report = read(folder/'report.json')
            self.assertEqual(inspect(folder), read(folder/'summary.json'))
            self.assertEqual(report['image'], read(FIRMWARE/'manifest.json')['image'])
            self.assertEqual(report['seconds'], 60)
            self.assertEqual(report['interval'], .1)
            self.assertEqual(len([c for c in report['cases'] if c['name'].startswith(protocol+':')]), 5)
        summary = read(EVIDENCE/'summary.json')
        self.assertFalse(summary['production_default'])
        self.assertFalse(summary['bounded_suites_all_pass'])
        self.assertFalse(summary['objective_complete'])
        for name in SUITES:
            report = read(EVIDENCE/name/'report.json')
            expected = [dict(name=c['name'], result=c['result'],
                             **({'reason': c['reason']} if 'reason' in c else {})) for c in report['cases']]
            self.assertEqual(summary['cases'][name], expected)

    def test_relocated_https_repeat_rechecks_raw_playback_and_memory(self):
        folder = EVIDENCE/'https-relocated'
        report = read(folder/'report.json')
        self.assertEqual(report['seconds'], 120)
        self.assertEqual(inspect(folder), read(folder/'summary.json'))
        self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
        name = 'groovesalad-64-aac'
        samples = next(b['samples'] for b in read(folder/'status.json') if b['case'] == name)
        spec = report['reference_probes'][name]['spec']
        self.assertEqual((spec['codec'], spec['profile'], spec['rate'], spec['channels']), ('aac', 'HE-AAC', 44100, 2))
        check_playback(samples, spec, minimum=63, warmup=15)
        self.assertLess(max(s['request_ms'] for s in samples), 2000)
        window = report['windows'][name]
        rows = read(folder/'performance.json')
        self.assertEqual(serial_health(rows)['result'], 'PASS')
        # Restoration deliberately reboots after playback. Audit only the
        # recorded playback window for unexpected resets, as the runner does.
        no_runtime_faults([r for r in rows if window['start'] <= r['at'] < window['end']])
        check_cpu([r for r in rows if window['start']+15 <= r['at'] < window['end']],
                  start=window['start']+15, end=window['end'])

    def test_relocated_load_keeps_three_profiles_and_stack(self):
        folder = EVIDENCE/'candidate-load-relocated'
        report, status, perf = (read(folder/f) for f in ('report.json', 'status.json', 'performance.json'))
        self.assertEqual(summarize_load(report, status, perf), read(folder/'summary.json'))
        self.assertTrue(all(c['result'] == 'PASS' for c in report['cases']))
        self.assertEqual({c['name'] for c in report['cases']}, {'restore-board'} | {
            'cpu-under-http-load:'+name for name in ('lc-48000-stereo', 'he-48000-stereo', 'hev2-44100-stereo')})
        no_runtime_faults(perf)
        margins = [int(m[1]) for row in perf if (m := re.search(r'name=audio_decode minimum_free=(\d+)', row['line']))]
        self.assertGreaterEqual(min(margins), 1024)

    def test_public_memory_failures_reproduced_from_raw_windows(self):
        for protocol, name, reason in (
                ('https', 'groovesalad-64-aac', 'Progressive heap loss during continuous playback'),
                ('http', 'groovesalad-32-aac', 'Progressive largest loss during continuous playback')):
            folder = EVIDENCE/protocol
            report = read(folder/'report.json')
            case = next(c for c in report['cases'] if c['name'] == protocol+':'+name)
            self.assertEqual((case['result'], case['reason']), ('FAIL', reason))
            window = report['windows'][name]
            rows = [r for r in read(folder/'performance.json') if window['start']+15 <= r['at'] < window['end']]
            with self.assertRaisesRegex(Failure, '^'+reason+'$'):
                check_cpu(rows, start=window['start']+15, end=window['end'])

    def test_exact_sources_including_both_versions_of_the_runner(self):
        manifest = read(EVIDENCE/'implementation.json')
        for name, record in manifest['files'].items():
            self.assertEqual(sha(EVIDENCE/record['snapshot']), record['sha256'], name)
        for name, digest in manifest['evidence'].items():
            self.assertEqual(sha(EVIDENCE/name), digest, name)
        for name in SUITES:
            for path, digest in read(EVIDENCE/name/'report.json').get('test_sources_sha256', {}).items():
                self.assertEqual(sha(EVIDENCE/manifest['runner_sources'][path+'@'+digest]), digest)


if __name__ == '__main__': unittest.main()
