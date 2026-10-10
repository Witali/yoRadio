"""Replay the matched C3 Rice screening and reject incomplete telemetry."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-flac-rice-physical-20261008'


def read(name):
    return json.loads((DATA/name).read_text())


class RicePhysicalEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('rice_physical_summary', DATA/'summarize.py')
        cls.summary = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.summary)
        cls.folder = DATA/'physical/control/radio-bossa-lpc32-http'
        cls.data = {name: json.loads((cls.folder/(name+'.json')).read_text())
                    for name in ('report', 'status', 'performance')}
        cls.batch = next(row for row in cls.data['status'] if row['case'].startswith('load:'))

    def summarize_mutation(self, mutate):
        data, batch = copy.deepcopy(self.data), copy.deepcopy(self.batch)
        mutate(data, batch)
        return self.summary.summarize_batch('control', self.folder, batch, data, {})

    def test_exact_archive_and_sources(self):
        index = read('index.json')
        files = {path.relative_to(DATA).as_posix() for path in DATA.rglob('*')
                 if path.is_file() and '__pycache__' not in path.parts}
        self.assertEqual(set(index), files-{'index.json'})
        for name, record in index.items():
            data = (DATA/name).read_bytes()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()),
                             (record['bytes'], record['sha256']), name)
            self.assertNotIn(Path(name).suffix, {'.pcm', '.flac', '.aac', '.key', '.pem', '.bin', '.elf'})
            self.assertNotRegex(data, rb'(?m)^-----BEGIN (?:RSA |EC )?PRIVATE KEY-----')
        for name, digest in read('source-index.json').items():
            self.assertEqual(hashlib.sha256((DATA/'sources'/name).read_bytes()).hexdigest(), digest)

    def test_build_configuration_linked_code_and_ram(self):
        self.assertEqual(read('config-difference.json'), {
            'CONFIG_YORADIO_FLAC_BYTEWISE_RICE': {'control': None, 'candidate': 'y'}})
        audit = read('linked-audit.json')
        self.assertTrue(audit['passed'] and audit['static_internal_ram_unchanged'])
        self.assertEqual(set(audit['allocated_section_changes']), {'.flash.text'})
        self.assertEqual(audit['allocated_section_changes']['.flash.text']['byte_delta'], -186)
        for mode in ('control', 'bytewise'):
            manifest = read('artifacts/'+mode+'/manifest.json')
            artifact = ROOT/'firmware/development'/('esp32c3-idf-6.1-r9a97-flac-rice-'+mode)
            self.assertEqual(hashlib.sha256((artifact/'app.bin').read_bytes()).hexdigest(), manifest['image']['sha256'])
            self.assertEqual(hashlib.sha256((DATA/'artifacts'/mode/'sdkconfig').read_bytes()).hexdigest(), manifest['sdkconfig_sha256'])
            self.assertEqual(audit['records'][mode]['elf_sha256'], manifest['elf_sha256'])
            self.assertTrue(read(mode+'/verify-http.json')['result'] == 'PASS')
            self.assertTrue(read(mode+'/verify-reserve.json')['passed'])
            self.assertFalse(read('artifacts/'+mode+'/qualification.json')['production_qualified'])
        self.assertIn('__clzsi2', (DATA/'bytewise/_Z17readRiceSignedInth-linked.txt').read_text())
        config = (DATA/'sources/idf/esp32c3-oled-native/main/Kconfig.projbuild').read_text()
        block = config.split('config YORADIO_FLAC_BYTEWISE_RICE', 1)[1].split('endmenu', 1)[0]
        self.assertIn('default n', block)

    def test_replay_original_failures_and_restoration(self):
        result = self.summary.summarize(DATA)
        self.assertEqual(result, read('summary.json'))
        self.assertEqual(len(result['cases']), 8)
        self.assertTrue(result['phases_complete'])
        self.assertEqual(result['restored'], 'PASS')
        self.assertTrue(all(result['final_board']['persistence'].values()))
        self.assertTrue(result['final_board']['playback_state_restored'])
        self.assertFalse(result['acceptance_passed'])
        self.assertTrue(result['phase_failures'])
        for case in result['cases']:
            expected = read('artifacts/'+case['mode']+'/manifest.json')['elf_sha256']
            self.assertEqual(case['board']['app_elf_sha256'], expected)
            self.assertEqual(case['original_gates_passed'],
                             all(row['result'] == 'PASS' for row in case['original_acceptance']))
            self.assertFalse(case['dma']['acoustic_continuity_qualified'])
            self.assertAlmostEqual(case['dma']['written_audio_wall_ratio'],
                case['dma']['delta']['written_bytes']/(48000*2*2*case['dma']['observed_seconds']))

    def test_missing_cpu_samples_cannot_be_complete(self):
        def drop(data, batch):
            data['performance'] = [row for row in data['performance'] if 'PERF CPU:' not in row['line']]
        result = self.summarize_mutation(drop)
        self.assertFalse(result['telemetry_complete'])
        self.assertFalse(result['acceptance_passed'])

    def test_malformed_cpu_and_interruption_cannot_be_complete(self):
        def damage(data, batch):
            row = next(row for row in data['performance'] if 'PERF CPU:' in row['line'])
            row['line'] = row['line'].replace('PERF CPU:', 'PERF CPU damaged:')
        self.assertFalse(self.summarize_mutation(damage)['telemetry_complete'])
        def interrupt(data, batch):
            batch['interrupted'] = 'test interrupted'
        result = self.summarize_mutation(interrupt)
        self.assertFalse(result['telemetry_complete'])
        self.assertEqual(result['runtime_acceptance']['result'], 'FAIL')

    def test_missing_dma_and_zero_audio(self):
        def drop_dma(data, batch):
            data['performance'] = [row for row in data['performance'] if 'PERF STAGED_DMA:' not in row['line']]
        self.assertFalse(self.summarize_mutation(drop_dma)['telemetry_complete'])
        def sparse_dma(data, batch):
            selected = [row for row in data['performance']
                        if 'PERF STAGED_DMA:' in row['line'] and
                        batch['started_at']+10 <= row['at'] <= batch['ended_at']][:3]
            data['performance'] = [row for row in data['performance']
                                  if 'PERF STAGED_DMA:' not in row['line'] or row in selected]
        result = self.summarize_mutation(sparse_dma)
        self.assertFalse(result['dma']['coverage_complete'])
        self.assertFalse(result['telemetry_complete'])
        def zero_audio(data, batch):
            for row in data['performance']:
                if 'PERF FLAC:' in row['line']:
                    row['line'] = re.sub(r'\baudio \d+ ms', 'audio 0 ms', row['line'])
        result = self.summarize_mutation(zero_audio)
        self.assertEqual(result['decoded_audio_wall_ratio'], 0)
        self.assertIsNone(result['elapsed_decode_ms_per_audio_second'])

    def test_canonical_runtime_faults_are_preserved(self):
        for line in ('decode failed', 'TLS failure: code=-1', 'assert failed',
                     'Guru Meditation', 'serial capture interrupted', 'ESP-ROM:test',
                     'Runtime watchdog timeout: task_watchdog=true events=1'):
            with self.subTest(line=line):
                def fault(data, batch):
                    data['performance'].append(dict(at=batch['started_at']+20, line=line))
                result = self.summarize_mutation(fault)
                self.assertEqual(result['runtime_acceptance']['result'], 'FAIL')
                self.assertTrue(result['fault_rows'])
                self.assertFalse(result['acceptance_passed'])


if __name__ == '__main__':
    unittest.main()
