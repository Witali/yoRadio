"""Host validation of retained physical flash-mode evidence; does not use USB."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/codec_benchmark/cache"))
from analyze_flash import validate
from analyze_hardware import parse

RESULTS = ROOT / "tests/results/esp32c3-flash-quad-20260930"


class QuadFlashEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.log = (RESULTS / "qio80-run-1.log").read_text()
        self.binary = (ROOT / "firmware/development/esp32c3-flash-qio80-test/app.bin").read_bytes()

    def test_all_six_physical_runs_and_exact_image_bytes(self):
        for mode, mhz in (("dio", 80), ("qio", 40), ("qio", 80)):
            binary = (ROOT / f"firmware/development/esp32c3-flash-{mode}{mhz}-test/app.bin").read_bytes()
            for boot in (1, 2):
                with self.subTest(mode=mode, mhz=mhz, boot=boot):
                    log = (RESULTS / f"{mode}{mhz}-run-{boot}.log").read_text()
                    result = validate(log, binary, mode, mhz)
                    self.assertEqual(result["read_passes"], 16)
                    self.assertEqual(len(result["decoded"]), 72)

    def test_mode_label_alone_cannot_prove_quad(self):
        bad = re.sub(r"ctrl=0x[0-9a-f]+", "ctrl=0x00ac2008", self.log)
        with self.assertRaises(ValueError):
            validate(bad, self.binary, "qio", 80)

    def test_wrong_clock_and_size_rejected(self):
        for old, new in (("actual_mhz=80", "actual_mhz=40"),
                         ("clock=0x80000000", "clock=0x00010000"),
                         ("physical_bytes=4194304", "physical_bytes=2097152")):
            with self.subTest(old=old), self.assertRaises(ValueError):
                validate(self.log.replace(old, new), self.binary, "qio", 80)

    def test_data_corruption_and_wrong_saved_image_rejected(self):
        with self.assertRaises(ValueError):
            validate(re.sub(r"crc32=0x[0-9a-f]+", "crc32=0x00000000", self.log),
                     self.binary, "qio", 80)
        with self.assertRaises(ValueError):
            validate(self.log, self.binary[:-1] + bytes([self.binary[-1] ^ 1]), "qio", 80)

    def test_incomplete_duplicate_and_crashed_runs_rejected(self):
        row = next(line for line in self.log.splitlines() if line.startswith("FLASH_READ "))
        for log in (self.log.replace(row, "", 1), self.log + "\n" + row,
                    self.log.replace("CACHE_HW_PASS", "NO_PASS"), self.log + "\nCORRUPT HEAP"):
            with self.assertRaises(ValueError):
                validate(log, self.binary, "qio", 80)

    def test_wrong_requested_mode_is_rejected_even_with_dio_header(self):
        with self.assertRaises(ValueError):
            validate(self.log, self.binary, "dio", 80)

    def test_flash_experiment_cannot_replace_dio_qemu_calibration(self):
        with self.assertRaises(ValueError):
            parse(self.log, "hardware")


if __name__ == "__main__":
    unittest.main()
