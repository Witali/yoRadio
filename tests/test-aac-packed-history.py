#!/usr/bin/env python3
"""Validate actual packed-history decoder evidence, including rejected precision."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/codec_benchmark"))
import run_aac_packed_history as experiment
import run_aac_bfp16 as common
import summarize_aac_packed_history as summarize

EVIDENCE = ROOT / "tests/results/esp32c3-aac-packed-history-20261001"
NAMES = ("synthetic", "groovesalad64", "groovesalad32", "groovesalad16", "abba64", "groovesalad128")


class PackedHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logs = {name: (EVIDENCE / name / "qemu.log").read_text() for name in NAMES}
        cls.results = {name: json.loads((EVIDENCE / name / "result.json").read_text()) for name in NAMES}

    def test_all_saved_results_are_reproducible_from_raw_logs(self):
        for name in NAMES:
            with self.subTest(name=name):
                parsed = experiment.parse_log(self.logs[name])
                for key, value in parsed.items():
                    self.assertEqual(value, self.results[name][key], key)
                self.assertEqual(common.sha256(EVIDENCE / name / "qemu.log"),
                                 self.results[name]["provenance"]["qemu_log_sha256"])
        self.assertEqual(sum(len(r["runs"]) for r in self.results.values()), 201)

    def test_two_lsb_gate_rejects_measured_three_and_seven_lsb_errors(self):
        for name, maximum in (("synthetic", 7), ("abba64", 3), ("groovesalad16", 3)):
            d = self.results[name]
            self.assertEqual(d["precision_limit_lsb"], 5)
            self.assertEqual(d["production_precision_limit_lsb"], 2)
            self.assertFalse(d["production_precision_pass"])
            self.assertEqual(d["precision_pass"], name != "synthetic")
            self.assertEqual(max(r["max_pcm_error_lsb"] for r in d["summaries"]), maximum)
            self.assertEqual(d["ram_saved_bytes"], 0)

    def test_summary_and_study_units_are_reproducible(self):
        summary, markdown = summarize.report(EVIDENCE)
        self.assertEqual(summary, json.loads((EVIDENCE / "summary.json").read_text()))
        self.assertEqual(markdown, (EVIDENCE / "TABLES.md").read_text(encoding="utf-8"))
        inference = summary["supplied_study_comparison"]
        self.assertAlmostEqual(inference["supplied_inferred_signal_dbfs"], -41.09, places=2)
        self.assertAlmostEqual(inference["supplied_16bit_error_rms_lsb"], 0.02920, places=5)

    def test_inactive_paths_are_not_reported_as_quantizer_coverage(self):
        for name in ("groovesalad64", "groovesalad32", "groovesalad128"):
            self.assertFalse(self.results[name]["quantization_exercised"])
        self.assertTrue(all(h["ps_frames"] == 0 for h in self.results["groovesalad16"]["history"]))
        self.assertTrue(any(h["ps_frames"] > 0 for h in self.results["abba64"]["history"]))

    def test_each_channel_obeys_histogram_and_pcm_error_counts(self):
        for name in NAMES[1:]:
            for s in self.results[name]["error_statistics"]:
                h = s["histogram"]
                self.assertEqual(sum(h.values()), s["samples"])
                self.assertEqual(s["over_two"], s["samples"] - sum(h.get(str(i), 0) for i in range(3)))
                self.assertLessEqual(s["over_two"], s["over_one"])
                self.assertEqual(s["over_limit"], s["samples"] - sum(h.get(str(i), 0) for i in range(6)))

    def test_zero_is_preserved_and_real_inputs_do_not_saturate(self):
        for name in NAMES:
            for d in self.results[name]["quantization"]:
                self.assertEqual(d["zero_to_nonzero"], 0)
                self.assertEqual(d["saturated"], 0)
                self.assertEqual(sum(d["exponent_histogram"].values()), d["pairs"])
                self.assertEqual(sum(d["bucket_histogram"].values()), d["pairs"])

    def test_arithmetic_counter_and_completion_are_required(self):
        for marker in ("PCX14_LIMIT", "PCX14_ARITHMETIC_PASS", "PCX14_COUNTER_PASS", "PCX14_EXPERIMENT_COMPLETE", "QEMU_AAC_FORMAT_PASS"):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                experiment.parse_log(self.logs["synthetic"].replace(marker, "REMOVED"))

    def test_missing_or_duplicate_comparisons_and_history_are_rejected(self):
        for kind in ("RESULT", "HISTORY", "QUANT", "EXP", "RATIO", "STATS", "HIST"):
            log = self.logs["abba64"]
            line = next(s for s in log.splitlines(True) if f"PCX14_{kind} " in s)
            for changed in (log.replace(line, "", 1), log + line):
                with self.subTest(kind=kind), self.assertRaises(ValueError):
                    experiment.parse_log(changed)

    def test_falsified_precision_and_two_lsb_count_are_rejected(self):
        log = self.logs["abba64"]
        with self.assertRaises(ValueError):
            experiment.parse_log(self.logs["synthetic"].replace("precision=FAIL", "precision=PASS", 1))
        changed = re.sub(r"over_two=[1-9]\d*", "over_two=0", log, count=1)
        self.assertNotEqual(changed, log)
        with self.assertRaises(ValueError):
            experiment.parse_log(changed)

    def test_corrupt_coverage_is_rejected(self):
        log = self.logs["abba64"]
        changed = re.sub(r"sbr_frames=[1-9]\d*", "sbr_frames=0", log, count=1)
        with self.assertRaises(ValueError):
            experiment.parse_log(changed)

    def test_original_bfp16_harness_still_runs_and_has_same_pcm(self):
        current = common.parse_log((EVIDENCE / "bfp16-regression/qemu.log").read_text())
        original = json.loads((ROOT / "tests/results/esp32c3-aac-bfp16-20260930/result.json").read_text())
        old = {(r["case"], r["bands"], r["run"]): r for r in original["runs"]}
        for row in current["runs"]:
            before = old[(row["case"], row["bands"], row["run"])]
            for key in ("samples", "frames", "max_l", "max_r", "different", "over_one", "changed_qmf"):
                self.assertEqual(row[key], before[key], key)


if __name__ == "__main__":
    unittest.main()
