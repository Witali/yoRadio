#!/usr/bin/env python3
"""Verify full AAC coverage and immutable decompilation evidence."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/audits/esp32c3-aac-full-20261001'


class FullAacDecompileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory=json.loads((DATA/'inventory.json').read_text())
        cls.export=json.loads((DATA/'pseudocode/manifest.json').read_text())
        cls.provenance=json.loads((DATA/'provenance.json').read_text())

    def test_every_archive_function_was_exported_at_its_address(self):
        expected={f['name']:f for f in self.inventory['functions']}
        actual={f['name']:f for f in self.export['functions']}
        self.assertEqual(len(self.inventory['objects']),144)
        self.assertEqual(len(expected),186)
        self.assertEqual(set(expected),set(actual))
        for name,f in expected.items():
            self.assertTrue(actual[name]['completed'])
            self.assertEqual(actual[name]['address'].split(':')[-1],f['address'])
            self.assertGreaterEqual(int(f['address'],16),0x43000000)
            self.assertLess(int(f['address'],16),0x43100000)

    def test_optimized_cores_and_discarded_helpers_are_included(self):
        names={f['name'] for f in self.inventory['functions']}
        self.assertTrue({'calc_sbr_anafilterbank_LC_core','calc_sbr_synfilterbank',
                         'calc_sbr_synfilterbank_LC','synthesis_sub_band_LC_core1',
                         'synthesis_sub_band_LC_core2','decode_huff_cw_tab1',
                         'lt_decode','unpack_idx_esc'} <= names)
        self.assertTrue(all(not s['name'].startswith(('ps_','sbr_','calc_sbr','synthesis_sub_band'))
                            for s in self.inventory['external_symbols']))

    def test_file_hashes_and_elf_identity(self):
        for name,digest in self.provenance['files'].items():
            self.assertEqual(hashlib.sha256((DATA/name).read_bytes()).hexdigest(),digest,name)
        self.assertEqual(self.inventory['elf_sha256'],self.export['sha256'])
        self.assertEqual(self.export['sha256'],self.provenance['elf_sha256'])
        self.assertTrue(self.inventory['analysis_only'])

    def test_empty_vendor_objects_and_warning_are_not_hidden(self):
        objects={o['member']:o for o in self.inventory['objects']}
        for name in ('get_audio_specific_config.c.obj','get_ga_specific_config.c.obj',
                     'pvmp4audiodecoderconfig.c.obj','pvmp4setaudioconfig.c.obj'):
            self.assertFalse(objects[name]['functions'])
            self.assertFalse(objects[name]['data'])
        warnings=[f['name'] for f in self.export['functions'] if f['pseudocode_contains_warning']]
        self.assertEqual(warnings,['ps_allocate_decoder'])


if __name__=='__main__':
    unittest.main()
