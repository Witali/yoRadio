#!/usr/bin/env python3
"""Retained real-radio PCM evidence, histogram completeness and error metrics."""
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/codec_benchmark"))
from run_aac_bfp16 import bin_bounds, error_summary, parse_log
from summarize_aac_bfp16_real import summarize, tables

EVIDENCE = ROOT / "tests/results/esp32c3-aac-bfp16-real-20260930"
NAMES = ("groovesalad64", "groovesalad32", "groovesalad16", "abba64", "groovesalad128")


class RealBfp16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = (EVIDENCE / "groovesalad64/qemu.log").read_text()

    def test_all_runs_reproduce_saved_statistics_and_tables(self):
        result = summarize([EVIDENCE / name / "result.json" for name in NAMES])
        self.assertEqual(result, json.loads((EVIDENCE / "summary.json").read_text()))
        self.assertEqual(tables(result), (EVIDENCE / "TABLES.md").read_text(encoding="utf-8"))
        self.assertEqual(len(result["rows"]), 20)
        self.assertEqual(sum(r["samples"] for r in result["rows"] if r["bands"] == 0), 12505088)
        for row in result["rows"]:
            if not row["bands"] or row["profile"] == "LC":
                self.assertEqual(row["maximum"], 0)
            elif row["bands"] == 1:
                self.assertEqual(row["maximum"], 3)

    def test_moments_match_direct_small_pcm_comparison(self):
        reference = [1000, -1000, 2000, -2000]
        candidate = [1000, -999, 1998, -1997]
        delta = [b - a for a, b in zip(reference, candidate)]
        s = {"samples": 4, "abs_sum": 6, "square_sum": 14, "signal_square_sum": 10000000,
             "signed_sum": 2, "over_one": 2, "maximum": 3}
        result = error_summary(s, {0: 1, 1: 1, 2: 1, 3: 1})
        self.assertEqual(result["mean_absolute_error_lsb"], sum(abs(x) for x in delta) / 4)
        self.assertEqual(result["rms_error_lsb"], math.sqrt(sum(x * x for x in delta) / 4))
        self.assertEqual(result["mean_signed_error_lsb"], sum(delta) / 4)
        self.assertEqual(result["over_one_percent"], 50)
        self.assertEqual(result["identical_percent"], 25)
        self.assertEqual(result["absolute_error_percentile_bounds_lsb"]["p99"], [3, 3])
        self.assertAlmostEqual(result["signal_to_error_db"], 10 * math.log10(10000000 / 14))

    def test_independent_ffprobe_frame_counts_and_full_formats(self):
        probes = json.loads((EVIDENCE / "ffprobe-frames.json").read_text())
        for name in NAMES:
            result = json.loads((EVIDENCE / name / "result.json").read_text())
            stream = probes[name]["streams"][0]
            for row in result["runs"]:
                self.assertEqual(row["frames"], int(stream["nb_read_frames"]))
            self.assertEqual(result["external"]["rate"], int(stream["sample_rate"]))
            self.assertEqual(result["external"]["channels"], stream["channels"])
            self.assertEqual(result["external"]["sbr"], int(stream["profile"] != "LC"))

    def test_coarse_tail_reports_bounds_and_covers_entire_pcm_difference_range(self):
        self.assertEqual(bin_bounds(4095), (4095, 4095))
        self.assertEqual(bin_bounds(4096), (4096, 8191))
        self.assertEqual(bin_bounds(4110), (61440, 65535))
        with self.assertRaises(ValueError):
            bin_bounds(4111)
        s = {"samples": 1, "abs_sum": 5000, "square_sum": 25000000, "signal_square_sum": 1,
             "signed_sum": -5000, "over_one": 1, "maximum": 5000}
        self.assertEqual(error_summary(s, {4096: 1})["absolute_error_percentile_bounds_lsb"]["p99"], [4096, 5000])

    def test_missing_histogram_is_rejected(self):
        row = next(line for line in self.log.splitlines(True) if "BFP16_HIST " in line)
        with self.assertRaises(ValueError):
            parse_log(self.log.replace(row, "", 1))

    def test_duplicate_histogram_entry_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_log(self.log.replace("bins=0:", "bins=0:1,0:", 1))

    def test_impossible_moments_and_counts_are_rejected(self):
        base = {"samples": 2, "abs_sum": 2, "square_sum": 4, "signal_square_sum": 100,
                "signed_sum": 2, "over_one": 1, "maximum": 2}
        for key, value in (("samples", 3), ("square_sum", 5), ("abs_sum", 3),
                           ("signed_sum", 3), ("over_one", 0), ("maximum", 3)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                error_summary({**base, key: value}, {0: 1, 2: 1})

    def test_incomplete_run_matrix_is_rejected(self):
        row = next(line for line in self.log.splitlines(True) if "BFP16_RESULT " in line)
        with self.assertRaises(ValueError):
            parse_log(self.log.replace(row, "", 1))

    def test_original_stack_failure_cannot_be_a_precision_pass(self):
        log = (EVIDENCE / "initial-4k-stack.log").read_text()
        self.assertIn("stack overflow", log)
        with self.assertRaises(ValueError):
            parse_log(log)

    def test_synthetic_precision_regression_is_unchanged(self):
        old_path = ROOT / "tests/results/esp32c3-aac-bfp16-20260930/result.json"
        old = json.loads(old_path.read_text())
        new = parse_log((EVIDENCE / "synthetic-regression/qemu.log").read_text())
        keys = ("case", "bands", "run", "samples", "frames", "max_l", "max_r",
                "different", "over_one", "complex_rows", "real_rows", "changed_qmf", "max_shift", "precision")
        self.assertEqual([{k: r[k] for k in keys} for r in old["runs"]],
                         [{k: r[k] for k in keys} for r in new["runs"]])


if __name__ == "__main__":
    unittest.main()
