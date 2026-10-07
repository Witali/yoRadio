import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("radio_profile", ROOT / "tools/codec_benchmark/cache/analyze_radio.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
RESULTS = ROOT / "tests/results/esp32c3-radio-hardware-20260930"


def load(folder, name):
    return json.loads((RESULTS / folder / name).read_text(encoding="utf-8"))


class RadioProfileTests(unittest.TestCase):
    def test_real_lc_playback_and_cpu_windows_pass(self):
        actual = MODULE.analyze(load("wifi-flash", "radio-perf.json"),
                                load("wifi-flash", "radio-status.json"),
                                ["lc-48000-stereo"], False)
        self.assertEqual(actual, load("wifi-flash", "radio-summary.json"))
        self.assertFalse(actual["format_changes_in_one_http_stream_verified"])
        self.assertTrue(34 < actual["cases"]["lc-48000-stereo"]["mean_busy_percent"] < 36)

    def test_aac_initialization_failure_is_not_a_low_cpu_success(self):
        with self.assertRaisesRegex(ValueError, "Firmware failure"):
            MODULE.analyze(load("baseline-failure", "radio-perf.json"),
                           load("baseline-failure", "radio-status.json"),
                           ["lc-48000-stereo"], False)

    def test_sbr_allocation_failure_rejected(self):
        with self.assertRaisesRegex(ValueError, "allocation failed"):
            MODULE.analyze(load("wifi-flash", "radio-perf.json"),
                           load("wifi-flash", "radio-status.json"))

    def test_silent_core_fallback_rejected_even_without_allocator_log(self):
        perf = [r for r in load("wifi-flash", "radio-perf.json") if "allocation failed" not in r["line"]]
        for case in ("he-48000-stereo", "hev2-44100-stereo"):
            with self.subTest(case=case), self.assertRaisesRegex(ValueError, "full-rate stereo"):
                MODULE.analyze(perf, load("wifi-flash", "radio-status.json"), [case], False)

    def test_missing_cpu_windows_rejected(self):
        perf = [r for r in load("wifi-flash", "radio-perf.json") if "PERF CPU:" not in r["line"]]
        with self.assertRaisesRegex(ValueError, "CPU windows"):
            MODULE.analyze(perf, load("wifi-flash", "radio-status.json"), ["lc-48000-stereo"], False)


if __name__ == "__main__":
    unittest.main()
