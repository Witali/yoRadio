#!/usr/bin/env python3
"""Check the retained real-FAAD comparison and reject misleading scale claims."""
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests/results/faad2-history-comparison-20261001"


class FaadComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((EVIDENCE / "comparison.json").read_text())
        cls.rows = cls.data["rows"]

    def test_complete_matrix_and_raw_output(self):
        self.assertEqual(len(self.rows), 60)
        keys = {(r["input"], r["mode"], r["float_scale"], r["scope"]) for r in self.rows}
        self.assertEqual(len(keys), 60)
        for row in self.rows:
            name = f"{row['input']}-{row['mode']}-{row['float_scale']}-{row['scope']}.log"
            raw = json.loads((EVIDENCE / name).read_text())
            for key, value in raw.items():
                self.assertEqual(row[key], value)
            self.assertGreater(row["samples"], 0)
            self.assertGreaterEqual(row["frames"], 30)
            self.assertAlmostEqual(row["pcm_rms_error_lsb"], math.sqrt(row["square_error"] / row["samples"]))
            self.assertEqual(bool(row["maximum"] > 2), bool(row["over_two"]))
            self.assertEqual(bool(row["maximum"] > 5), bool(row["over_five"]))

    def test_fixed_results_and_format_contract(self):
        maxima = {"synthetic_hev2": 3, "abba64": 2, "groovesalad16": 2, "groovesalad64": 2, "groovesalad128": 0}
        for row in self.rows:
            self.assertEqual(row["channels"], 1 if row["input"] == "groovesalad16" else 2)
            self.assertEqual(row["rate"], 32000 if row["input"] == "groovesalad16" else 44100)
            if row["input"] in ("synthetic_hev2", "abba64"):
                self.assertGreater(row["ps_frames"], 0)
            if row["mode"] == "fixed":
                self.assertTrue(row["representable"])
                self.assertEqual(row["over_five"], 0)
                if row["scope"] == 3:
                    self.assertEqual(row["maximum"], maxima[row["input"]])

    def test_controls_are_exact_and_histograms_account_for_overflow(self):
        for row in self.rows:
            if not row["scope"]:
                self.assertEqual(row["different"], 0)
                self.assertEqual(row["maximum"], 0)
            for trace in row["history"]:
                self.assertEqual(sum(trace["exponents"]) + trace["out_of_range"], trace["pairs"])
            self.assertEqual(row["representable"], not any(t["out_of_range"] or t["saturated"] for t in row["history"]))

    def test_apparently_better_enlarged_scale_is_not_qualified(self):
        for name, count in (("abba64", 17439), ("synthetic_hev2", 622)):
            row = next(r for r in self.rows if r["input"] == name and r["mode"] == "float" and r["float_scale"] == 16384 and r["scope"] == 3)
            self.assertEqual(row["maximum"], 1)
            self.assertFalse(row["representable"])
            self.assertEqual(sum(t["out_of_range"] for t in row["history"]), count)

    def test_fixed_to_float_signal_scale_matches_source(self):
        a = next(r for r in self.rows if r["input"] == "abba64" and r["mode"] == "fixed" and r["scope"] == 3)
        b = next(r for r in self.rows if r["input"] == "abba64" and r["mode"] == "float" and r["float_scale"] == 512 and r["scope"] == 3)
        for x, y in zip(a["history"], b["history"]):
            self.assertAlmostEqual(x["rms_native"] / y["rms_native"], 512, delta=0.01)
        self.assertEqual(self.data["scale_invariance"]["interior_scale_invariance_cases"], 98304)
        self.assertTrue(self.data["scale_invariance"]["minimum_shift_exception_checked"])

    def test_probe_and_quantizer_hashes(self):
        for key, path in (("probe_sha256", "tools/codec_benchmark/faad_history_probe.c"),
                          ("quantizer_sha256", "idf/esp32c3-oled-native/main/packed_complex14.h")):
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), self.data["provenance"][key])


if __name__ == "__main__":
    unittest.main()
