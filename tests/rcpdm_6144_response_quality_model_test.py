"""Check phase sign, fixed-delay compensation and the 20-kHz Hann boundary."""
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"tools/esp8266_audio_profile"))
import measure_rcpdm_6144_response as response
import measure_pdm_matrix as model


def pack(bits):
    """Independent chronological MSB-first packing, without production helpers."""
    return np.packbits(np.asarray(bits, dtype=np.uint8), bitorder="big").view(
        ">u4").astype("<u4")


class ResponseTest(unittest.TestCase):
    def test_exact_pure_delay_and_unwrapping(self):
        hz=np.asarray(response.FREQUENCIES)
        delay=80e-6  # More than one full phase turn at 20 kHz.
        h=.75*np.exp(-2j*np.pi*hz*delay)
        curve=response.curve(hz, h, delay)
        np.testing.assert_allclose(curve["gain_db"], 20*np.log10(.75), atol=1e-12)
        np.testing.assert_allclose(curve["raw_phase_degrees"], -360*hz*delay, atol=1e-11)
        np.testing.assert_allclose(curve["group_delay_us"], 80, atol=1e-9)
        np.testing.assert_allclose(curve["interpolation_compensated_phase_degrees"], 0, atol=1e-11)
        np.testing.assert_allclose(curve["interpolation_compensated_group_delay_us"], 0, atol=1e-9)

    def test_reject_invalid_curve_and_band(self):
        for hz, h in (([20, 30], [1, 1]), ([20, 20, 30], [1, 1, 1]),
                      ([20, 30, 40], [1, 0, 1]), ([20, 30, 40], [1, np.nan, 1])):
            with self.assertRaises(ValueError):
                response.curve(hz, h, 0)
        for high in (19, 20000.5, model.GRID_RATE//2):
            with self.assertRaises(ValueError):
                model.analyze([], {}, {}, band_high_hz=high)

    def test_phase_and_gain_against_known_delayed_square(self):
        frames=72000
        period=np.r_[np.ones(24, dtype=np.int16), -np.ones(24, dtype=np.int16)]
        pcm=np.tile(period, frames//48)*16000
        delay_bits=17
        bits=np.roll(np.repeat((period>0).astype(np.uint8), 128), delay_bits)
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/"delayed.bin"
            np.tile(pack(bits), frames//48).tofile(file)
            result=response.measure_transfer(pcm, {"known": file}, 1000)
        expected_delay=np.exp(-2j*np.pi*1000*delay_bits/response.CARRIER)
        frequency=np.arange(999, 1002)
        # The measured transfer averages three Hann bins, not H(1000) alone.
        weights=np.array([.25, 1., .25])*np.sinc(frequency/response.CARRIER)**2
        for name, filt in model.original.filters(frequency).items():
            actual=complex(**result["known"][name]["transfer"])
            expected=(32768/16000)*expected_delay*np.sum(filt*weights)/sum(weights)
            self.assertAlmostEqual(abs(actual-expected), 0, delta=1e-12)
            self.assertEqual(len(result["known"][name]["window_transfers"]), 1)

    def test_20khz_upper_hann_bin_is_counted(self):
        frames=72000
        # 20 kHz has exactly five cycles per 1536 carrier bits.
        bits=(np.arange(1536)*5 % 1536)<768
        pcm=np.round(20000*np.sin(2*np.pi*20000*np.arange(frames)/48000)).astype("<i2")
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/"20khz.bin"
            np.tile(pack(bits), frames*128//1536).tofile(file)
            paths, configs={"square": file}, {"square": dict(bits=128)}
            old=model.analyze(pcm, paths, configs, 20000)
            guard=model.analyze(pcm, paths, configs, 20000, band_high_hz=20001)
            transfer=response.measure_transfer(pcm, paths, 20000)
        for name in ("rc10us", "rc40us", "ladder10us"):
            before=old["models"]["square"][name]
            after=guard["models"]["square"][name]
            self.assertTrue(after["tone_detected"])
            self.assertIsNone(after["thd_db"])  # Not a claim of zero distortion.
            # Missing one side-bin loses 1/6 of the coherent tone power.
            # Filter attenuation changes slightly between 19999/20000/20001 Hz.
            self.assertAlmostEqual(after["sinad_db"]-before["sinad_db"], 10*np.log10(6/5), delta=.0003)
            self.assertAlmostEqual(after["fundamental_gain_db"], transfer["square"][name]["gain_db"], delta=1e-7)


if __name__ == "__main__":
    unittest.main()
