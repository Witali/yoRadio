"""Physical build layouts must match the selected early-owner configuration."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/codec_benchmark'))
from verify_aac_network_build import verify_layout


class LayoutTests(unittest.TestCase):
    def layout(self, early):
        return dict(native_aac_decoder={208 if early else 204},
                    aac_compact_owner_t={180 if early else 176},
                    aac_high_owner_t={32744}, aac_high_runtime_t={160})

    def test_both_exact_layouts(self):
        for early in (False, True):
            config='CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER=y' if early else '# CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER is not set'
            fields={('owner',0),('pending_owner',4)} if early else {('owner',0)}
            sizes=verify_layout(config,self.layout(early),fields)
            self.assertEqual(sizes['native_aac_decoder'],208 if early else 204)

    def test_config_mismatch_and_inconsistent_types_fail(self):
        with self.assertRaises(ValueError):
            verify_layout('',self.layout(True),{('owner',0),('pending_owner',4)})
        rows=self.layout(True);rows['native_aac_decoder']={204,208}
        with self.assertRaises(ValueError):
            verify_layout('CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER=y',rows,{('owner',0),('pending_owner',4)})

    def test_missing_or_misplaced_pending_pointer_fails(self):
        for fields in ({('owner',0)}, {('owner',0),('pending_owner',8)}):
            with self.assertRaises(ValueError):
                verify_layout('CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER=y',self.layout(True),fields)

    def test_dsp_size_is_not_relaxed(self):
        rows=self.layout(True);rows['aac_high_owner_t']={32748}
        with self.assertRaises(ValueError):
            verify_layout('CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER=y',rows,{('owner',0),('pending_owner',4)})


if __name__=='__main__':unittest.main()
