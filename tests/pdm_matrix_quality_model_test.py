"""Numerical-model regressions; no radio recordings needed."""
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/esp8266_audio_profile"))
import measure_pdm_matrix as matrix
import measure_rcpdm8_quality as old


class MatrixTest(unittest.TestCase):
    def test_frequency_and_shift_pairing(self):
        for bits in matrix.BITS:
            configs = [c for c in matrix.VARIANTS.values() if c["bits"] == bits and c["role"] == "comparison"]
            self.assertEqual(len(configs), 3)
            for config in configs:
                self.assertEqual(config["bit_rate_hz"], 48000 * bits)
                if config["alpha"]:
                    self.assertEqual(config["alpha"], 2 / bits)
                    self.assertTrue(9 < config["internal_rc_us"] < 10.4)

    def test_word_order_and_voltage_hold(self):
        # Same +1 first half, -1 second half, encoded at every carrier.
        expected = np.r_[np.ones(64), -np.ones(64)]
        for bits in matrix.BITS:
            width = min(bits, 32)
            bits_list = [1] * (bits // 2) + [0] * (bits // 2)
            words = [sum(b << (width-1-i) for i, b in enumerate(bits_list[j:j+width]))
                     for j in range(0, bits, width)]
            np.testing.assert_array_equal(matrix.bits_to_grid(words, bits), expected)
        words = np.array([0x12345678, 0x89abcdef], dtype=np.uint32)
        np.testing.assert_array_equal(matrix.bits_to_grid(words, 32),
                                      np.repeat(old.bits_to_grid(words, 32), 4))
        with self.assertRaises(ValueError):
            matrix.bits_to_grid([0], 128)

    def test_identical_physical_filter(self):
        models = old.filters(np.array([0, 1/(2*np.pi*1e-5)]))
        self.assertAlmostEqual(abs(models["rc10us"][1]), 1/np.sqrt(2))
        self.assertAlmostEqual(abs(models["ladder10us"][1]), 1/3)

    def test_higher_grid_preserves_old_score_and_idle_detection(self):
        with tempfile.TemporaryDirectory() as directory:
            configs, paths = {}, {}
            frames=72000
            # A deterministic nontrivial 32-bit signal checks all score fields;
            # idle128 must not acquire a fictitious tone through FFT roundoff.
            words = np.resize(np.array([0x5555aaaa, 0x7fff0000, 0x0001ffff], dtype="<u4"), frames)
            for name, bits in (("signal", 32), ("idle", 128)):
                paths[name] = Path(directory) / name
                configs[name] = dict(bits=bits)
            words.tofile(paths["signal"])
            np.full(frames*4, 0xaaaaaaaa, dtype="<u4").tofile(paths["idle"])
            t = np.arange(frames)/48000
            pcm = np.round(10000*np.sin(2*np.pi*1000*t)).astype("<i2")
            saved_variants = old.VARIANTS
            try:
                old.VARIANTS = {"signal": 32}
                expected = old.analyze(pcm, {"signal": paths["signal"]}, 1000)
            finally:
                old.VARIANTS = saved_variants
            actual = matrix.analyze(pcm, paths, configs, 1000)
            for model, row in actual["models"]["signal"].items():
                for key, value in row.items():
                    baseline = expected["models"]["signal"][model][key]
                    if value is None or isinstance(value, bool):
                        self.assertEqual(value, baseline)
                    else:
                        self.assertAlmostEqual(value, baseline, delta=.02)
            for row in actual["models"]["idle"].values():
                self.assertFalse(row["tone_detected"])
                self.assertIsNone(row["sinad_db"])
                self.assertTrue(row["below_numerical_floor"])


if __name__ == "__main__":
    unittest.main()
