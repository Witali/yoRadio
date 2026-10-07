"""Validate live-radio AAC formats and summarize stable 5-second CPU windows."""
import argparse
import json
from pathlib import Path
import re
from statistics import mean

CASES = {"lc-48000-stereo": (48000, "AAC PCM"),
         "he-48000-stereo": (48000, "HE-AAC "),
         "hev2-44100-stereo": (44100, "HE-AACv2 ")}


def analyze(perf, statuses, cases=None, require_changes=True):
    cases = tuple(CASES) if cases is None else tuple(cases)
    if not cases or any(case not in CASES for case in cases):
        raise ValueError("Select known AAC cases")
    result = {"kind": "physical_radio_aac_profile", "cpu_hz": 160000000,
              "deep_sleep": False, "warmup_seconds_excluded": 10,
              "source": "paced LAN HTTP tone fixtures; USB logs and 1 Hz status polling",
              "cpu_method": "FreeRTOS runtime accounting: busy = total - idle",
              "cases": {}}
    for r in perf:
        if (r["case"] in cases or (require_changes and r["case"] == "changing")) and any(s in r["line"] for s in (
                "allocation failed", "decode error", "Fail to", "assert failed", "Guru Meditation", "CORRUPT HEAP")):
            raise ValueError("Firmware failure during playback: " + r["line"])
    for case in cases:
        rate, label = CASES[case]
        states = [r for r in statuses if r["case"] == case and r["seconds"] >= 10]
        if len(states) < 10 or any(not r["audio"] or r["pcm_sample_rate"] != rate or
                r["pcm_channels"] != 2 or r["bits_per_sample"] != 16 or
                not r["format"].startswith(label) for r in states):
            raise ValueError(f"No stable full-rate stereo playback: {case}")
        cpu = [r for r in perf if r["case"] == case and r["seconds"] >= 10 and "PERF CPU:" in r["line"]]
        if len(cpu) < 3:
            raise ValueError(f"Insufficient stable CPU windows: {case}")
        values = [dict((k, float(v)) for k, v in re.findall(r"(\w+)=([\d.]+)%", r["line"])) for r in cpu]
        if any(not 0 <= v["busy"] <= 100 or abs(v["busy"] + v["idle"] - 100) > 0.2 for v in values):
            raise ValueError("Invalid CPU percentage")
        heap = [int(re.search(r"heap=(\d+)", r["line"])[1]) for r in cpu]
        decoded = [r for r in perf if r["case"] == case and r["seconds"] >= 10 and "PERF AAC:" in r["line"]]
        if len(decoded) < 3:
            raise ValueError(f"Insufficient decoder windows: {case}")
        decode_stats = [tuple(map(int, re.search(r"window (\d+) ms, audio (\d+) ms, decode (\d+) ms", r["line"]).groups()))
                        for r in decoded]
        speed = sum(a for _, a, _ in decode_stats) / sum(w for w, _, _ in decode_stats)
        if not 0.9 < speed < 1.1:
            raise ValueError(f"Audio is not proceeding in real time: {case}: {speed}")
        result["cases"][case] = dict(cpu_windows=len(cpu), status_samples=len(states),
            mean_busy_percent=mean(v["busy"] for v in values),
            min_busy_percent=min(v["busy"] for v in values),
            max_busy_percent=max(v["busy"] for v in values),
            mean_task_percent={k: mean(v[k] for v in values) for k in ("decode", "output", "wifi", "tcpip", "web", "stream")},
            min_free_heap_bytes=min(heap), pcm_rate=rate, channels=2,
            mean_decoder_elapsed_percent=100 * sum(d for _, _, d in decode_stats) / sum(a for _, a, _ in decode_stats),
            audio_seconds_per_wall_second=speed, format=states[-1]["format"])
    changing = [r for r in statuses if r["case"] == "changing" and r["audio"]]
    expected = {(rate, label) for rate, label in CASES.values()}
    seen = {(r["pcm_sample_rate"], label) for r in changing for _, label in CASES.values()
            if r["format"].startswith(label) and r["pcm_channels"] == 2}
    if require_changes and not expected <= seen:
        raise ValueError("One HTTP stream did not expose all three AAC formats")
    result["format_changes_in_one_http_stream_verified"] = expected <= seen
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--case", choices=tuple(CASES), action="append")
    parser.add_argument("--skip-changing", action="store_true")
    args = parser.parse_args()
    result = analyze(json.loads((args.directory / "radio-perf.json").read_text(encoding="utf-8")),
                     json.loads((args.directory / "radio-status.json").read_text(encoding="utf-8")),
                     args.case, not args.skip_changing)
    output = args.directory / "radio-summary.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
