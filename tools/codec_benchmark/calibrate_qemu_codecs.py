"""Compare saved ESP32-C3 hardware timings with identical QEMU decoder windows."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics

from calibrate_qemu_aac import EVIDENCE, ROOT, DECODER_RUNTIME, check_environment, text_hash


def compare(codec, hardware, qemu):
    check_environment(qemu)
    for marker in ("QEMU_AAC_WORK_COUNTER nop1024=1025", "QEMU_AAC_CAL_PASS",
                   "QEMU_CODEC_CAL_PASS codec=" + codec, "QEMU_SMOKE_PASS"):
        if marker not in qemu:
            raise ValueError("Incomplete QEMU run: " + marker)
    if re.search(r"assert failed|Guru Meditation|panic'ed", qemu):
        raise ValueError("Firmware failure in QEMU log")
    rows = re.findall(r"PERF \w+: window (\d+) ms, audio (\d+) ms, decode (\d+) ms "
                      r"\([^)]+\), calls (\d+), max (\d+) us, in (\d+), pcm (\d+)", hardware)
    if len(rows) != 2:
        raise ValueError("Expected two hardware windows")
    measurements = {}
    for line in qemu.splitlines():
        if "QEMU_CODEC_CAL codec=" not in line:
            continue
        fields = dict(re.findall(r"(\w+)=(\w+)", line))
        if fields.pop("codec") != codec:
            raise ValueError("Wrong codec in QEMU log")
        values = {k: int(v) for k, v in fields.items()}
        key = values["run"], values["window"]
        if key in measurements or key[0] not in (1, 2, 3) or key[1] not in (1, 2):
            raise ValueError("Duplicate/unexpected QEMU window")
        measurements[key] = values
    if len(measurements) != 6:
        raise ValueError("Expected three QEMU runs of both windows")
    windows = []
    for index, row in enumerate(rows, 1):
        wall_ms, _, decode_ms, calls, _, consumed, pcm = map(int, row)
        if not 0 < decode_ms < wall_ms:
            raise ValueError("Invalid hardware timing")
        runs = [measurements[run, index] for run in (1, 2, 3)]
        if any((r["calls"], r["consumed"], r["pcm"]) != (calls, consumed, pcm) for r in runs):
            raise ValueError("QEMU/hardware calls, input or PCM mismatch")
        instructions = [run["instructions"] for run in runs]
        # Allocator first-use paths and occasional RTOS interrupts can differ.
        # Retain and bound the observed spread; never hide it by rounding.
        if min(instructions) <= 0 or (max(instructions) - min(instructions)) / min(instructions) > 0.001:
            raise ValueError("Invalid or inconsistent instruction counts")
        count = statistics.median(instructions)
        audio_seconds = pcm / 192000
        windows.append({
            "window": index, "decode_ms_floor": decode_ms, "pcm_bytes": pcm,
            "input_bytes": consumed, "calls": calls, "instructions": count,
            "hardware_decode_percent_approx": decode_ms / 1000 / audio_seconds * 100,
            "qemu_decode_percent_at_1_cpi": count / 160e6 / audio_seconds * 100,
            "effective_cycles_per_instruction": decode_ms * 160000 / count,
            "qemu_run_instructions": instructions,
            "qemu_run_spread_percent": (max(instructions) - min(instructions)) / count * 100,
        })
    factor = sum(w["decode_ms_floor"] for w in windows) * 160000 / sum(w["instructions"] for w in windows)
    factors = [w["effective_cycles_per_instruction"] for w in windows]
    return {
        "codec": codec, "backend": "Espressif", "factor": factor,
        "observed_factor_range": [min(factors), max(factors)],
        "hardware_log_sha256_utf8_lf": text_hash(hardware),
        "qemu_log_sha256_utf8_lf": text_hash(qemu),
        "windows": windows, "runs_per_window": 3,
    }


def build_profile(logs, aac_path=None):
    fixture_root = ROOT / "tests/fixtures/esp32c3_calibration"
    manifest = json.loads((fixture_root / "manifest.json").read_text(encoding="utf-8-sig"))
    cases = []
    for codec in ("mp3", "flac", "vorbis", "opus"):
        fixture = next(f for f in manifest["fixtures"] if f["codec"] == codec)
        data = (fixture_root / fixture["file"]).read_bytes()
        if len(data) != fixture["bytes"] or hashlib.sha256(data).hexdigest() != fixture["sha256"]:
            raise ValueError("Fixture hash/length mismatch: " + codec)
        hardware = (EVIDENCE / f"hardware-{codec}.log").read_text(encoding="utf-8-sig")
        if f"Reading {len(data)}-byte" not in hardware or "cpu freq: 160000000 Hz" not in hardware:
            raise ValueError("Hardware fixture/CPU metadata mismatch: " + codec)
        qemu = (logs / f"qemu-{codec}.log").read_text(encoding="utf-8-sig")
        case = compare(codec, hardware, qemu)
        case["fixture"] = fixture
        cases.append(case)
    if aac_path is None:
        aac_path = ROOT / "tools/codec_benchmark/calibration/esp32c3-aac-160mhz.json"
    aac_text = aac_path.read_text(encoding="utf-8-sig")
    aac = json.loads(aac_text)
    return {
        "schema_version": 1, "id": "esp32c3-espressif-codecs-160mhz-20260930",
        "target": "esp32c3", "cpu_hz": 160000000,
        "qemu_codec_version": "2.6.2", "icount": "shift=0,align=off,sleep=off",
        "qemu_decoder_runtime_version": DECODER_RUNTIME,
        "formula": aac["formula"],
        "universal_factor_supported": False,
        "aac_profile": {"file": aac_path.name, "sha256_utf8_lf": text_hash(aac_text),
                        "factor": aac["factor"], "observed_factor_range": aac["observed_factor_range"]},
        "codecs": cases,
        "limitations": aac["limitations"] + [
            "These four factors fit the earlier optimized hardware build; AAC's preferred factor fits the later build.",
            "FLAC means the Espressif decoder, not the current custom FLAC backend; Helix/minimp3 are also outside scope.",
            "No held-out physical validation; matching source windows calibrates rather than independently validates predictions.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--logs", type=Path, default=EVIDENCE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--aac-calibration", type=Path)
    args = parser.parse_args()
    try:
        result = build_profile(args.logs, args.aac_calibration)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for case in result["codecs"]:
        print(f"{case['codec']}: {case['factor']:.6f}, window range {case['observed_factor_range']}")
