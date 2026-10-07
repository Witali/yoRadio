"""Verify retained physical/QEMU evidence for the scoped low-QMF adapter."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/esp32c3_tests'),str(ROOT/'tools/codec_benchmark')]
from ota import image_info
from ota_diagnostic import serial_health
from summarize_load import summarize_load
from summarize_public_windows import inspect
import run_aac_low_workspace as qemu

EVIDENCE=ROOT/'tests/results/esp32c3-aac-low-production-20261003'
FIRMWARE=ROOT/'firmware/development/esp32c3-aac-low-workspace'
RUNS=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class LowProductionTests(unittest.TestCase):
    def test_saved_firmware_and_physical_build_exclude_test_instrumentation(self):
        manifest=read(FIRMWARE/'manifest.json')
        self.assertEqual(image_info((FIRMWARE/'app.bin').read_bytes()),manifest['image'])
        for name,record in manifest['files'].items():
            self.assertEqual(sha(FIRMWARE/name),record['sha256'])
            self.assertEqual((FIRMWARE/name).stat().st_size,record['bytes'])
        build=read(EVIDENCE/'build-verification.json')
        self.assertEqual(build['elf_sha256'],manifest['image']['app_elf_sha256'])
        self.assertEqual(build['sdkconfig_sha256'],sha(FIRMWARE/'sdkconfig'))
        self.assertEqual(build['config_changes'],{'CONFIG_YORADIO_AAC_LOW_WORKSPACE':[None,'y']})
        self.assertEqual(build['wrapper_disassembly_sha256'],sha(EVIDENCE/'physical-low-wrapper.asm'))
        final=read(EVIDENCE/'final-board.json')
        self.assertEqual(final['board']['app_elf_sha256'],manifest['image']['app_elf_sha256'])
        self.assertTrue(final['status']['audio'])
        config=(FIRMWARE/'sdkconfig').read_text(encoding='utf-8')
        for flag in ('YORADIO_AAC_COMPACT_SBR','YORADIO_AAC_HIGH_HISTORY','YORADIO_AAC_SMOOTHING_HISTORY',
                     'YORADIO_AAC_LOW_WORKSPACE','YORADIO_AAC_PLUS'):
            self.assertIn('CONFIG_'+flag+'=y\n',config)
        for flag in ('YORADIO_QEMU','YORADIO_QEMU_AAC_POINTER_AUDIT','YORADIO_QEMU_AAC_LOW_WORKSPACE',
                     'YORADIO_DEEP_SLEEP_CLOCK','SPI_FLASH_AUTO_SUSPEND'):
            self.assertNotIn('CONFIG_'+flag+'=y\n',config)

    def test_unpoisoned_qemu_path_preserves_all_control_pcm_and_capture_hashes(self):
        config=(EVIDENCE/'qemu/sdkconfig').read_text(encoding='utf-8')
        self.assertIn('CONFIG_YORADIO_AAC_LOW_WORKSPACE=y\n',config)
        self.assertNotIn('CONFIG_YORADIO_QEMU_AAC_LOW_WORKSPACE=y\n',config)
        for name in RUNS:
            folder=EVIDENCE/'qemu'/name
            saved=read(folder/'result.json')
            for key,value in qemu.parse_log((folder/'qemu.log').read_text(encoding='utf-8')).items():
                self.assertEqual(saved[key],value)
            self.assertTrue(saved['production_storage_path'])
            self.assertFalse(saved['transient_row_poisoning'])
            self.assertTrue(saved['precision_pass'])
            self.assertEqual(saved['pcm_vs_previous']['different'],0)
            self.assertEqual(saved['pcm_vs_previous']['samples'],657540)
            self.assertEqual(saved['provenance']['sdkconfig_sha256'],sha(EVIDENCE/'qemu/sdkconfig'))
            self.assertEqual(saved['provenance']['qemu_log_sha256'],sha(folder/'qemu.log'))
            if name!='synthetic':self.assertTrue(saved['capture_identical'])

    def test_control_pcm_equality_from_actual_wave_samples(self):
        previous=ROOT/'tests/results/esp32c3-aac-low-workspace-20261003/control-candidate.wav.gz'
        candidate=EVIDENCE/'qemu/control-candidate.wav.gz'
        audio=[]
        for path in (previous,candidate):
            with wave.open(io.BytesIO(gzip.decompress(path.read_bytes()))) as stream:
                self.assertEqual((stream.getnchannels(),stream.getsampwidth(),stream.getframerate()),(2,2,48000))
                self.assertEqual(stream.getnframes()*stream.getnchannels(),657540)
                audio.append(stream.readframes(stream.getnframes()))
        self.assertEqual(audio[0],audio[1])
        expected=read(EVIDENCE/'qemu/synthetic/result.json')['pcm_vs_previous']['pcm_sha256']
        self.assertEqual(hashlib.sha256(audio[1]).hexdigest(),expected)

    def test_ota_transition_and_roundtrip_preserve_state_and_image(self):
        image=read(FIRMWARE/'manifest.json')['image']
        for name in ('ota-transition','ota-repeat'):
            folder=EVIDENCE/name
            report=read(folder/'report.json')
            self.assertEqual(report.get('target_image',report.get('image')),image)
            self.assertTrue(report['cases'])
            self.assertTrue(all(c['result']=='PASS' for c in report['cases']))
            self.assertEqual(serial_health(read(folder/'performance.json'))['result'],'PASS')
            for case in report['cases']:
                for field in ('wifi_unchanged','settings_unchanged','playlist_unchanged'):
                    self.assertTrue(case['evidence'][field])

    def test_controlled_cpu_comparison_is_recomputed_from_raw_windows(self):
        for name in ('baseline-load','candidate-load'):
            folder=EVIDENCE/name
            report=read(folder/'report.json')
            self.assertTrue(all(c['result']=='PASS' for c in report['cases']))
            self.assertEqual(summarize_load(report,read(folder/'status.json'),read(folder/'performance.json')),
                             read(folder/'summary.json'))
        before=read(EVIDENCE/'baseline-load/report.json')
        after=read(EVIDENCE/'candidate-load/report.json')
        self.assertEqual(before['fixture_hashes'],after['fixture_hashes'])
        self.assertNotEqual(before['board']['app_elf_sha256'],after['board']['app_elf_sha256'])
        self.assertEqual(after['board']['app_elf_sha256'],read(FIRMWARE/'manifest.json')['image']['app_elf_sha256'])

    def test_local_all_codec_matrix_and_stack(self):
        folder=EVIDENCE/'local'
        report=read(folder/'report.json')
        self.assertTrue(all(c['result']=='PASS' for c in report['cases']))
        names={c['name'] for c in report['cases']}
        codecs={'mp3-320':'mp3','flac-level8':'flac','vorbis-q10':'vorbis','opus-510':'opus',
                'aac-lc-320':'aac','lc-22050-mono':'aac','he-44100-stereo':'aac',
                'he-48000-stereo':'aac','hev2-44100-stereo':'aac'}
        self.assertEqual(names,{'restore-board'}|{f'http:{name}:{hint}' for name,codec in codecs.items() for hint in ('auto',codec)})
        rows=read(folder/'performance.json')
        self.assertEqual(serial_health(rows)['result'],'PASS')
        self.assertFalse(any(re.search(r'allocation failed|decode (?:error|failed)',r['line']) for r in rows))
        margins=[int(m[1]) for r in rows if (m:=re.search(r'PERF STACK: name=audio_decode minimum_free=(\d+)',r['line']))]
        self.assertTrue(margins)
        self.assertGreaterEqual(min(margins),1024)

    def test_public_results_keep_measured_outcomes_and_bounded_windows(self):
        summary=read(EVIDENCE/'summary.json')
        self.assertFalse(summary['production_default'])
        self.assertFalse(summary['bounded_suites_all_pass'])
        self.assertFalse(summary['objective_complete'])
        expected_failures={'http':{'http:groovesalad-64-aac':'URLError'},
                           'https':{'https:groovesalad-64-aac':'Runtime allocation/decoder/TLS failure',
                                    'https:groovesalad-16-aac':'URLError'}}
        for protocol in ('http','https'):
            folder=EVIDENCE/protocol
            saved=read(folder/'summary.json')
            self.assertEqual(inspect(folder),saved)
            report=read(folder/'report.json')
            self.assertEqual(report['image'],read(FIRMWARE/'manifest.json')['image'])
            self.assertEqual(report['transport'],protocol)
            self.assertGreaterEqual(report['seconds'],60)
            self.assertTrue(any(c['name'].startswith(protocol+':') for c in report['cases']))
            self.assertEqual({c['name']:c['reason'] for c in report['cases'] if c['result']=='FAIL'},
                             expected_failures[protocol])
            for case in report['cases']:
                retained=next(c for c in summary['cases'][protocol] if c['name']==case['name'])
                self.assertEqual(retained['result'],case['result'])
                self.assertEqual(retained.get('reason'),case.get('reason'))

    def test_exact_implementation_and_raw_evidence_hashes(self):
        manifest=read(EVIDENCE/'implementation.json')
        for name,record in manifest['files'].items():
            self.assertEqual(sha(EVIDENCE/record['snapshot']),record['sha256'],name)
        for name,expected in manifest['evidence'].items():
            self.assertEqual(sha(EVIDENCE/name),expected,name)


if __name__=='__main__':unittest.main()
