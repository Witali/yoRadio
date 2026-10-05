"""Replay retained step-3 evidence, including failures and independent PCM."""
import array
import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
import save_vorbis_lifecycle as saver

OUTPUT = ROOT / 'tests/results/esp32c3-vorbis-output-20261005'
FAULTS = ROOT / 'tests/results/esp32c3-vorbis-output-faults-20261005'


class Evidence(unittest.TestCase):
    def test_manifests(self):
        for folder in (OUTPUT, FAULTS):
            manifest = json.loads((folder / 'manifest.json').read_text())
            files = {p.relative_to(folder).as_posix() for p in folder.rglob('*')
                     if p.is_file() and p.name != 'manifest.json'}
            self.assertEqual(files, set(manifest))
            for name, identity in manifest.items():
                data = (folder / name).read_bytes()
                self.assertEqual(len(data), identity['bytes'], name)
                self.assertEqual(hashlib.sha256(data).hexdigest(), identity['sha256'], name)

    def test_complete_fault_sweep(self):
        result = saver.summarize(FAULTS)
        self.assertEqual(result['counts'], {'PASS': 1, 'HANDLED': 209})
        self.assertEqual(result['cycles'], 100)
        self.assertFalse(result['original_pcm_match'])
        self.assertTrue(result['initialization_gate_pass'])
        self.assertEqual(result['baseline_reference']['pcm'], 2112000)
        self.assertEqual(result['peak_ledger']['peak_actual'], 42672)

    def test_complete_original_dsp_and_independent_reference(self):
        pcm = gzip.decompress((OUTPUT / 'final/ample.pcm.gz').read_bytes())
        self.assertEqual(pcm, gzip.decompress((OUTPUT / 'raw-reference/ample.pcm.gz').read_bytes()))
        self.assertNotEqual(pcm, gzip.decompress((OUTPUT / 'baseline/ample.pcm.gz').read_bytes()))
        a, b = array.array('h'), array.array('h')
        a.frombytes(pcm)
        b.frombytes(gzip.decompress((OUTPUT / 'ffmpeg.pcm.gz').read_bytes()))
        if sys.byteorder != 'little': a.byteswap(); b.byteswap()
        self.assertEqual(len(a), len(b))
        delta = [abs(x-y) for x, y in zip(a, b)]
        saved = json.loads((OUTPUT / 'reference-error.json').read_text())
        self.assertEqual(max(delta), saved['max_absolute'])
        self.assertEqual(sum(d > 3 for d in delta), 0)
        self.assertAlmostEqual((sum(d*d for d in delta)/len(delta))**0.5, saved['rmse'])


if __name__ == '__main__': unittest.main()
