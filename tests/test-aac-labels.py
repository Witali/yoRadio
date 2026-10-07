"""Check the remaining AAC offset refactor against retained decoder evidence."""
import hashlib
import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/codec_benchmark'))
EVIDENCE = ROOT/'tests/results/esp32c3-aac-labels-20261001'
VARIANTS = {'packed-history':'packed_history', 'pc16-history':'pc16_history',
            'ps-port':'ps_history_port', 'pc16-write':'pc16_write', 'pc16-cache':'pc16_cache'}
def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


class LabelsTests(unittest.TestCase):
    def test_all_runs_reparse_with_valid_hashes(self):
        runs = samples = 0
        for variant, module in VARIANTS.items():
            parse = importlib.import_module('run_aac_'+module).parse_log
            for case in ('synthetic','abba64'):
                folder = EVIDENCE/variant/case; saved = read(folder/'result.json')
                for key,value in parse((folder/'qemu.log').read_text()).items():
                    self.assertEqual(value,saved[key],(variant,case,key))
                for name,key in [('qemu.log','qemu_log_sha256'),('sdkconfig','sdkconfig_sha256')]:
                    self.assertEqual(sha(folder/name),saved['provenance'][key])
                runs += len(saved['runs']); samples += sum(r['samples'] for r in saved['runs'])
        manifest = read(EVIDENCE/'implementation.json')
        self.assertEqual(runs,345); self.assertEqual(runs,manifest['paired_runs'])
        self.assertEqual(samples,manifest['candidate_scalar_pcm_samples'])

    def test_pcm_statistics_and_rejected_precision_do_not_change(self):
        fields = ('case','variant','run','frames','samples','different','max_l','max_r',
                  'over_one','over_two','over_limit','changed_qmf','max_shift')
        for variant in VARIANTS:
            for case in ('synthetic','abba64'):
                new = read(EVIDENCE/variant/case/'result.json')
                old = read(ROOT/'tests/results'/('esp32c3-aac-'+variant+'-20261001')/case/'result.json')
                self.assertEqual(len(new['runs']),len(old['runs']))
                for a,b in zip(new['runs'],old['runs']):
                    for field in fields:
                        if field in a and field in b: self.assertEqual(a[field],b[field],(variant,case,field))
                self.assertEqual(new.get('error_statistics'),old.get('error_statistics'))
                for field in ('precision_pass','production_precision_pass'): self.assertEqual(new[field],old[field])
        self.assertFalse(read(EVIDENCE/'packed-history/synthetic/result.json')['precision_pass'])

    def test_production_adapters_with_cache_remain_bit_exact(self):
        from run_aac_reserve import parse_log
        folder = EVIDENCE/'owner'; saved = read(folder/'result.json')
        for key,value in parse_log((folder/'qemu.log').read_text()).items(): self.assertEqual(value,saved[key])
        self.assertEqual(saved['pcm']['pcm_sha256'],'66484d0f5d3b813335db9f5ebc9ebf426de871bf6ff131b2afbf824d902aadfe')
        self.assertEqual(saved['pcm']['frames'],328770)
        self.assertEqual(saved['pcm']['different_samples'],0)
        self.assertEqual(saved['pcm']['max_pcm_error_lsb'],0)

    def test_exact_sources_are_preserved_for_both_build_batches(self):
        manifest = read(EVIDENCE/'implementation.json')
        for entry in [*manifest['files'].values(),manifest['first_three_variants_header']]:
            self.assertEqual(sha(EVIDENCE/entry['snapshot']),entry['sha256'])


if __name__ == '__main__': unittest.main()
