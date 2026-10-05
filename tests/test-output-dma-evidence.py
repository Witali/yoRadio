"""Replay the DMA A/B evidence without hiding failed hardware gates."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/results/esp32c3-output-dma-20261005'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools/esp32c3_tests'))
from compare_output_dma import compare


def read(path): return json.loads(path.read_text())
def sha(data): return hashlib.sha256(data).hexdigest()


class DMAEvidence(unittest.TestCase):
    def test_manifest(self):
        manifest = read(DATA / 'manifest.json')
        files = {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                 if p.is_file() and p.name != 'manifest.json'}
        self.assertEqual(files, set(manifest))
        for name, identity in manifest.items():
            data = (DATA / name).read_bytes()
            self.assertEqual(len(data), identity['bytes'], name)
            self.assertEqual(sha(data), identity['sha256'], name)

    def test_host_pcm_and_source_snapshot(self):
        folder = DATA / 'host-final'
        report = read(folder / 'report.json')
        self.assertTrue(report['pcm_identical'] and report['case_metadata_identical'])
        for name, identity in report['variants'].items():
            pcm = gzip.decompress((folder / (name+'.pcm.gz')).read_bytes())
            self.assertEqual(len(pcm), identity['pcm_bytes'])
            self.assertEqual(sha(pcm), identity['sha256'])
        for name, digest in report['sources'].items():
            self.assertEqual(sha((folder / 'sources' / name).read_bytes()), digest)
        self.assertIn('432', (folder / 'dma.log').read_text().splitlines()[-1])
        self.assertEqual(report['normalizer'], 'PASS normalizer cases=648 max_error_lsb=0')

    def test_hardware_comparisons_include_failures(self):
        for candidate, filename in [('candidate-load','comparison.json'),
                                    ('prefill-load','comparison-prefill.json')]:
            actual = compare(DATA / 'control-load', DATA / candidate)
            self.assertEqual(actual, read(DATA / filename))
            self.assertEqual(len(actual['candidate']['cases']), 7)
        first = read(DATA / 'comparison.json')['candidate']['cases']['hev2-44100-stereo']
        self.assertEqual(first['acceptance'], 'FAIL')
        self.assertLess(first['audio_wall_ratio'], 0.90)
        final = read(DATA / 'comparison-prefill.json')['candidate']['cases']
        self.assertEqual(sum(c['acceptance'] == 'FAIL' for c in final.values()), 3)
        for case in final.values():
            self.assertGreater(case['audio_wall_ratio'], 0.99)
            self.assertLess(case['audio_wall_ratio'], 1.01)

    def test_images_memory_and_ota_eof(self):
        control = read(DATA / 'verify-staged/build.json')
        final = read(DATA / 'verify-prefill/build.json')
        self.assertEqual(control['sections']['.dram0.bss']-final['sections']['.dram0.bss'], 2016)
        self.assertEqual(control['types'], final['types'])
        self.assertEqual(control['features'], final['features'])
        for variant, evidence in [('staged','control-load'),('dma','candidate-load'),('dma-prefill','prefill-load')]:
            folder = ROOT / ('firmware/development/esp32c3-output-'+variant)
            manifest = read(folder / 'manifest.json')
            app = (folder / 'app.bin').read_bytes()
            self.assertEqual(sha(app), manifest['app_sha256'])
            self.assertEqual(app[176:208].hex(), read(DATA / evidence / 'report.json')['board']['app_elf_sha256'])
            self.assertTrue(manifest['hardware_tested'])
            self.assertFalse(manifest['production_qualified'])
        for folder in ('ota-control','ota-candidate','ota-prefill','prefill-eof'):
            cases = read(DATA / folder / 'report.json')['cases']
            self.assertTrue(all(c['result'] == 'PASS' for c in cases), folder)
        board = read(DATA / 'board-final.json')
        self.assertEqual(board['info']['app_elf_sha256'], final['elf_sha256'])


if __name__ == '__main__': unittest.main()
