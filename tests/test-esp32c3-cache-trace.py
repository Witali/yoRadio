import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cache_analyze", ROOT / "tools/codec_benchmark/cache/analyze.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
RESULTS = ROOT / "tests/results/esp32c3-cache-qemu-20260930"


class CacheTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = json.loads((RESULTS / "run-1.json").read_text())
        self.log = (RESULTS / "run-1.log").read_text(encoding="utf-8")

    def test_saved_runs_are_valid_and_repeatable(self):
        second = json.loads((RESULTS / "run-2.json").read_text())
        result = module.analyze(self.log, self.trace)
        other = module.analyze((RESULTS / "run-2.log").read_text(encoding="utf-8"), second)
        self.assertEqual(result, other)
        self.assertFalse(result["physical_timing_measured"])
        self.assertIsNone(result["refill_penalty_cycles"])
        self.assertFalse(result["changes_empirical_coefficients"])

    def test_partial_or_duplicate_windows_rejected(self):
        self.trace["runs"].pop()
        with self.assertRaises(ValueError):
            module.analyze(self.log, self.trace)
        self.trace["runs"].append(copy.deepcopy(self.trace["runs"][0]))
        with self.assertRaises(ValueError):
            module.analyze(self.log, self.trace)

    def test_plugin_preserves_guest_work_compared_with_windows_qemu(self):
        baseline = (RESULTS / "windows-no-plugin.log").read_text(encoding="utf-8")
        self.assertEqual(module.ROW.findall(baseline), module.ROW.findall(self.log))

    def test_unknown_mmu_mapping_rejected(self):
        self.trace["unmapped_measured_accesses"] = 1
        with self.assertRaises(ValueError):
            module.analyze(self.log, self.trace)

    def test_wrong_geometry_or_hardware_claim_rejected(self):
        for key, value in (("ways", 4), ("physical_timing_measured", True), ("writeback_bytes", 32)):
            modified = copy.deepcopy(self.trace)
            modified[key] = value
            with self.assertRaises(ValueError):
                module.analyze(self.log, modified)

    def test_wrong_pcm_or_counter_rejected(self):
        for old, new in (("rate=48000", "rate=24000"), ("nop1024=1025", "nop1024=777"),
                         ("QEMU_CACHE_PASS", "QEMU_CACHE_FAIL")):
            with self.assertRaises(ValueError):
                module.analyze(self.log.replace(old, new), self.trace)

    def test_invalid_refill_count_rejected(self):
        self.trace["runs"][0]["models"]["continuous_lru"]["refill_bytes"] += 32
        with self.assertRaises(ValueError):
            module.analyze(self.log, self.trace)

    def test_different_access_streams_rejected(self):
        self.trace["runs"][0]["models"]["cold_call_lru"]["data_line_accesses"] += 1
        with self.assertRaises(ValueError):
            module.analyze(self.log, self.trace)

    def test_failure_after_pass_rejected(self):
        with self.assertRaises(ValueError):
            module.analyze(self.log + "\nCORRUPT HEAP", self.trace)


if __name__ == "__main__":
    unittest.main()
