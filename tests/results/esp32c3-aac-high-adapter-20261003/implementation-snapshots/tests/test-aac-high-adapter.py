#!/usr/bin/env python3
"""Guard PCM precision and lifecycle gates for the PC18 production adapter."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import run_aac_high_adapter as runner


class HighAdapterTests(unittest.TestCase):
    def test_retained_production_adapter_evidence(self):
        evidence = ROOT/'tests/results/esp32c3-aac-high-adapter-20261003'
        saved = json.loads((evidence/'adapter/result.json').read_text(encoding='utf-8'))
        log = evidence/'adapter/qemu.log'
        for key, value in runner.parse_log(log.read_text(encoding='utf-8')).items():
            self.assertEqual(saved[key], value)
        for path, key in ((log, 'qemu_log_sha256'), (evidence/'adapter-sdkconfig', 'sdkconfig_sha256')):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), saved['provenance'][key])
        self.assertTrue(saved['precision_pass'])
        self.assertLessEqual(saved['pcm']['max_pcm_error_lsb'], 3)
        self.assertGreater(saved['pcm']['samples'], 600000)
        implementation = json.loads((evidence/'implementation.json').read_text(encoding='utf-8'))
        for name, item in implementation['files'].items():
            self.assertEqual(hashlib.sha256((evidence/item['snapshot']).read_bytes()).hexdigest(),
                             item['sha256'], name)

    def wav(self, folder, name, values, rate=48000):
        path = Path(folder)/name
        with wave.open(str(path), 'wb') as f:
            f.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
            f.writeframes(struct.pack('<'+'h'*len(values), *values))
        return path

    def test_signed_error_and_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            reference = self.wav(folder, 'ref.wav', [-32768, -20, 20, 32767])
            candidate = self.wav(folder, 'new.wav', [-32765, -23, 20, 32764])
            result = runner.compare_pcm(reference, candidate)
            self.assertEqual(result['max_pcm_error_lsb'], 3)
            self.assertEqual(result['different'], 3)
            self.assertAlmostEqual(result['rms_error_lsb'], (27/4)**.5)
            candidate = self.wav(folder, 'new.wav', [-32764, -20, 20, 32767])
            self.assertGreater(runner.compare_pcm(reference, candidate)['max_pcm_error_lsb'], 3)

    def test_reject_changed_duration_rate_and_silence(self):
        with tempfile.TemporaryDirectory() as folder:
            reference = self.wav(folder, 'ref.wav', [1, 2])
            for values, rate in (([1], 48000), ([1, 2], 44100)):
                with self.assertRaises(ValueError):
                    runner.compare_pcm(reference, self.wav(folder, 'new.wav', values, rate))
            silence = self.wav(folder, 'zero.wav', [0, 0])
            with self.assertRaises(ValueError):
                runner.compare_pcm(silence, silence)

    def test_requires_new_memory_and_concurrency_evidence(self):
        log = (ROOT/'tests/results/esp32c3-aac-compact-owner-20261002/adapter/qemu.log').read_text()
        with self.assertRaises(ValueError):
            runner.parse_log(log)
        samples = runner.adapter.parse_log(log)['adapter']['samples']
        added = (f'\nAACCOMPACT_CONCURRENT_PASS decoders=2 samples={samples} pcm_hash=01234567\n'
                 'AACCOMPACT_MEMORY owner_bytes=47980 block_bytes=47984 context_bytes=24\n')
        self.assertEqual(runner.parse_log(log+added)['concurrent']['decoders'], 2)
        for before, after in (('owner_bytes=47980', 'owner_bytes=49708'),
                              ('decoders=2', 'decoders=1'), ('context_bytes=24', 'context_bytes=8')):
            with self.assertRaises(ValueError):
                runner.parse_log(log+added.replace(before, after))


if __name__ == '__main__':
    unittest.main()
