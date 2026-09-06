"""Verify the interpolation/delay reasoning without fitting a measured signal."""
import unittest
import numpy as np


class InterpolationTest(unittest.TestCase):
    def test_ramp_is_causal_moving_average_and_preserves_one_lsb(self):
        samples = np.array([0, 1, -1, 32767, -32768, 0], dtype=np.int64) * 8192
        for bits in (8, 16, 32, 64, 128):
            previous = np.r_[0, samples[:-1]]
            self.assertTrue(np.all((samples - previous) % bits == 0))
            ramp = (previous[:, None] + (samples - previous)[:, None] // bits *
                    np.arange(1, bits + 1)).ravel()
            held = np.repeat(samples, bits)
            average = np.convolve(held, np.ones(bits) / bits, mode='full')[:len(held)]
            np.testing.assert_array_equal(ramp, average)
            self.assertEqual(ramp[bits], 8192 // bits)

    def test_fixed_group_delay_at_all_output_rates(self):
        for bits in (8, 16, 32, 64, 128):
            rate = 48000 * bits
            frequency = np.array([100., 1000., 7000., 20000.])
            actual = np.exp(-2j * np.pi * frequency[:, None] / rate * np.arange(bits)).mean(axis=1)
            delay = (bits - 1) / (2 * rate)
            expected = (np.sinc(frequency / 48000) / np.sinc(frequency / rate) *
                        np.exp(-2j * np.pi * frequency * delay))
            np.testing.assert_allclose(actual, expected, atol=1e-14, rtol=1e-14)


if __name__ == '__main__':
    unittest.main()
