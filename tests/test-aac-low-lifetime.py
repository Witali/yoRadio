#!/usr/bin/env python3
"""Validate real-decoder QMF lifetime evidence and its negative control."""
import hashlib
import gzip
import io
import json
from pathlib import Path
import re
import math
import struct
import sys
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
import run_aac_low_lifetime as runner
EVIDENCE=ROOT/'tests/results/esp32c3-aac-low-lifetime-20261003'
BASELINE=ROOT/'tests/results/esp32c3-aac-pointer-audit-20261003'
RUNS=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LowLifetimeTests(unittest.TestCase):
    def test_retained_control_audio_recomputes_error_statistics(self):
        streams={}
        wavs={}
        for name in ('reference','positive','negative'):
            raw=gzip.decompress((EVIDENCE/f'control-{name}.wav.gz').read_bytes())
            wavs[name]=raw
            with wave.open(io.BytesIO(raw)) as audio:
                self.assertEqual((audio.getnchannels(),audio.getsampwidth(),audio.getframerate()),(2,2,48000))
                streams[name]=audio.readframes(audio.getnframes())
        self.assertEqual(streams['reference'],streams['positive'])
        self.assertEqual(len(streams['reference']),len(streams['negative']))
        errors=[abs(a[0]-b[0]) for a,b in zip(struct.iter_unpack('<h',streams['reference']),
                                           struct.iter_unpack('<h',streams['negative']))]
        saved=read(EVIDENCE/'negative-history/result.json')['pcm_without_poison']
        self.assertEqual(len(errors),saved['samples'])
        self.assertEqual(sum(bool(e) for e in errors),saved['different'])
        self.assertEqual(max(errors),saved['max_pcm_error_lsb'])
        self.assertAlmostEqual(math.sqrt(sum(e*e for e in errors)/len(errors)),saved['rms_error_lsb'])
        self.assertEqual(hashlib.sha256(wavs['reference']).hexdigest(),saved['reference_wav_sha256'])
        self.assertEqual(hashlib.sha256(streams['negative']).hexdigest(),saved['pcm_sha256'])
        for name in RUNS:
            saved=read(EVIDENCE/name/'result.json')['pcm_without_poison']
            self.assertEqual(hashlib.sha256(streams['positive']).hexdigest(),saved['pcm_sha256'])

    def test_native_runs_preserve_controls_and_captures(self):
        for name in RUNS:
            with self.subTest(name=name):
                folder=EVIDENCE/name
                result=read(folder/'result.json')
                parsed=runner.parse_log((folder/'qemu.log').read_text(encoding='utf-8'))
                for key,value in parsed.items():
                    self.assertEqual(result[key],value)
                self.assertTrue(result['precision_pass'])
                self.assertEqual(result['low_lifetime']['first_row'],8)
                self.assertEqual(result['pcm_without_poison']['samples'],657540)
                self.assertEqual(result['pcm_without_poison']['different'],0)
                self.assertEqual(result['provenance']['sdkconfig_sha256'],sha(EVIDENCE/'sdkconfig'))
                self.assertEqual(result['provenance']['qemu_log_sha256'],sha(folder/'qemu.log'))
                self.assertEqual(result['baseline_sha256'],sha(BASELINE/name/'result.json'))
                if name!='synthetic':
                    self.assertTrue(result['capture_identical'])
                    self.assertEqual(result['capture'],read(BASELINE/name/'result.json')['capture'])

    def test_required_history_corruption_is_detected(self):
        folder=EVIDENCE/'negative-history'
        result=read(folder/'result.json')
        self.assertEqual(runner.parse_log((folder/'qemu.log').read_text(encoding='utf-8'))['low_lifetime']['first_row'],7)
        self.assertFalse(result['precision_pass'])
        self.assertGreater(result['pcm_without_poison']['different'],1000)
        self.assertGreater(result['pcm_without_poison']['max_pcm_error_lsb'],3)
        self.assertEqual(result['provenance']['sdkconfig_sha256'],sha(folder/'sdkconfig'))
        self.assertEqual(result['provenance']['qemu_log_sha256'],sha(folder/'qemu.log'))

    def test_incomplete_or_contradictory_reports_rejected(self):
        log=(EVIDENCE/'synthetic/qemu.log').read_text(encoding='utf-8')
        marker=re.search(r'AAC_LOW_LIFETIME[^\r\n]*',log).group()
        for bad in (log.replace(marker,''),log+'\n'+marker,
                    log.replace('first_row=8','first_row=9'),
                    log.replace('rows=32 bands=32','rows=31 bands=32'),
                    re.sub(r'poisoned_words=\d+','poisoned_words=1',log),
                    re.sub(r'complex=\d+','complex=0',log)):
            with self.assertRaises(ValueError):
                runner.parse_log(bad)

    def test_scope_and_exact_source_snapshots(self):
        config=(EVIDENCE/'sdkconfig').read_text(encoding='utf-8')
        for key in ('YORADIO_QEMU','YORADIO_QEMU_AAC_POINTER_AUDIT','YORADIO_QEMU_AAC_LOW_LIFETIME'):
            self.assertIn('CONFIG_'+key+'=y\n',config)
        self.assertNotIn('CONFIG_YORADIO_QEMU_AAC_LOW_POISON_HISTORY=y\n',config)
        for path,entry in read(EVIDENCE/'implementation.json')['files'].items():
            self.assertEqual(sha(EVIDENCE/entry['snapshot']),entry['sha256'],path)

    def test_aggregate_does_not_claim_unimplemented_memory_saving(self):
        summary=read(EVIDENCE/'summary.json')
        runs=[read(EVIDENCE/name/'result.json') for name in RUNS]
        self.assertEqual(summary['actual_ram_saving_bytes'],0)
        self.assertEqual({r['memory']['owner_bytes'] for r in runs},{summary['owner_request_bytes']})
        self.assertEqual(summary['poison_calls'],sum(r['low_lifetime']['calls'] for r in runs))
        self.assertEqual(summary['poisoned_words'],sum(r['low_lifetime']['poisoned_words'] for r in runs))
        self.assertEqual(summary['pointer_checks'],sum(r['pointers']['checks'] for r in runs))
        self.assertEqual(summary['capture_samples'],sum(r.get('capture',{}).get('samples',0) for r in runs))


if __name__=='__main__':
    unittest.main()
