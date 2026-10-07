#!/usr/bin/env python3
"""Validate the fifth storage variant and preserve four-format evidence parsing."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('storage_tests', ROOT / 'tests/test-aac-storage.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


class Storage18Tests(base.StorageTests):
    evidence = ROOT / 'tests/results/esp32c3-aac-storage18-20261002'
    expected_runs = {'qmf':153, 'ps':177}
    payloads = dict(base.StorageTests.payloads, **{'5':3088})

    def test_18bit_variant_is_measured(self):
        for (kind, name), result in self.results.items():
            rows = [r for r in result['runs'] if r['variant']==5]
            self.assertEqual(len(rows), 9 if name=='synthetic' else 3)
            for row in rows:
                self.assertLessEqual(row['max_shift'], 14)
                self.assertEqual(row['over_limit'], 0)
        text = (self.evidence / 'arithmetic.log').read_text()
        self.assertIn('STORAGE_18BIT_EXACT_PASS pairs=262144', text)
        self.assertIn('random_pairs=1000000 boundary_pairs=167322 formats=5', text)

    def test_prior_variants_preserve_pcm(self):
        fields = ('samples','frames','max_l','max_r','different','over_one','over_two','over_limit')
        for (kind, name), result in self.results.items():
            old = json.loads((base.EVIDENCE / kind / name / 'result.json').read_text())
            self.assertEqual(result['provenance']['fixtures'], old['provenance']['fixtures'])
            if name!='synthetic':
                self.assertEqual(result['provenance']['recording']['sha256'],
                                 old['provenance']['recording']['sha256'])
            previous = {(r['case'],r['variant'],r['run']):r for r in old['runs']}
            for row in result['runs']:
                if row['variant']==5:continue
                reference = previous[row['case'],row['variant'],row['run']]
                for field in fields:
                    self.assertEqual(row[field], reference[field], (kind,name,field))
            self.assertEqual([r for r in result.get('error_statistics',[]) if r['variant']!=5],
                             old.get('error_statistics',[]))

    def test_mislabelled_or_missing_fifth_variant_rejected(self):
        for kind, parser in base.PARSERS.items():
            log = self.logs[kind, 'abba64']
            without_fifth = '\n'.join(line for line in log.splitlines() if 'variant=5 ' not in line)
            for changed in (without_fifth, log.replace('formats=5','formats=4'),
                            log.replace('formats=5','formats=6')):
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    parser(changed)


if __name__ == '__main__':
    unittest.main()
