import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("hardware_cache", ROOT / "tools/codec_benchmark/cache/analyze_hardware.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
RESULTS = ROOT / "tests/results/esp32c3-cache-hardware-20260930"


class HardwareCacheTests(unittest.TestCase):
    def setUp(self):
        self.hardware = [(RESULTS / f"hardware-run-{i}.log").read_text(encoding="utf-8-sig") for i in (1, 2)]
        self.qemu = [(RESULTS / f"qemu-run-{i}.log").read_text(encoding="utf-8-sig") for i in (1, 2)]

    def test_saved_measurements_reproduce_summary(self):
        saved = json.loads((RESULTS / "summary.json").read_text())
        saved.pop("log_sha256")
        self.assertEqual(MODULE.analyze(self.hardware, self.qemu), saved)
        self.assertFalse(saved["whole_radio_cpu_measured"])
        self.assertIsNone(saved["universal_refill_penalty_cycles"])

    def test_hardware_timing_differs_from_guest_instruction_counts(self):
        result = MODULE.analyze(self.hardware, self.qemu)
        for case, bounds in (("lc48000_stereo", (16, 18)), ("he48000_stereo", (34, 36)),
                             ("hev2_44100_stereo", (44, 46))):
            mode = result["cases"][case]["modes"]["continuous"]
            self.assertTrue(bounds[0] < mode["decoder_cpu_percent"] < bounds[1])
            self.assertGreater(mode["effective_cycles_per_instruction"], 1.5)
        self.assertEqual(result["probes"]["1"]["extra_cycles_per_cold_line"], 103)
        self.assertGreater(result["probes"]["256"]["extra_cycles_per_cold_line"], 300)

    def test_missing_and_duplicate_windows_rejected(self):
        lines = self.hardware[0].splitlines()
        row = next(line for line in lines if line.startswith("CACHE_DECODE "))
        for log in (self.hardware[0].replace(row, "", 1), self.hardware[0] + "\n" + row):
            with self.assertRaises(ValueError):
                MODULE.parse(log, "hardware")

    def test_wrong_pcm_timer_or_mode_rejected(self):
        for old, new in (("rate=48000", "rate=24000"), ("ticks=14814128", "ticks=100000"),
                         ("deep_sleep=0", "deep_sleep=1"), ("channels=2", "channels=1"),
                         ("pcer=1", "pcer=0"), ("CACHE_HW_PASS", "CACHE_HW_FAIL")):
            with self.subTest(old=old), self.assertRaises(ValueError):
                MODULE.parse(self.hardware[0].replace(old, new), "hardware")

    def test_line_counter_semantics_must_be_verified(self):
        with self.assertRaises(ValueError):
            MODULE.parse(self.hardware[0].replace("cold_d=256", "cold_d=81448"), "hardware")

    def test_qemu_virtual_time_is_not_accepted_as_instructions(self):
        with self.assertRaises(ValueError):
            MODULE.parse(self.qemu[0].replace("instructions=1025", "instructions=160000"), "qemu")

    def test_failed_or_unrepeated_runs_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.parse(self.hardware[0] + "\nCORRUPT HEAP", "hardware")
        with self.assertRaises(ValueError):
            MODULE.analyze(self.hardware[:1], self.qemu)


if __name__ == "__main__":
    unittest.main()
