"""Summarize guest instruction demand; never treat QEMU time as hardware CPU load."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("log", type=Path)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--calibration", type=Path,
                    help="Saved ESP32-C3 AAC factor; produces explicitly labelled decoder estimates")
args = parser.parse_args()
text = args.log.read_text(encoding="utf-8-sig")
required_markers = ("QEMU_AAC_WORK_COUNTER nop1024=1025", "QEMU_AAC_WORK_PASS",
                    "QEMU_AAC_FORMAT_PASS", "QEMU_SMOKE_PASS")
for marker in required_markers:
    if marker not in text:
        raise SystemExit("Incomplete or uncalibrated run: missing " + marker)
if re.search(r"assert failed|Guru Meditation|panic'ed", text):
    raise SystemExit("Firmware failure in log")

expected = {
    "lc44100_stereo": (44100, 2, 24, 24576),
    "lc22050_mono": (22050, 1, 13, 13312),
    "lc48000_stereo": (48000, 2, 26, 26624),
    "he44100_stereo": (44100, 2, 14, 28672),
    "he48000_stereo": (48000, 2, 15, 30720),
    "hev2_44100_stereo": (44100, 2, 15, 30720),
}
cases = {name: [] for name in expected}
for line in text.splitlines():
    if "QEMU_AAC_WORK case=" not in line:
        continue
    fields = dict(re.findall(r"(\w+)=(\w+)", line))
    name = fields.pop("case")
    if name not in cases:
        raise SystemExit("Unexpected benchmark case: " + name)
    values = {key: int(value) for key, value in fields.items()}
    rate, channels, frames, samples = expected[name]
    if (values["rate"], values["channels"], values["frames"], values["samples"]) != (
            rate, channels, 8 * frames, 8 * samples):
        raise SystemExit("Wrong decoded layout/sample count: " + name)
    if values["instructions"] <= 0 or not 0 < values["max_call"] < values["instructions"]:
        raise SystemExit("Invalid instruction counter: " + name)
    values["instructions_per_audio_second"] = values["instructions"] * rate / values["samples"]
    cases[name].append(values)

results = []
for name, runs in cases.items():
    if sorted(run["run"] for run in runs) != [1, 2, 3]:
        raise SystemExit("Expected exactly three runs: " + name)
    demands = [run["instructions_per_audio_second"] for run in runs]
    median = statistics.median(demands)
    results.append({
        "case": name, "median_million_instructions_per_audio_second": median / 1e6,
        "run_spread_percent": (max(demands) - min(demands)) / median * 100,
        "hypothetical_decoder_percent_at_160MHz_1_cycle_per_instruction": median / 160e6 * 100,
        "decoder_heap_bytes": max(run["decoder_heap"] for run in runs),
        "runs": runs,
    })

output = {
    "measurement": "RISC-V guest instructions in production ADTS/AAC decode calls",
    "hardware_cpu_load_measured": False,
    "qemu_icount": "shift=0,align=off,sleep=off",
    "counter_calibration": {"nop_instructions": 1024, "observed_including_counter_read": 1025},
    "warmup_repeats": 1, "measured_repeats_per_run": 8, "runs_per_case": 3,
    "log_sha256_utf8_lf": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    "limitations": [
        "QEMU is not cycle accurate; the 160 MHz percentage assumes one cycle per instruction.",
        "Measured calls include ADTS assembly and incidental RTOS interrupts, exclude deliberate delays, UI and PCM output.",
        "No Wi-Fi, TCP/TLS, physical PDM output, cache stalls, or hardware instruction latency is modeled.",
        "Original half-second synthetic fixtures repeated; not a worst-case music/corpus benchmark.",
    ],
    "cases": results,
}
if args.calibration:
    calibration_text = args.calibration.read_text(encoding="utf-8-sig")
    calibration = json.loads(calibration_text)
    environment = re.search(r"QEMU_AAC_WORK_ENV target=(\w+) cpu_hz=(\d+) codec_version=(\S+)", text)
    if not environment or environment.groups() != (calibration.get("target"), str(calibration.get("cpu_hz")), calibration.get("qemu_decoder_runtime_version")):
        raise SystemExit("Calibration target/clock/codec version does not match the QEMU log")
    if (calibration.get("schema_version") != 1 or calibration.get("target") != "esp32c3" or
            calibration.get("cpu_hz") != 160000000 or calibration.get("decoder") != "Espressif AAC" or
            calibration.get("icount") != output["qemu_icount"]):
        raise SystemExit("Incompatible ESP32-C3 AAC calibration")
    factor = calibration["factor"]
    low, high = calibration["observed_factor_range"]
    if not all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in (factor, low, high)) or not low <= factor <= high:
        raise SystemExit("Invalid calibration factors")
    output["calibration"] = {
        "id": calibration["id"], "sha256_utf8_lf": hashlib.sha256(calibration_text.encode("utf-8")).hexdigest(),
        "factor": factor, "observed_factor_range": [low, high],
        "limitations": calibration["limitations"],
    }
    for case in results:
        base = case["hypothetical_decoder_percent_at_160MHz_1_cycle_per_instruction"]
        case["estimated_decoder_percent_at_160MHz"] = base * factor
        case["estimate_using_observed_factor_range_percent"] = [base * low, base * high]
        case["estimate_status"] = ("unvalidated SBR/PS extrapolation from AAC-LC" if case["case"].startswith("he")
                                   else "AAC-LC extrapolation across fixture/layout/adapter")
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
print("Case | M instructions/audio second | hypothetical 1 CPI at 160 MHz | run spread | decoder heap")
for case in results:
    print(f"{case['case']} | {case['median_million_instructions_per_audio_second']:.2f} | "
          f"{case['hypothetical_decoder_percent_at_160MHz_1_cycle_per_instruction']:.2f}% | "
          f"{case['run_spread_percent']:.4f}% | {case['decoder_heap_bytes']}")
if args.calibration:
    print("Calibrated decoder estimates only (not measured CPU or total radio load):")
    for case in results:
        low, high = case["estimate_using_observed_factor_range_percent"]
        print(f"{case['case']} | {case['estimated_decoder_percent_at_160MHz']:.2f}% | "
              f"observed-factor range {low:.2f}-{high:.2f}% | {case['estimate_status']}")
