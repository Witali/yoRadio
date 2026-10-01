#!/usr/bin/env python3
import json
from pathlib import Path
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
import run_aac_reserve as reserve
import run_aac_bfp16 as common
EVIDENCE = ROOT/'tests/results/esp32c3-aac-radio-ram-20261001'


class ReserveTests(unittest.TestCase):
    def test_qemu_evidence(self):
        folder = EVIDENCE/'qemu-reserve'
        result = json.loads((folder/'result.json').read_text())
        for key, value in reserve.parse_log((folder/'qemu.log').read_text()).items():
            self.assertEqual(value, result[key])
        for name in ('qemu.log', 'sdkconfig'):
            key = name.replace('.', '_') + '_sha256'
            self.assertEqual(common.sha256(folder/name), result['provenance'][key])
        self.assertEqual(result['pcm']['frames'], 328770)
        self.assertEqual(result['pcm']['max_pcm_error_lsb'], 0)
        manifest = json.loads((EVIDENCE/'implementation.json').read_text())
        for path, digest in manifest['files'].items():
            snapshot = manifest.get('snapshots', {}).get(path)
            self.assertEqual(common.sha256(EVIDENCE/snapshot if snapshot else ROOT/path), digest, path)

    def test_missing_or_duplicate_format_rejected(self):
        log = (EVIDENCE/'qemu-reserve/qemu.log').read_text()
        line = next(s for s in log.splitlines(True) if 'QEMU_AAC_CASE_PASS' in s)
        for bad in (log.replace(line, '', 1), log + line,
                    log.replace('HE44 first: 44100 Hz', 'HE44 first: 22050 Hz', 1),
                    log.replace('QEMU_SMOKE_PASS', 'REMOVED')):
            with self.assertRaises(ValueError):
                reserve.parse_log(bad)

    def test_pcm_oracle_rejects_corruption_and_silence(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/'a.wav', Path(tmp)/'b.wav'
            def write(path, data):
                with wave.open(str(path), 'wb') as out:
                    out.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
                    out.writeframes(data)
            write(a, b'\x01\x00\x02\x00')
            write(b, b'\x01\x00\x02\x00')
            self.assertEqual(reserve.compare_pcm(a, b)['max_pcm_error_lsb'], 0)
            write(b, b'\x01\x00\x03\x00')
            with self.assertRaises(ValueError): reserve.compare_pcm(a, b)
            write(a, b'\0'*4); write(b, b'\0'*4)
            with self.assertRaises(ValueError): reserve.compare_pcm(a, b)

    def test_physical_trials_keep_failures(self):
        for variant, expected in (('baseline', ['PASS', 'FAIL', 'FAIL']),
                                  ('reserve', ['FAIL']*3),
                                  ('reserve-ram', ['FAIL']*3),
                                  ('ram', ['PASS']*3)):
            report = json.loads((EVIDENCE/variant/'report.json').read_text())
            rows = [r for r in report['cases'] if r['name'].startswith('memory-playback:')]
            self.assertEqual([r['result'] for r in rows], expected)
            ota = json.loads((EVIDENCE/variant/'ota.json').read_text())
            self.assertEqual(ota['after']['app_elf_sha256'], report['board']['app_elf_sha256'])
            for key in ('wifi_unchanged', 'playlist_unchanged', 'settings_unchanged'):
                self.assertIs(ota[key], True)


if __name__ == '__main__':
    unittest.main()
