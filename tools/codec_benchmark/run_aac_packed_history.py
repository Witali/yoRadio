#!/usr/bin/env python3
"""Qualify 14+14+4 complex SBR/PS history against the pinned C3 AAC decoder.

No board access. Exit 2 is a completed PCM precision rejection, not a broken
experiment. Development permits 5 LSB; production still requires 2 LSB.
"""
import re
import statistics
import sys

import run_aac_bfp16 as common

VARIANTS = {1: "nearest_sbr", 2: "nearest_ps", 3: "nearest_both",
            4: "midpoint_sbr", 5: "midpoint_ps", 6: "midpoint_both",
            7: "lossless_history_traversal", 0: "wrapper_bypass"}


def records(log, kind):
    rows = []
    marker = f"PCX14_{kind} "
    for line in log.splitlines():
        if marker not in line:
            continue
        row = dict(re.findall(r"(\w+)=([\w.-]+)", line.split(marker, 1)[1]))
        rows.append({k: v if k in ("case", "precision") else int(v) for k, v in row.items()})
    return rows


def row_key(r):
    return r["case"], r["variant"], r["run"]


def parse_log(log):
    limits = records(log, "LIMIT")
    if len(limits) != 1 or limits[0].get("production") != 2 or not 1 <= limits[0].get("development", 0) <= 5:
        raise ValueError("Missing/invalid development and production accuracy limits")
    limit = limits[0]["development"]
    for marker in ("PCX14_ARITHMETIC_PASS", "PCX14_COUNTER_PASS nop1024=1025",
                   "PCX14_EXPERIMENT_COMPLETE", "QEMU_AAC_FORMAT_PASS",
                   "QEMU_SMOKE_PASS", "QEMU_OLED_PASS", "QEMU_AUDIO_PASS"):
        if marker not in log:
            raise ValueError(f"Missing validation/completion marker: {marker}")
    rows, histories = records(log, "RESULT"), records(log, "HISTORY")
    headers = records(log, "EXTERNAL")
    if len(headers) > 1:
        raise ValueError("Duplicate external recording header")
    external = headers[0] if headers else None
    cases = ("external",) if external else common.CASES
    expected = {(case, variant, run) for case in cases
                for variant in ((1,) if case.startswith("lc") else VARIANTS)
                for run in (1, 2, 3)}
    if (set(map(row_key, rows)) != expected or len(rows) != len(expected) or
            set(map(row_key, histories)) != expected or len(histories) != len(expected)):
        raise ValueError("Incomplete/duplicate comparison or history matrix")
    history = {row_key(r): r for r in histories}
    for r in rows:
        h = history[row_key(r)]
        variant = r["variant"]
        scope = 3 if variant == 7 else (variant - 1) % 3 + 1
        maximum = max(r["max_l"], r["max_r"])
        if (r["samples"] <= 0 or r["frames"] <= 10 or min(r["ref_work"], r["packed_work"]) <= 0 or
                not 0 <= r["over_two"] <= r["over_one"] <= r["different"] <= r["samples"] or
                bool(maximum > 2) != bool(r["over_two"]) or bool(maximum > 1) != bool(r["over_one"]) or
                bool(maximum > limit) != bool(r["over_limit"]) or not 0 <= r["over_limit"] <= r["different"] or
                bool(maximum) != bool(r["different"]) or
                r["precision"] != ("FAIL" if r["over_limit"] else "PASS")):
            raise ValueError(f"Invalid paired PCM comparison: {r}")
        if (h["pairs"] != 544 * h["sbr_frames"] + 653 * h["ps_frames"] or
                r["complex_rows"] != h["sbr_frames"] + h["ps_frames"] or r["real_rows"] or
                min(h["pairs"], h["sbr_frames"], h["ps_frames"], h["lc_skips"]) < 0):
            raise ValueError("Wrong typed history coverage")
        if not variant and (h["pairs"] or h["lc_skips"]):
            raise ValueError("Bypass touched history")
        if variant and ((not scope & 1 and (h["sbr_frames"] or h["lc_skips"])) or
                        (not scope & 2 and h["ps_frames"])):
            raise ValueError("Wrong history scope")
        sbr = external["sbr"] if external else not r["case"].startswith("lc")
        if not sbr and (h["pairs"] or h["lc_skips"]):
            raise ValueError("AAC-LC unexpectedly entered SBR")
        if sbr and variant and scope & 1 and not h["sbr_frames"] + h["lc_skips"]:
            raise ValueError("SBR hook was not exercised")
        if (not h["pairs"] or variant in (0, 7)) and (r["different"] or r["changed_qmf"]):
            raise ValueError("Unquantized control changed")
        if h["pairs"] and variant not in (0, 7) and not r["changed_qmf"]:
            raise ValueError("Quantization did not change any history values")
    diagnostics = records(log, "QUANT")
    diagnostic_keys = {key for key in expected if key[1] not in (0, 7) and key[2] == 1}
    if set(map(row_key, diagnostics)) != diagnostic_keys or len(diagnostics) != len(diagnostic_keys):
        raise ValueError("Missing/duplicate quantizer diagnostics")
    exponents, ratios = records(log, "EXP"), records(log, "RATIO")
    for d in diagnostics:
        key = row_key(d)
        for entries, field, size in ((exponents, "exponent", 16), (ratios, "bucket", 6)):
            matched = [e for e in entries if row_key(e) == key]
            if (len(matched) != size or {e[field] for e in matched} != set(range(size)) or
                    any(e["count"] < 0 for e in matched) or sum(e["count"] for e in matched) != d["pairs"]):
                raise ValueError("Invalid quantizer histogram")
            d[field + "_histogram"] = {str(e[field]): e["count"] for e in matched}
        if d["pairs"] != history[key]["pairs"] or d["zero_to_nonzero"]:
            raise ValueError("Quantizer coverage/zero preservation failed")
    if len(exponents) != 16 * len(diagnostics) or len(ratios) != 6 * len(diagnostics):
        raise ValueError("Extra diagnostic records")
    summaries = []
    for case in cases:
        for variant in ((1,) if case.startswith("lc") else VARIANTS):
            group = [r for r in rows if r["case"] == case and r["variant"] == variant]
            for field in ("samples", "frames", "different", "over_one", "over_two", "over_limit", "max_l", "max_r", "changed_qmf"):
                if len({r[field] for r in group}) != 1:
                    raise ValueError("Non-deterministic PCM/history comparison")
            # Run 1 includes exhaustive pointer overlap checks and QMF diagnostics.
            overhead = [100 * (r["packed_work"] / r["ref_work"] - 1) for r in group if r["run"] != 1]
            h = history[row_key(group[0])]
            summaries.append({"case": case, "variant": variant, "name": VARIANTS[variant],
                              "coverage": "control" if variant in (0, 7) else "quantized" if h["pairs"] else "not_exercised",
                              "history_pairs_per_run": h["pairs"], "samples_per_run": group[0]["samples"],
                              "max_pcm_error_lsb": max(max(r["max_l"], r["max_r"]) for r in group),
                              "over_one_per_run": [r["over_one"] for r in group],
                              "over_two_per_run": [r["over_two"] for r in group],
                              "over_limit_per_run": [r["over_limit"] for r in group],
                              "instruction_overhead_median_percent": round(statistics.median(overhead), 3),
                              "instruction_overhead_range_percent": [round(min(overhead), 3), round(max(overhead), 3)]})
    result = {"experiment": "complex_history_14_14_4", "precision_limit_lsb": limit,
              "precision_pass": all(not r["over_limit"] for r in rows),
              "production_precision_limit_lsb": 2,
              "production_precision_pass": all(not r["over_two"] for r in rows),
              "quantization_exercised": any(s["coverage"] == "quantized" for s in summaries),
              "ram_saved_bytes": 0, "theoretical_history_payload_saving_bytes_hev2": 4788,
              "timing_unit": "QEMU guest instructions; includes wrapper, bounds checks and basic counters; runs 2/3 only",
              "summaries": summaries, "runs": rows, "history": histories, "quantization": diagnostics}
    if external:
        normalized = log.replace("PCX14_", "BFP16_").replace("variant=", "bands=").replace("packed=", "bfp=").replace("clipped_packed=", "clipped_bfp=")
        old_rows = [dict(r, bands=r["variant"]) for r in rows]
        stats = common.parse_statistics(normalized, old_rows, external)
        for s in stats:
            s["variant"] = s.pop("bands")
            hist = s["histogram"]
            if s["over_two"] != s["samples"] - sum(hist.get(str(k), 0) for k in range(3)):
                raise ValueError("Two-LSB exceedances disagree with histogram")
            if s["over_limit"] != s["samples"] - sum(hist.get(str(k), 0) for k in range(limit + 1)):
                raise ValueError("Development limit exceedances disagree with histogram")
            s["derived"]["over_two_percent"] = 100 * s["over_two"] / s["samples"]
            s["derived"]["over_limit_percent"] = 100 * s["over_limit"] / s["samples"]
        for r in rows:
            channels = [s for s in stats if (s["variant"], s["run"]) == (r["variant"], r["run"])]
            if sum(s["over_two"] for s in channels) != r["over_two"]:
                raise ValueError("Two-LSB channel counts disagree with result")
            if sum(s["over_limit"] for s in channels) != r["over_limit"]:
                raise ValueError("Development-limit channel counts disagree with result")
        result.update(external=external, error_statistics=stats)
    return result


if __name__ == "__main__":
    args = common.make_parser(__doc__, "packed-history").parse_args()
    sys.exit(common.run(args, log_parser=parse_log,
                         config_key="YORADIO_QEMU_AAC_PACKED_HISTORY_TEST", axis="variant"))
