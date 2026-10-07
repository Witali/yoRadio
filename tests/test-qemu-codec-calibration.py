"""Calibration must use matching physical/QEMU windows and verified fixtures."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/codec_benchmark"))
import calibrate_qemu_aac as aac
import calibrate_qemu_codecs as codecs


class CalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qemu = (aac.EVIDENCE / "qemu.log").read_text(encoding="utf-8-sig")
        cls.hardware = {name: (aac.EVIDENCE / name).read_text(encoding="utf-8-sig") for name in aac.HARDWARE}
        cls.fixture = aac.FIXTURE.read_bytes()

    def test_aac_units_and_weighting(self):
        result = aac.calibrate(self.qemu, self.hardware, self.fixture)
        self.assertAlmostEqual(result["factor"], (1080 + 1071) * 160000 / (85508815 + 85019977))
        self.assertFalse(result["hardware_total_cpu_load_measured"])
        self.assertFalse(result["he_aac_hardware_validated"])

    def test_reject_different_fixture(self):
        with self.assertRaisesRegex(ValueError, "hash"):
            aac.calibrate(self.qemu, self.hardware, self.fixture[:-1])

    def test_reject_mismatched_hardware_window(self):
        hardware = dict(self.hardware)
        hardware[aac.HARDWARE[0]] = hardware[aac.HARDWARE[0]].replace("pcm 970752", "pcm 970753")
        with self.assertRaisesRegex(ValueError, "Mismatched"):
            aac.calibrate(self.qemu, hardware, self.fixture)

    def test_reject_incomplete_and_uncounted_runs(self):
        for marker in ("QEMU_AAC_CAL_PASS", "nop1024=1025", "QEMU_SMOKE_PASS"):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                aac.calibrate(self.qemu.replace(marker, "missing"), self.hardware, self.fixture)

    def test_reject_duplicate_window(self):
        line = next(line for line in self.qemu.splitlines() if "QEMU_AAC_CAL path=" in line)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            aac.calibrate(self.qemu + "\n" + line, self.hardware, self.fixture)

    def test_reject_changed_decoder(self):
        with self.assertRaisesRegex(ValueError, "runtime changed"):
            aac.calibrate(self.qemu.replace(aac.DECODER_RUNTIME, "v9.0.0"), self.hardware, self.fixture)

    def test_each_other_codec_reproducible(self):
        result = codecs.build_profile(aac.EVIDENCE)
        saved = json.loads((ROOT / "tools/codec_benchmark/calibration/esp32c3-codecs-160mhz.json").read_text())
        self.assertEqual(result, saved)
        self.assertEqual(len(result["codecs"]), 4)
        self.assertFalse(result["universal_factor_supported"])

    def test_cross_codec_mixup_rejected(self):
        hardware = (aac.EVIDENCE / "hardware-mp3.log").read_text(encoding="utf-8-sig")
        qemu = (aac.EVIDENCE / "qemu-opus.log").read_text(encoding="utf-8-sig")
        with self.assertRaises(ValueError):
            codecs.compare("mp3", hardware, qemu)


if __name__ == "__main__":
    unittest.main()
