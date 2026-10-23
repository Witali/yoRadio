"""Host-only path-key controls; no capture, PCM, reference or process execution."""
import copy
import unittest

from capture8 import canonical_variant_sources
from pcm_metrics import need

KEY = 'variant/vorbis_repair/setup.c'
WIN = 'variant\\vorbis_repair\\setup.c'
SHA = '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'


class VariantPathControls(unittest.TestCase):
    def test_actual_windows_key_maps_to_exact_setup_identity(self):
        self.assertEqual(canonical_variant_sources({WIN: SHA}), {KEY: SHA})

    def test_forward_slash_and_mixed_separator_keys(self):
        self.assertEqual(canonical_variant_sources({KEY: SHA}), {KEY: SHA})
        self.assertEqual(canonical_variant_sources({'variant\\vorbis_repair/setup.c': SHA}), {KEY: SHA})

    def test_case_sensitive_filename_retained_without_hash_mutation(self):
        values = {WIN: SHA, 'variant\\vorbis_repair\\COPYING': 'a' * 64}
        before = copy.deepcopy(values)
        self.assertEqual(canonical_variant_sources(values), {KEY: SHA, 'variant/vorbis_repair/COPYING': 'a' * 64})
        self.assertEqual(values, before)

    def test_separator_alias_duplicates_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Duplicate canonical Windows variant source path'):
            canonical_variant_sources({WIN: SHA, KEY: SHA})

    def test_windows_case_alias_duplicates_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'Duplicate canonical Windows variant source path'):
            canonical_variant_sources({KEY: SHA, 'variant/VORBIS_REPAIR/SETUP.c': SHA})

    def test_absolute_drive_unc_parent_and_colon_paths_rejected(self):
        for key in ('/variant/setup.c', 'C:\\variant\\setup.c', '\\\\host\\share\\setup.c',
                    '../variant/setup.c', 'variant/../setup.c', 'variant/part:setup.c'):
            with self.subTest(key=key):
                with self.assertRaisesRegex(RuntimeError, 'Safe relative path required'):
                    canonical_variant_sources({key: SHA})

    def test_redundant_or_nonvariant_paths_rejected(self):
        for key in ('variant//vorbis_repair/setup.c', 'variant/./vorbis_repair/setup.c',
                    './variant/vorbis_repair/setup.c', 'sources/variant/setup.c', '.', ''):
            with self.subTest(key=key):
                with self.assertRaises(RuntimeError):
                    canonical_variant_sources({key: SHA})

    def test_nontext_and_missing_maps_rejected(self):
        for values in ({}, [], None, {1: SHA}):
            with self.subTest(values=values):
                with self.assertRaises(RuntimeError):
                    canonical_variant_sources(values)

    def test_invalid_hashes_rejected_without_rewriting(self):
        for digest in ('', 'x' * 64, 'A' * 64, 'a' * 63, None, 1):
            with self.subTest(digest=digest):
                with self.assertRaisesRegex(RuntimeError, 'Exact lowercase variant source SHA256 required'):
                    canonical_variant_sources({WIN: digest})

    def test_missing_or_wrong_setup_identity_still_rejected(self):
        for values in ({'variant/vorbis_repair/output.c': SHA}, {WIN: '0' * 64}):
            with self.subTest(values=values):
                mapped = canonical_variant_sources(values)
                with self.assertRaisesRegex(RuntimeError, 'Actual variant setup identity'):
                    need(mapped.get(KEY) == SHA, 'Actual variant setup identity')


if __name__ == '__main__': unittest.main()
