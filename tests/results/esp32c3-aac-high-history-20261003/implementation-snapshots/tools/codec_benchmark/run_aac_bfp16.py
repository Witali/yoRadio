#!/usr/bin/env python3
"""Run the pinned C3 AAC BFP16 numerical experiment; never access a board.

Use the ESP-IDF Python environment (esptool required). Exit 0 means this small
corpus meets 1 LSB, 2 means measured precision rejection, 1 means harness failure.
Neither a corpus pass nor experiment completion qualifies production firmware.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import statistics
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINNED_CODEC_SHA256 = "311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909"
CASES = ("lc44100_stereo", "lc22050_mono", "lc48000_stereo",
         "he44100_stereo", "he48000_stereo", "hev2_44100_stereo")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_log(log):
    for marker in ("BFP16_ARITHMETIC_PASS", "BFP16_COUNTER_PASS nop1024=1025",
                   "BFP16_EXPERIMENT_COMPLETE", "QEMU_AAC_FORMAT_PASS",
                   "QEMU_SMOKE_PASS", "QEMU_OLED_PASS", "QEMU_AUDIO_PASS"):
        if marker not in log:
            raise ValueError(f"Missing completion/validation marker: {marker}")
    rows = []
    for line in log.splitlines():
        if "BFP16_RESULT " not in line:
            continue
        row = dict(re.findall(r"(\w+)=([\w.-]+)", line.split("BFP16_RESULT ", 1)[1]))
        for key in row.keys() - {"case", "precision"}:
            row[key] = int(row[key])
        rows.append(row)
    external = re.findall(r"BFP16_EXTERNAL (.*)", log)
    if len(external) > 1:
        raise ValueError("Duplicate external recording header")
    external = ({k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", external[0])} if external else None)
    cases = ("external",) if external else CASES
    expected = {(case, bands, run) for case in cases
                for bands in ((32,) if case.startswith("lc") else (32, 8, 1, 0))
                for run in (1, 2, 3)}
    actual = {(r["case"], r["bands"], r["run"]) for r in rows}
    if actual != expected or len(rows) != len(expected):
        raise ValueError("Incomplete/duplicate case, block-size or repetition matrix")
    for r in rows:
        if r["samples"] <= 0 or r["frames"] <= 10 or min(r["ref_work"], r["bfp_work"]) <= 0:
            raise ValueError(f"Missing decode work: {r}")
        if r["precision"] != ("FAIL" if r["over_one"] else "PASS"):
            raise ValueError(f"Inconsistent precision result: {r}")
        maximum = max(r["max_l"], r["max_r"])
        if (not 0 <= r["over_one"] <= r["different"] <= r["samples"] or
                bool(maximum > 1) != bool(r["over_one"]) or
                bool(maximum) != bool(r["different"])):
            raise ValueError(f"Inconsistent error counts/maximum: {r}")
        if r["case"].startswith("lc") or not r["bands"] or (external and not external["sbr"]):
            if r["different"] or r["complex_rows"] or r["real_rows"]:
                raise ValueError(f"Unquantized control changed: {r}")
        elif not (r["complex_rows"] + r["real_rows"] and r["changed_qmf"]):
            raise ValueError(f"Quantization hook not exercised: {r}")
    summaries = []
    for case in cases:
        for bands in ((32,) if case.startswith("lc") else (32, 8, 1, 0)):
            group = [r for r in rows if r["case"] == case and r["bands"] == bands]
            overheads = [100 * (r["bfp_work"] / r["ref_work"] - 1) for r in group]
            summaries.append({"case": case, "bands": bands,
                              "max_pcm_error_lsb": max(max(r["max_l"], r["max_r"]) for r in group),
                              "samples_per_run": group[0]["samples"],
                              "over_one_per_run": [r["over_one"] for r in group],
                              "instruction_overhead_median_percent": round(statistics.median(overheads), 3),
                              "instruction_overhead_range_percent": [round(min(overheads), 3), round(max(overheads), 3)]})
    result = {"precision_limit_lsb": 1, "precision_pass": all(not r["over_one"] for r in rows),
            "ram_saved_bytes": 0, "timing_unit": "QEMU guest instructions, not hardware CPU time",
            "summaries": summaries, "runs": rows}
    if external:
        result["external"] = external
        result["error_statistics"] = parse_statistics(log, rows, external)
    return result


def bin_bounds(index):
    if not 0 <= index < 4111:
        raise ValueError("Histogram index outside uint16 absolute-error range")
    return (index, index) if index < 4096 else ((index - 4095) * 4096, (index - 4094) * 4096 - 1)


def error_summary(s, hist):
    count = s["samples"]
    if sum(hist.values()) != count or count <= 0:
        raise ValueError("Histogram sample count differs from PCM count")
    if s["over_one"] != count - hist.get(0, 0) - hist.get(1, 0):
        raise ValueError("Histogram contradicts one-LSB exceedance count")
    if abs(s["signed_sum"]) > s["abs_sum"]:
        raise ValueError("Signed error sum exceeds absolute error sum")
    if not hist or not bin_bounds(max(hist))[0] <= s["maximum"] <= bin_bounds(max(hist))[1]:
        raise ValueError("Histogram contradicts maximum error")
    for power, key in ((1, "abs_sum"), (2, "square_sum")):
        lower = sum(bin_bounds(i)[0] ** power * n for i, n in hist.items())
        upper = sum(bin_bounds(i)[1] ** power * n for i, n in hist.items())
        if not lower <= s[key] <= upper:
            raise ValueError("Error moments contradict histogram")
    quantiles = {}
    for label, numerator in (("p50", 500), ("p90", 900), ("p95", 950), ("p99", 990), ("p999", 999)):
        target = (count * numerator + 999) // 1000
        cumulative = 0
        for index, n in sorted(hist.items()):
            cumulative += n
            if cumulative >= target:
                lo, hi = bin_bounds(index)
                quantiles[label] = [lo, min(hi, s["maximum"])]
                break
    return {"mean_absolute_error_lsb": s["abs_sum"] / count,
            "rms_error_lsb": math.sqrt(s["square_sum"] / count),
            "mean_signed_error_lsb": s["signed_sum"] / count,
            "over_one_percent": 100 * s["over_one"] / count,
            "identical_percent": 100 * hist.get(0, 0) / count,
            "reference_rms_lsb": math.sqrt(s["signal_square_sum"] / count),
            "error_to_full_scale_dbfs": 10 * math.log10(s["square_sum"] / count / 32768 ** 2) if s["square_sum"] else None,
            "signal_to_error_db": 10 * math.log10(s["signal_square_sum"] / s["square_sum"]) if s["square_sum"] and s["signal_square_sum"] else None,
            "absolute_error_percentile_bounds_lsb": quantiles}


def parse_statistics(log, rows, external):
    stats, histograms = {}, {}
    for line in log.splitlines():
        if "BFP16_STATS " in line:
            s = dict(re.findall(r"(\w+)=([\w.-]+)", line.split("BFP16_STATS ", 1)[1]))
            s = {k: (v if k == "case" else int(v)) for k, v in s.items()}
            key = (s["bands"], s["run"], s["channel"])
            if key in stats:
                raise ValueError("Duplicate channel statistics")
            stats[key] = s
        elif "BFP16_HIST " in line:
            fields = dict(re.findall(r"(\w+)=([^ ]+)", line.split("BFP16_HIST ", 1)[1]))
            key = tuple(int(fields[k]) for k in ("bands", "run", "channel"))
            histogram = histograms.setdefault(key, {})
            for index, n in re.findall(r"(\d+):(\d+)", fields["bins"]):
                index, n = int(index), int(n)
                bin_bounds(index)
                if index in histogram or not n:
                    raise ValueError("Duplicate/empty histogram entry")
                histogram[index] = n
    expected = {(r["bands"], r["run"], ch) for r in rows for ch in range(external["channels"])}
    if set(stats) != expected or set(histograms) != expected:
        raise ValueError("Missing/extra per-channel statistics or histogram")
    for r in rows:
        if sum(stats[(r["bands"], r["run"], ch)]["over_one"] for ch in range(external["channels"])) != r["over_one"]:
            raise ValueError("Per-channel exceedances differ from paired result")
        for ch in range(external["channels"]):
            key = r["bands"], r["run"], ch
            s = stats[key]
            if s["samples"] * external["channels"] != r["samples"] or s["maximum"] != r["max_l" if ch == 0 else "max_r"]:
                raise ValueError("Channel statistics disagree with paired comparison")
            s["derived"] = error_summary(s, histograms[key])
            s["histogram"] = {str(k): v for k, v in sorted(histograms[key].items())}
    return list(stats.values())


def run(args, *, log_parser=parse_log, config_key="YORADIO_QEMU_AAC_BFP16_TEST", axis="bands"):
    build = args.build.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    config = (build / "config/sdkconfig.h").read_text()
    for key in ("YORADIO_QEMU", "YORADIO_QEMU_AAC_TEST", config_key,
                "YORADIO_AAC_PLUS", "COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE"):
        if f"#define CONFIG_{key} 1\n" not in config:
            raise ValueError(f"Build is missing {key}")
    archive = args.dependency_root / "esp-adf-libs/esp_audio_codec/lib/esp32c3/libesp_audio_codec.a"
    if sha256(archive) != PINNED_CODEC_SHA256:
        raise ValueError("AAC binary changed: recheck internal function ABI before using wrappers")
    manifest_path = ROOT / "tests/fixtures/aac_stream_format/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for name, entry in manifest["files"].items():
        if sha256(manifest_path.parent / name) != entry["sha256"]:
            raise ValueError(f"Fixture hash mismatch: {name}")
    flash = output / "flash.bin"
    merge = [sys.executable, "-m", "esptool", "--chip", "esp32c3", "merge-bin",
             "-o", str(flash), "--flash-mode", "dio", "--flash-freq", "80m",
             "--flash-size", "4MB", "--pad-to-size", "4MB"]
    for offset, name in (("0x0", "bootloader/bootloader.bin"),
                         ("0x8000", "partition_table/partition-table.bin"),
                         ("0xe000", "ota_data_initial.bin"),
                         ("0x10000", "yoradio_esp32c3_oled_native.bin"), ("0x3b0000", "spiffs.bin")):
        merge += [offset, str(build / name)]
    with (output / "merge.log").open("w") as log:
        subprocess.run(merge, stdout=log, stderr=subprocess.STDOUT, check=True)

    recording = None
    if args.input:
        data = args.input.read_bytes()
        if not 0 < len(data) <= 0x1d0000 - 32:
            raise ValueError("Recording must fit the disposable app1 test region")
        probe = json.loads(subprocess.check_output([args.ffprobe, "-v", "error", "-show_entries",
                            "stream=codec_name,profile,sample_rate,channels", "-show_entries",
                            "format=format_name,duration,bit_rate", "-of", "json", str(args.input)], text=True))
        if probe["format"]["format_name"] != "aac" or len(probe["streams"]) != 1 or probe["streams"][0]["codec_name"] != "aac":
            raise ValueError("External input must be one raw ADTS AAC stream")
        info = probe["streams"][0]
        if info["profile"] not in ("LC", "HE-AAC", "HE-AACv2"):
            raise ValueError("Unrecognized AAC profile; specify a supported test input")
        header = struct.pack("<8I", 0x31504642, len(data), int(info["sample_rate"]), info["channels"],
                             int(info["profile"] != "LC"), 1, 3, 1)
        with flash.open("r+b") as stream:
            stream.seek(0x1e0000)
            stream.write(header + data)
        recording = {"file": str(args.input.resolve()), "sha256": sha256(args.input), "bytes": len(data),
                     "source_url": args.source_url, "ffprobe": probe,
                     "file_completed_utc": datetime.fromtimestamp(args.input.stat().st_mtime, timezone.utc).isoformat(),
                     "transcoding": False}

    def guest_path(path):
        if not args.wsl:
            return str(path)
        return subprocess.check_output(["wsl.exe", "--exec", "wslpath", "-a", path.as_posix()], text=True).strip()

    command = (["wsl.exe", "--cd", guest_path(ROOT), "--exec"] if args.wsl else []) + [args.qemu]
    command += ["-M", "esp32c3,audiodev=audio0", "-nographic", "-no-reboot", "-snapshot",
                "-icount", "shift=0,align=off,sleep=off", "-audiodev",
                f"wav,id=audio0,path={guest_path(output / 'audio.wav')},out.frequency=48000",
                "-L", args.bios, "-drive", f"file={guest_path(flash)},if=mtd,format=raw"]
    with (output / "qemu.log").open("w") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                       timeout=args.timeout, check=True)
    result = log_parser((output / "qemu.log").read_text(errors="replace"))
    result["provenance"] = {"codec_sha256": sha256(archive),
                            "elf_sha256": sha256(build / "yoradio_esp32c3_oled_native.elf"),
                            "sdkconfig_sha256": sha256(build / "sdkconfig"),
                            "fixtures": manifest, "qemu_command": command,
                            "qemu_log_sha256": sha256(output / "qemu.log")}
    if recording:
        result["provenance"]["recording"] = recording
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", newline="\n")
    for row in result["summaries"]:
        print(f"{row['case']:20s} {axis}={row[axis]:2d} max_error={row['max_pcm_error_lsb']:4d} LSB "
              f"instructions={row['instruction_overhead_median_percent']:+.3f}%")
    print("PCM precision:", "PASS (corpus only)" if result["precision_pass"] else f"FAIL (>{result['precision_limit_lsb']} LSB)")
    if result.get("quantization_exercised") is False:
        print("No packed history exercised; this input checks controls and format behavior only.")
    return 0 if result["precision_pass"] else 2


def make_parser(description=__doc__, experiment="bfp16"):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--build", type=Path, default=ROOT / f"idf/esp32c3-oled-native/build-qemu-aac-{experiment}")
    parser.add_argument("--dependency-root", type=Path, default=ROOT / ".idf")
    parser.add_argument("--output", type=Path, default=ROOT / f".build/aac-{experiment}")
    parser.add_argument("--qemu", required=True, help="Executable path in the selected Windows/WSL environment")
    parser.add_argument("--bios", required=True, help="QEMU BIOS directory in the selected environment")
    parser.add_argument("--wsl", action="store_true", help="Run Linux QEMU via WSL from Windows")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--input", type=Path, help="Optional real ADTS recording; default runs the synthetic matrix")
    parser.add_argument("--source-url", default=None, help="Provenance only; the runner makes no network requests")
    parser.add_argument("--ffprobe", default="ffprobe", help="FFprobe executable for external input format verification")
    return parser


if __name__ == "__main__":
    sys.exit(run(make_parser().parse_args()))
