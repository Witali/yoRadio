#!/usr/bin/env python3
"""Validate retained real-decoder BFP16 evidence and reject misleading passes."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bfp16", ROOT / "tools/codec_benchmark/run_aac_bfp16.py")
bfp16 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bfp16)
EVIDENCE = ROOT / "tests/results/esp32c3-aac-bfp16-20260930"


class Bfp16EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log = (EVIDENCE / "qemu.log").read_text()
        cls.saved = json.loads((EVIDENCE / "result.json").read_text())

    def test_retained_matrix_rejects_precision_and_matches_summary(self):
        parsed = bfp16.parse_log(self.log)
        self.assertFalse(parsed["precision_pass"])
        self.assertEqual(len(parsed["runs"]), 45)
        for key, value in parsed.items():
            self.assertEqual(value, self.saved[key], key)
        for row in parsed["summaries"]:
            if row["bands"] == 1:
                self.assertEqual(row["max_pcm_error_lsb"], 3)

    def test_completion_is_required(self):
        for marker in ("BFP16_EXPERIMENT_COMPLETE", "BFP16_ARITHMETIC_PASS", "BFP16_COUNTER_PASS"):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                bfp16.parse_log(self.log.replace(marker, "REMOVED"))

    def test_raw_log_matches_recorded_hash(self):
        self.assertEqual(bfp16.sha256(EVIDENCE / "qemu.log"),
                         self.saved["provenance"]["qemu_log_sha256"])

    def test_missing_and_duplicate_cases_are_rejected(self):
        row = next(line for line in self.log.splitlines(True) if "BFP16_RESULT " in line)
        for log in (self.log.replace(row, "", 1), self.log + row):
            with self.assertRaises(ValueError):
                bfp16.parse_log(log)

    def test_wrong_precision_label_is_rejected(self):
        with self.assertRaises(ValueError):
            bfp16.parse_log(self.log.replace("precision=FAIL", "precision=PASS", 1))

    def test_unexecuted_quantization_hook_is_rejected(self):
        with self.assertRaises(ValueError):
            bfp16.parse_log(self.log.replace("changed_qmf=42016", "changed_qmf=0", 1))

    def test_control_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            bfp16.parse_log(self.log.replace("max_l=0 max_r=0 different=0", "max_l=1 max_r=0 different=1", 1))

    def test_impossible_maximum_is_rejected(self):
        with self.assertRaises(ValueError):
            bfp16.parse_log(self.log.replace("max_l=5689 max_r=5453", "max_l=1 max_r=1", 1))


if __name__ == "__main__":
    unittest.main()
