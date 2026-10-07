#!/usr/bin/env python3
"""Combine channel error moments/histograms without counting reruns as new audio."""
import argparse
import json
from pathlib import Path
from run_aac_bfp16 import error_summary, parse_log, sha256


def summarize(paths):
    rows, recordings = [], []
    for path in paths:
        saved = json.loads(path.read_text())
        log = path.parent / "qemu.log"
        if sha256(log) != saved["provenance"]["qemu_log_sha256"]:
            raise ValueError(f"Log hash mismatch: {path}")
        measured = parse_log(log.read_text())
        for key, value in measured.items():
            if saved[key] != value:
                raise ValueError(f"Saved result differs from raw log: {path}, {key}")
        recording = saved["provenance"]["recording"]
        name = Path(recording["file"]).stem
        rate = saved["external"]["rate"]
        channels = saved["external"]["channels"]
        recordings.append({"name": name, **recording})
        stats = saved["error_statistics"]
        for bands in (32, 8, 1, 0):
            selected = [s for s in stats if s["bands"] == bands and s["run"] == 1]
            # Repetitions demonstrate determinism, not three independent songs.
            for channel in range(channels):
                repeats = [s for s in stats if s["bands"] == bands and s["channel"] == channel]
                comparable = [{k: v for k, v in s.items() if k != "run"} for s in repeats]
                if len(repeats) != 3 or not all(s == comparable[0] for s in comparable):
                    raise ValueError(f"Non-repeatable PCM statistics: {name}, {bands}, {channel}")
            combined = {key: sum(s[key] for s in selected) for key in
                        ("samples", "abs_sum", "square_sum", "signal_square_sum", "signed_sum", "over_one",
                         "clipped_ref", "clipped_bfp")}
            maximum = max(selected, key=lambda s: s["maximum"])
            combined["maximum"] = maximum["maximum"]
            hist = {}
            for s in selected:
                for key, value in s["histogram"].items():
                    index = int(key)
                    hist[index] = hist.get(index, 0) + value
            rows.append({"recording": name, "profile": recording["ffprobe"]["streams"][0]["profile"],
                         "rate": rate, "channels": channels, "bands": bands,
                         "decoded_seconds": combined["samples"] / channels / rate,
                         **combined, **error_summary(combined, hist),
                         "maximum_example": {"channel": maximum["channel"], "sample": maximum["max_at"],
                                             "seconds": maximum["max_at"] / rate,
                                             "reference": maximum["max_ref"], "candidate": maximum["max_bfp"]}
                         if combined["maximum"] else None})
    return {"repetitions": 3, "repetition_statistics_identical": True,
            "aggregation": "channels combined; one continuous pass per recording, reruns not pooled",
            "recordings": recordings, "rows": rows}


def tables(data):
    lines = ["# BFP16 error statistics on real AAC radio recordings", "",
             "All errors are relative to the unmodified Espressif decoder's signed 16-bit PCM.",
             "Three reruns agree exactly; each table counts the audio once, combining L/R.", ""]
    for bands in (32, 8, 1, 0):
        lines += [f"## {'Unmodified control' if bands == 0 else f'{bands} subbands per shared exponent'}", "",
                  "| Recording | Profile / Hz | Samples (L+R) | Max LSB | MAE LSB | RMS LSB | >1 LSB | P99 absolute LSB | Signal/error dB |",
                  "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for row in data["rows"]:
            if row["bands"] != bands:
                continue
            lo, hi = row["absolute_error_percentile_bounds_lsb"]["p99"]
            p99 = str(lo) if lo == hi else f"{lo}-{hi}"
            ratio = row["signal_to_error_db"]
            ratio_text = f"{ratio:.2f}" if ratio is not None else "infinite (identical)"
            lines.append(f"| {row['recording']} | {row['profile']} / {row['rate']} | {row['samples']:,} | "
                         f"{row['maximum']} | {row['mean_absolute_error_lsb']:.6f} | {row['rms_error_lsb']:.6f} | "
                         f"{row['over_one_percent']:.6f}% | {p99} | {ratio_text} |")
        lines.append("")
    lines += ["MAE: mean absolute error. RMS: root mean square error. P99: 99th percentile of absolute error.",
              "Signal/error compares baseline PCM energy with difference energy; it is not an AAC quality score.",
              "Exact histogram bins cover 0-4095 LSB; higher bins have width 4096 and yield percentile bounds.",
              "Error-free runs have zero error energy; their dB ratios are stored as null in JSON.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = summarize(args.results)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    (args.output / "TABLES.md").write_text(tables(data), encoding="utf-8", newline="\n")
    print(tables(data))
