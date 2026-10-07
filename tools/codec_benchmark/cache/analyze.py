#!/usr/bin/env python3
"""Validate cache traces; report traffic only, never inferred hardware timing."""
import argparse
import json
from pathlib import Path
import re
from statistics import mean

CASES = {
    "lc48000_stereo": (48000, 26624, 26, 30),
    "he48000_stereo": (48000, 30720, 15, 17),
    "hev2_44100_stereo": (44100, 30720, 15, 16),
}
MODELS = ("continuous_lru", "continuous_fifo", "cold_call_lru")
ROW = re.compile(r"QEMU_CACHE_CASE case=(\w+) pass=(\d+) instructions=(\d+) "
                 r"rate=(\d+) channels=(\d+) samples=(\d+) frames=(\d+) calls=(\d+) stack_free=(\d+)")


def analyze(log: str, trace: dict) -> dict:
    for marker in ("QEMU_CACHE_PASS", "QEMU_SMOKE_PASS", "QEMU_OLED_PASS", "QEMU_AUDIO_PASS",
                   "QEMU_CACHE_ENV target=esp32c3 cpu_hz=160000000 "
                   "codec_version=v2.6.0-4-gfd141ab nop1024=1025"):
        if marker not in log:
            raise ValueError(f"Missing successful check: {marker}")
    if re.search(r"assert failed|Guru Meditation|CORRUPT HEAP|abort\(\)", log):
        raise ValueError("Firmware reported a failure")
    for key, expected in {"schema": 1, "target": "esp32c3", "cache_bytes": 16384,
                          "ways": 8, "line_bytes": 32, "physical_timing_measured": False,
                          "kind": "modelled_flash_cache_traffic", "writeback_bytes": 0,
                          "errors": 0, "unmapped_measured_accesses": 0}.items():
        if trace.get(key) != expected:
            raise ValueError(f"Invalid trace metadata: {key}")
    if trace.get("observed_mmu_writes", 0) <= 0:
        raise ValueError("No MMU mappings observed")
    firmware = {}
    for match in ROW.finditer(log):
        name = match[1]
        run, instructions, rate, channels, samples, frames, calls, stack = map(int, match.groups()[1:])
        key = (name, run)
        if name not in CASES or run not in (1, 2) or key in firmware:
            raise ValueError("Unexpected or duplicate firmware window")
        if (rate, samples, frames, calls) != CASES[name] or channels != 2 or instructions <= 0 or stack < 1024:
            raise ValueError("PCM, instruction or stack validation failed")
        firmware[key] = {"instructions": instructions, "audio_seconds": samples / rate,
                         "calls": calls, "stack_free_bytes": stack}
    expected_keys = {(name, run) for name in CASES for run in (1, 2)}
    if set(firmware) != expected_keys:
        raise ValueError("Incomplete firmware windows")
    seen = set()
    for row in trace["runs"]:
        key = row["case"], row["pass"]
        if key not in firmware or key in seen or row["calls"] != firmware[key]["calls"]:
            raise ValueError("Plugin/firmware windows disagree")
        seen.add(key)
        if set(row["models"]) != set(MODELS):
            raise ValueError("Missing cache model")
        accesses = set()
        for stats in row["models"].values():
            if any(type(n) is not int or n < 0 for n in stats.values()):
                raise ValueError("Invalid cache counter")
            misses = stats["instruction_misses"] + stats["data_misses"]
            if not 0 < stats["instruction_misses"] <= stats["instruction_line_accesses"]:
                raise ValueError("Invalid instruction miss count")
            if not 0 <= stats["data_misses"] <= stats["data_line_accesses"]:
                raise ValueError("Invalid data miss count")
            if stats["refill_bytes"] != 32 * misses or stats["evictions"] > misses:
                raise ValueError("Invalid refill/eviction count")
            accesses.add((stats["instruction_line_accesses"], stats["data_line_accesses"]))
        if len(accesses) != 1:
            raise ValueError("Models saw different accesses")
    if seen != expected_keys:
        raise ValueError("Incomplete plugin windows")
    result = {"kind": "modelled_flash_cache_traffic", "physical_timing_measured": False,
              "refill_penalty_cycles": None, "changes_empirical_coefficients": False,
              "cases": {}}
    for name in CASES:
        rows = [r for r in trace["runs"] if r["case"] == name]
        work = [firmware[name, p]["instructions"] for p in (1, 2)]
        if (max(work) - min(work)) / mean(work) > 0.001:
            raise ValueError("Instruction spread exceeds 0.1%; investigate")
        seconds = firmware[name, 1]["audio_seconds"]
        summary = {"audio_seconds_per_pass": seconds, "instructions": work,
                   "calls_per_pass": CASES[name][3], "models": {}}
        for model in MODELS:
            counts = [r["models"][model] for r in rows]
            misses = [s["instruction_misses"] + s["data_misses"] for s in counts]
            accesses = mean(s["instruction_line_accesses"] + s["data_line_accesses"] for s in counts)
            summary["models"][model] = {
                "mean_instruction_misses": mean(s["instruction_misses"] for s in counts),
                "mean_data_misses": mean(s["data_misses"] for s in counts),
                "total_misses_per_pass": misses,
                "mean_misses_per_audio_second": mean(misses) / seconds,
                "misses_per_100_line_accesses": 100 * mean(misses) / accesses,
                "mean_refill_bytes_per_audio_second": 32 * mean(misses) / seconds,
            }
        summary["cold_minus_continuous_lru_misses_per_audio_second"] = (
            summary["models"]["cold_call_lru"]["mean_misses_per_audio_second"] -
            summary["models"]["continuous_lru"]["mean_misses_per_audio_second"])
        result["cases"][name] = summary
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.log.read_text(encoding="utf-8"), json.loads(args.trace.read_text()))
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"CACHE_TRACE_PASS: {len(result['cases'])} cases, no physical timing inferred")


if __name__ == "__main__":
    main()
