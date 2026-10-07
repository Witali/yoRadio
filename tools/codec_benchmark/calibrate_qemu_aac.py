"""Fit ESP32-C3 AAC instruction cost to the retained physical-board windows."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "tests/results/esp32c3-aac-calibration-20260930"
FIXTURE = ROOT / "tests/fixtures/esp32c3_calibration/aac-lc-320.aac"
FIXTURE_SHA256 = "1b8ee7e7476c2ab5393a6bfffb895f5efd9ab9b83799123ff64cdfa0bc5bc4a5"
EXPECTED = {1: (335, 202528, 970752), 2: (334, 202447, 962560)}
HARDWARE = ("hardware-optimized.log", "hardware-backend-comparison.log")
DECODER_RUNTIME = "v2.6.0-4-gfd141ab"

# The factor fits total elapsed decoder-call time on the reference board.
# Do not add a second cache penalty without first removing its reference share.
CACHE_ACCOUNTING = {
    "reference_cache_stalls_included_in_factor": True,
    "separate_cache_stall_cycles_measured": False,
    "reference_cache_stall_cycles": None,
    "refill_penalty_cycles": None,
    "qemu_cache_miss_counts_available": False,
    "cache": {
        "bytes": 16384, "ways": 8, "line_bytes": 32,
        "read_only": True, "dirty_line_writeback_applicable": False,
    },
    "policy": "Use the saved factor with its reference cache cost included; do not add an unmeasured extra cache multiplier.",
    "future_delta_model": "cycles = instructions * factor + target_cache_stall_cycles - instructions / reference_instructions * reference_cache_stall_cycles",
    "future_delta_model_status": "Requires separately established reference and target stall costs; unavailable in retained measurements.",
    "hardware_reference": "https://documentation.espressif.com/esp32-c3_datasheet_en.html",
}


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_environment(text):
    environment = re.search(r"QEMU_AAC_WORK_ENV target=(\w+) cpu_hz=(\d+) codec_version=(\S+)", text)
    if not environment or environment.groups() != ("esp32c3", "160000000", DECODER_RUNTIME):
        raise ValueError("Target/clock/decoder runtime changed; do not reuse historical hardware calibration")


def calibrate(text, hardware_texts, fixture):
    check_environment(text)
    if hashlib.sha256(fixture).hexdigest() != FIXTURE_SHA256:
        raise ValueError("The original hardware fixture hash does not match")
    for marker in ("QEMU_AAC_WORK_COUNTER nop1024=1025", "QEMU_AAC_CAL_PASS",
                   "QEMU_AAC_WORK_PASS", "QEMU_AAC_FORMAT_PASS", "QEMU_SMOKE_PASS"):
        if marker not in text:
            raise ValueError("Incomplete QEMU run: " + marker)
    if re.search(r"assert failed|Guru Meditation|panic'ed", text):
        raise ValueError("Firmware failure in QEMU log")
    counts = {}
    for line in text.splitlines():
        if "QEMU_AAC_CAL path=" not in line:
            continue
        fields = dict(re.findall(r"(\w+)=(\w+)", line))
        path = fields.pop("path")
        values = {key: int(value) for key, value in fields.items()}
        key = path, values["run"], values["window"]
        if path not in ("legacy", "current") or values["run"] not in (1, 2, 3) or values["window"] not in EXPECTED:
            raise ValueError("Unexpected calibration case")
        if key in counts:
            raise ValueError("Duplicate calibration window")
        if tuple(values[k] for k in ("calls", "consumed", "pcm")) != EXPECTED[values["window"]]:
            raise ValueError("QEMU window differs from the hardware input/PCM/calls")
        if values["instructions"] <= 0:
            raise ValueError("Invalid instruction count")
        counts[key] = values
    if len(counts) != 12:
        raise ValueError("Expected two windows, two paths and three runs")
    reference = {}
    for path in ("legacy", "current"):
        for window in EXPECTED:
            runs = [counts[path, run, window]["instructions"] for run in (1, 2, 3)]
            if max(runs) != min(runs):
                raise ValueError("Instruction counts changed across repeats; investigate before fitting")
            reference[path, window] = statistics.median(runs)

    if set(hardware_texts) != set(HARDWARE):
        raise ValueError("Both retained hardware runs are required")
    hardware_runs = []
    for name in HARDWARE:
        hardware = hardware_texts[name]
        rows = re.findall(r"PERF AAC: window (\d+) ms, audio (\d+) ms, decode (\d+) ms "
                          r"\([^)]+\), calls (\d+), max (\d+) us, in (\d+), pcm (\d+)", hardware)
        if len(rows) != 2:
            raise ValueError("Expected two hardware windows: " + name)
        windows = []
        for window, row in enumerate(rows, 1):
            wall_ms, audio_ms, decode_ms, calls, max_us, consumed, pcm = map(int, row)
            if (calls, consumed, pcm) != EXPECTED[window] or not 0 < decode_ms < wall_ms:
                raise ValueError("Mismatched hardware window: " + name)
            instructions = reference["legacy", window]
            audio_seconds = pcm / (48000 * 2 * 2)
            # Hardware logs floor milliseconds and percent tenths. Derive the
            # ratio from decode milliseconds and exact PCM, not printed 18.7%.
            windows.append({
                "window": window, "decode_ms_floor": decode_ms,
                "pcm_bytes": pcm, "input_bytes": consumed, "calls": calls,
                "instructions": instructions,
                "hardware_decode_percent_approx": decode_ms / 1000 / audio_seconds * 100,
                "qemu_decode_percent_at_1_cpi": instructions / 160e6 / audio_seconds * 100,
                "effective_cycles_per_instruction": decode_ms * 160000 / instructions,
                "current_path_instruction_ratio": reference["current", window] / instructions,
            })
        hardware_runs.append({
            "log": name, "log_sha256_utf8_lf": text_hash(hardware), "windows": windows,
            "weighted_factor": sum(w["decode_ms_floor"] for w in windows) * 160000 /
                               sum(w["instructions"] for w in windows),
        })
    factors = [w["effective_cycles_per_instruction"] for run in hardware_runs for w in run["windows"]]
    return {
        "schema_version": 1,
        "id": "esp32c3-espressif-aac-160mhz-20260930",
        "target": "esp32c3", "cpu_hz": 160000000,
        "decoder": "Espressif AAC", "qemu_codec_version": "2.6.2",
        "qemu_decoder_runtime_version": DECODER_RUNTIME,
        "icount": "shift=0,align=off,sleep=off",
        "factor": hardware_runs[1]["weighted_factor"],
        "factor_selection": "Weighted later backend-comparison run; about 2.02",
        "observed_factor_range": [min(factors), max(factors)],
        "formula": "estimated decoder percent = instructions_per_audio_second / cpu_hz * 100 * factor",
        "cache_accounting": CACHE_ACCOUNTING,
        "hardware_total_cpu_load_measured": False,
        "he_aac_hardware_validated": False,
        "calibration_fixture": {"sha256": FIXTURE_SHA256, "bytes": len(fixture),
                                "codec": "AAC-LC", "sample_rate": 48000, "channels": 2,
                                "target_bitrate": 320000},
        "qemu_log_sha256_utf8_lf": text_hash(text),
        "hardware_runs": hardware_runs,
        "qemu_windows": [{"path": key[0], **value} for key, value in counts.items()],
        "limitations": [
            "Empirical decoder-call elapsed-time factor, not a universal CPU CPI or emulator speed multiplier.",
            "Reference cache refill/stall costs are already included; their separate share was not measured. Adding another cache penalty would double-count it.",
            "Observed range spans two historical firmware builds; it is not a confidence interval or guaranteed bound.",
            "Hardware decode times are floored to milliseconds; counter/timer overhead and preemption are included.",
            "AAC-LC rate/bitrate/channel or adapter changes are extrapolations; HE-AAC SBR/PS transfer is unvalidated.",
            "No estimate of total radio CPU: Wi-Fi, TLS, PDM, display and other work must be added separately.",
            "Historical logs lack a fixture hash and codec archive hash; recovered bytes match saved lengths and both exact PCM/input/call windows.",
            "Recalibrate when codec library, target, clock, memory placement or instruction mix changes.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = calibrate(args.log.read_text(encoding="utf-8-sig"),
                           {name: (EVIDENCE / name).read_text(encoding="utf-8-sig") for name in HARDWARE},
                           FIXTURE.read_bytes())
    except ValueError as error:
        raise SystemExit(str(error)) from error
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Saved decoder factor {result['factor']:.6f}; observed range {result['observed_factor_range']}")
