"""Validate matched RX experiments without converting diagnostic progress to PASS."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'tests/results/esp32c3-rx-matched-20261007'
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
from save_rx_comparison_evidence import COPY_KEYS, validate_pair
from summarize_stream_memory import summarize
from ota_diagnostic import serial_health


def read(name):
    return json.loads((DATA/name).read_text())


class PairValidation(unittest.TestCase):
    def setUp(self):
        self.configs = dict(baseline='\n'.join('# '+k+' is not set' for k in COPY_KEYS),
                            candidate='\n'.join(k+'=y' for k in COPY_KEYS))
        self.builds = {k: dict(elf_sha256=k, source_sha256={'audio.c':'same'}) for k in self.configs}
        self.summaries = {k: dict(image=k, requested_seconds=600, observed_seconds=600.1,
            fixture_hashes={'hev2':'same'}, cpu_budget_percent=None) for k in self.configs}

    def test_only_matching_configuration_and_sources(self):
        validate_pair(self.configs, self.builds, self.summaries)
        self.configs['candidate'] += '\nCONFIG_OTHER_CHANGE=y'
        with self.assertRaises(ValueError): validate_pair(self.configs, self.builds, self.summaries)
        self.setUp()
        self.builds['candidate']['source_sha256']['audio.c'] = 'changed'
        with self.assertRaises(ValueError): validate_pair(self.configs, self.builds, self.summaries)

    def test_wrong_duration_stream_image_or_cpu_gate_rejected(self):
        original = copy.deepcopy(self.summaries)
        for field,value in (('requested_seconds',60), ('observed_seconds',599),
                            ('fixture_hashes',{'hev2':'other'}), ('image','wrong'),
                            ('cpu_budget_percent',85)):
            self.summaries = copy.deepcopy(original)
            self.summaries['candidate'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_pair(self.configs, self.builds, self.summaries)


class MatchedEvidence(unittest.TestCase):
    def test_manifest_and_recorded_sources(self):
        manifest = read('manifest.json')
        self.assertEqual(set(manifest), {p.relative_to(DATA).as_posix() for p in DATA.rglob('*')
                                        if p.is_file() and p != DATA/'manifest.json'})
        for name, record in manifest.items():
            data = (DATA/name).read_bytes()
            self.assertEqual(record, dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
        for phase in ('baseline','ota','candidate','restore'):
            for name,digest in read(phase+'/report.json')['test_sources_sha256'].items():
                self.assertEqual(hashlib.sha256((DATA/'sources'/digest/name).read_bytes()).hexdigest(), digest)

    def test_replay_and_comparison_scope(self):
        summaries = {k:summarize(DATA/k, independent_network=True) for k in ('baseline','candidate')}
        self.assertEqual(summaries, read('summary.json'))
        configs = {k:(DATA/'firmware'/k/'sdkconfig').read_text() for k in summaries}
        builds = {k:read('firmware/'+k+'/manifest.json') for k in summaries}
        validate_pair(configs, builds, summaries)
        for name,s in summaries.items():
            self.assertEqual(s['acceptance'], read(name+'/report.json')['cases'])
            self.assertFalse(s['ownership']['complete'])
            self.assertIn('network',s)
            self.assertFalse(s['acoustic_continuity_qualified'])
        self.assertFalse(read('provenance.json')['production_qualified'])

    def test_ota_and_final_restoration(self):
        for phase in ('ota','restore'):
            cases = read(phase+'/report.json')['cases']
            self.assertTrue(cases)
            self.assertTrue(all(c['result']=='PASS' for c in cases))
            health = serial_health(read(phase+'/performance.json'))
            self.assertEqual(health, read(phase+'/serial-health.json'))
            self.assertEqual(health['result'],'PASS')
        final = read('board-final.json')
        self.assertTrue(final['status']['audio'])
        self.assertEqual(final['stationtimeout'],10)
        self.assertEqual(final['info']['app_elf_sha256'],read('firmware/baseline/manifest.json')['elf_sha256'])
        asm = (DATA/'verify/wlanif_input.txt').read_text()
        self.assertIn('<pbuf_alloc>',asm)
        self.assertIn('<esp_netif_free_rx_buffer>',asm)
        self.assertNotIn('<esp_pbuf_allocate>',asm)


if __name__ == '__main__':
    unittest.main()
