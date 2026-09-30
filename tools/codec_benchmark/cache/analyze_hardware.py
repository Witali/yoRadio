"""Validate identical-image C3 hardware/QEMU runs and derive scoped AAC factors."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from statistics import mean

CASES = {
    "lc48000_stereo": (48000, 26624, 26, 30),
    "he48000_stereo": (48000, 30720, 15, 17),
    "hev2_44100_stereo": (44100, 30720, 15, 16),
}
CPU_HZ = 160_000_000


def rows(log, prefix):
    return [dict(re.findall(r"(\w+)=([^\s]+)", line))
            for line in log.splitlines() if line.startswith(prefix + " ")]


def parse(log, runtime):
    env = rows(log, "CACHE_HW_ENV")
    expected = dict(target="esp32c3", runtime=runtime, cpu_hz=str(CPU_HZ),
                    pcer="1" if runtime == "hardware" else "0",
                    codec_version="v2.6.0-4-gfd141ab", deep_sleep="0",
                    irq_masked="1", flash_mode="dio", flash_mhz="80")
    if env != [expected] or log.count(f"CACHE_HW_PASS runtime={runtime}") != 1:
        raise ValueError("Missing or inconsistent environment/completion marker")
    if re.search(r"assert failed|Guru Meditation|CORRUPT HEAP|abort\(\)", log):
        raise ValueError("Firmware failure")
    if runtime == "qemu" and rows(log, "CACHE_ICOUNT_PROBE") != [dict(nops="1024", instructions="1025")]:
        raise ValueError("QEMU did not count guest instructions")
    probes = [{k: int(v) for k, v in r.items()} for r in rows(log, "CACHE_PROBE")]
    probe_keys = {(r["lines"], r["run"]) for r in probes}
    if len(probes) != 32 or probe_keys != {(n, r) for n in (1, 8, 64, 256) for r in range(1, 9)}:
        raise ValueError("Missing or duplicate cache probes")
    for r in probes:
        expected_cold = r["lines"] if runtime == "hardware" else 0
        if (r["cold_i"], r["warm_i"], r["cold_d"], r["warm_d"]) != (0, 0, expected_cold, 0):
            raise ValueError("Cache probe does not validate one miss per cold data line")
        expected_access = r["lines"] if runtime == "hardware" else 0
        if (r["cold_da"], r["warm_da"]) != (expected_access, expected_access):
            raise ValueError("Unexpected cache probe accesses")
        if r["warm_ticks"] <= 0 or r["cold_ticks"] < r["warm_ticks"]:
            raise ValueError("Invalid probe timing")
    decoded = []
    for row in rows(log, "CACHE_DECODE"):
        r = {k: v if k in ("case", "mode") else int(v) for k, v in row.items()}
        if r["case"] not in CASES or r["mode"] not in ("continuous", "cold"):
            raise ValueError("Unknown case/mode")
        if tuple(r[k] for k in ("rate", "samples", "frames", "calls")) != CASES[r["case"]] or r["channels"] != 2:
            raise ValueError("Wrong PCM format or frame/call count")
        if r["ticks"] <= 0 or r["us"] <= 0 or r["max_us"] <= 0 or r["stack_free"] < 1024:
            raise ValueError("Invalid timer or insufficient stack")
        if runtime == "hardware":
            if not (0 < r["im_raw"] <= r["ia"] and 0 < r["dm_raw"] <= r["da"]):
                raise ValueError("Invalid hardware miss/access counters")
            # esp_timer brackets both cycle reads; allow integer-us quantization
            # and the small per-call timer wrapper, not milliseconds of drift.
            if abs(r["us"] - r["ticks"] / 160) > 3 * r["calls"]:
                raise ValueError("Cycle counter and wall timer disagree")
        elif any(r[k] for k in ("ia", "im_raw", "da", "dm_raw")):
            raise ValueError("Unexpected QEMU cache counters")
        decoded.append(r)
    keys = {(r["case"], r["mode"], r["round"], r["pass"]) for r in decoded}
    expected_keys = {(c, m, r, p) for c in CASES for m in ("continuous", "cold")
                     for r in range(1, 5) for p in range(1, 4)}
    if len(decoded) != len(expected_keys) or keys != expected_keys:
        raise ValueError("Missing or duplicate decoder windows")
    return probes, decoded


def analyze(hardware_logs, qemu_logs):
    if len(hardware_logs) < 2 or len(qemu_logs) < 2:
        raise ValueError("At least two complete runs per runtime are required")
    hardware = [parse(log, "hardware") for log in hardware_logs]
    qemu = [parse(log, "qemu") for log in qemu_logs]
    result = dict(schema_version=1, target="esp32c3", cpu_hz=CPU_HZ,
                  kind="same_image_hardware_aac_cache_calibration", deep_sleep=False,
                  hardware_runs=len(hardware), qemu_runs=len(qemu),
                  hardware_decoder_timing_measured=True, whole_radio_cpu_measured=False,
                  universal_refill_penalty_cycles=None, historical_factor_replaced=False,
                  instruction_cache_line_semantics_independently_validated=False,
                  data_cache_line_semantics_validated=True, cases={}, probes={})
    for lines in (1, 8, 64, 256):
        p = [r for probes, _ in hardware for r in probes if r["lines"] == lines]
        cold, warm = mean(r["cold_ticks"] for r in p), mean(r["warm_ticks"] for r in p)
        result["probes"][str(lines)] = dict(cold_cycles=cold, warm_cycles=warm,
            extra_cycles_per_cold_line=(cold - warm) / lines)
    for case, (rate, samples, _, _) in CASES.items():
        entry = dict(rate=rate, channels=2, samples_per_pass=samples, modes={})
        for mode in ("continuous", "cold"):
            h = [r for _, dec in hardware for r in dec if r["case"] == case and r["mode"] == mode]
            q = [r for _, dec in qemu for r in dec if r["case"] == case and r["mode"] == mode]
            cycles, instructions = mean(r["ticks"] for r in h), mean(r["ticks"] for r in q)
            spread = (max(r["ticks"] for r in h) - min(r["ticks"] for r in h)) / cycles
            if spread > 0.01:
                raise ValueError("Hardware spread exceeds 1%; inspect run conditions")
            if (max(r["ticks"] for r in q) - min(r["ticks"] for r in q)) / instructions > 0.001:
                raise ValueError("QEMU instruction spread exceeds 0.1%")
            factor = cycles / instructions
            entry["modes"][mode] = dict(windows=len(h), mean_cycles=cycles,
                min_cycles=min(r["ticks"] for r in h), max_cycles=max(r["ticks"] for r in h),
                cycle_spread_percent=100 * spread, mean_qemu_instructions=instructions,
                decoder_cpu_percent=100 * cycles / CPU_HZ / (samples / rate),
                effective_cycles_per_instruction=factor,
                historical_2_018_factor_error_percent=100 * (2.018192916067804 / factor - 1),
                mean_instruction_misses_raw=mean(r["im_raw"] for r in h),
                mean_data_misses=mean(r["dm_raw"] for r in h),
                maximum_call_us=max(r["max_us"] for r in h))
        a, b = entry["modes"]["continuous"], entry["modes"]["cold"]
        delta_cycles = b["mean_cycles"] - a["mean_cycles"]
        delta_misses = (b["mean_instruction_misses_raw"] + b["mean_data_misses"]
                        - a["mean_instruction_misses_raw"] - a["mean_data_misses"])
        entry.update(cold_extra_cycles=delta_cycles,
            cold_extra_decoder_percent_points=b["decoder_cpu_percent"] - a["decoder_cpu_percent"],
            cold_relative_slowdown_percent=100 * delta_cycles / a["mean_cycles"],
            cold_extra_misses_raw=delta_misses,
            observed_delta_cycles_per_extra_miss=delta_cycles / delta_misses if delta_misses > 0 else None)
        result["cases"][case] = entry
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hardware", type=Path, action="append", required=True)
    parser.add_argument("--qemu", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = analyze([p.read_text(encoding="utf-8-sig") for p in args.hardware],
                      [p.read_text(encoding="utf-8-sig") for p in args.qemu])
    summary["log_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in args.hardware + args.qemu}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(args.hardware)} hardware and {len(args.qemu)} QEMU runs: {args.output}")


if __name__ == "__main__":
    main()
