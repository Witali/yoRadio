"""Check benchmark units and reject incomplete/uncalibrated CPU reports."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
LOG = (ROOT / "tests/results/esp32c3-aac-qemu-20260930/qemu.log").read_text(encoding="utf-8-sig")


class SummaryTests(unittest.TestCase):
    def summarize(self, log, succeeds):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "run.log", Path(directory) / "result.json"
            source.write_text(log, encoding="utf-8")
            run = subprocess.run([sys.executable, str(ROOT / "tools/codec_benchmark/summarize_qemu_aac.py"),
                                  str(source), "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(run.returncode == 0, succeeds, run.stderr)
            if succeeds:
                return json.loads(output.read_text())
            self.assertFalse(output.exists())

    def test_units_and_hardware_disclaimer(self):
        result = self.summarize(LOG, True)
        self.assertFalse(result["hardware_cpu_load_measured"])
        self.assertEqual(len(result["cases"]), 6)
        lc = result["cases"][0]
        expected_mips = 49668784 * 44100 / 196608 / 1e6
        self.assertAlmostEqual(lc["median_million_instructions_per_audio_second"], expected_mips)
        self.assertAlmostEqual(lc["hypothetical_decoder_percent_at_160MHz_1_cycle_per_instruction"], expected_mips / 1.6)

    def test_no_counter_calibration(self):
        self.summarize(LOG.replace("nop1024=1025", "nop1024=123456"), False)

    def test_incomplete_run(self):
        self.summarize(LOG.replace("QEMU_AAC_WORK_PASS", "unfinished"), False)

    def test_wrong_sample_count(self):
        self.summarize(LOG.replace("samples=196608", "samples=1", 1), False)

    def test_duplicate_measurement(self):
        line = next(line for line in LOG.splitlines() if "QEMU_AAC_WORK case=" in line)
        self.summarize(LOG + "\n" + line, False)

    def test_firmware_panic(self):
        self.summarize(LOG + "\nGuru Meditation Error\n", False)


if __name__ == "__main__":
    unittest.main()
