"""No-radio regressions for no-dither spur and temporal analysis."""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/esp8266_audio_profile"))
import inspect_rcpdm_no_dither as inspect


class DitherAnalysisTest(unittest.TestCase):
    def test_alternating_idle_has_no_fake_audio_spur(self):
        words = np.full(72000, 0x55555555, dtype="<u4")
        self.assertEqual(inspect.spurs(words, 1000)["strongest_nonfundamental_bins"], [])

    def test_known_square_wave_excludes_fundamental(self):
        # 24 high PCM-sized words then 24 low: a coherent 1-kHz square wave.
        period = np.r_[np.full(24, 0xffffffff, dtype="<u4"), np.zeros(24, dtype="<u4")]
        result = inspect.spurs(np.tile(period, 1500), 1000)
        self.assertEqual(result["windows"], 1)
        self.assertEqual(result["strongest_nonfundamental_bins"][0]["hz"], 3000)
        self.assertTrue(all(abs(p["hz"] - 1000) > 2 for p in result["strongest_nonfundamental_bins"]))

    def test_temporal_silence_is_not_a_coherent_lsb_tone(self):
        words = np.full(396000, 0x55555555, dtype="<u4")
        gains = inspect.lsb_windows(words, words, 1 + 0j)
        self.assertEqual(len(gains), 8)
        np.testing.assert_allclose(gains, 0, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
