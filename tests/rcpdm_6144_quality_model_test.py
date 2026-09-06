from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"tools/esp8266_audio_profile"))
import measure_rcpdm_6144 as experiment


class Rate6144Test(unittest.TestCase):
    def test_same_carrier_and_exact_fixed_delay(self):
        for cfg in experiment.CONFIGS.values():
            self.assertEqual(cfg["bit_rate_hz"], 48000*128)
            self.assertEqual(cfg["bits"], 128)
        self.assertEqual(experiment.CONFIGS["rc128-half"]["fixed_delay_seconds"], 127/(2*6144000))
        self.assertEqual(experiment.CONFIGS["pdm128"]["fixed_delay_seconds"], 0)

    def test_idle_is_not_a_weak_tone(self):
        words=np.full(396000*4, 0x55555555, dtype="<u4")
        values, means=experiment.coherent_windows(words)
        self.assertEqual(len(values), 8)
        np.testing.assert_allclose(values, 0, atol=1e-14)
        np.testing.assert_array_equal(means, 0)

    def test_word_stride_and_coherent_gain_at_6144(self):
        # A 1-kHz square wave: 24 PCM frames high, then 24 frames low.
        words=np.tile(np.r_[np.full(96, 0xffffffff, dtype="<u4"), np.zeros(96, dtype="<u4")], 8250)
        values, means=experiment.coherent_windows(words)
        phase=np.exp(-2j*np.pi*np.arange(6144)/6144)
        input_wave=np.r_[np.ones(3072), -np.ones(3072)]
        aperture=np.sinc(1000/6144000)*np.exp(-1j*np.pi*1000/6144000)
        expected=2*np.dot(input_wave, phase)/6144*aperture/(1+2j*np.pi*1000*1e-5)
        np.testing.assert_allclose(values, expected, atol=1e-12)
        np.testing.assert_array_equal(means, 0)


if __name__ == "__main__":
    unittest.main()
