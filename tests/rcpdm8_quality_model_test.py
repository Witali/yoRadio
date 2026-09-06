"""Generated data only. Run with the NumPy-enabled Python used by the model."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import numpy as np

spec = importlib.util.spec_from_file_location("quality", Path(__file__).resolve().parents[1] / "tools/esp8266_audio_profile/measure_rcpdm8_quality.py")
quality = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality)


class QualityTest(unittest.TestCase):
    def test_bit_order_and_carrier_hold(self):
        expected = np.array([1.] * 4 + [-1.] * 28)
        np.testing.assert_array_equal(quality.bits_to_grid(np.array([0x80]), 8), expected)
        np.testing.assert_array_equal(quality.bits_to_grid(np.array([0xf0000000]), 32), expected)

    def test_same_physical_filter_for_both_carriers(self):
        f = np.array([0., 1 / (2 * np.pi * 1e-5)])
        filters = quality.filters(f)
        self.assertAlmostEqual(abs(filters["rc10us"][1]), 1 / np.sqrt(2))
        self.assertAlmostEqual(abs(filters["ladder10us"][1]), 1 / 3)
        for values in filters.values():
            self.assertEqual(values[0], 1)

    def test_idle_is_not_a_negative_sinad(self):
        with tempfile.TemporaryDirectory() as directory:
            files = {}
            for name, width in quality.VARIANTS.items():
                files[name] = Path(directory) / name
                np.full(72000, 0xaa if width == 8 else 0xaaaaaaaa,
                        dtype="u1" if width == 8 else "<u4").tofile(files[name])
            t = np.arange(72000) / 48000
            pcm = np.round(327.67 * np.sin(2 * np.pi * 1000 * t)).astype(np.int16)
            result = quality.analyze(pcm, files, 1000)
            for variant in result["models"].values():
                for row in variant.values():
                    self.assertFalse(row["tone_detected"])
                    self.assertIsNone(row["sinad_db"])
                    self.assertTrue(row["below_numerical_floor"])


if __name__ == "__main__":
    unittest.main()
