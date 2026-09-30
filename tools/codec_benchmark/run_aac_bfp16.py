#!/usr/bin/env python3
"""Run the pinned C3 AAC BFP16 numerical experiment; never access a board.

Use the ESP-IDF Python environment (esptool required). Exit 0 means this small
corpus meets 1 LSB, 2 means measured precision rejection, 1 means harness failure.
Neither a corpus pass nor experiment completion qualifies production firmware.
"""
import argparse
import hashlib
import json
import re
import statistics
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
    expected = {(case, bands, run) for case in CASES
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
        if r["case"].startswith("lc") or not r["bands"]:
            if r["different"] or r["complex_rows"] or r["real_rows"]:
                raise ValueError(f"Unquantized control changed: {r}")
        elif not (r["complex_rows"] + r["real_rows"] and r["changed_qmf"]):
            raise ValueError(f"Quantization hook not exercised: {r}")
    summaries = []
    for case in CASES:
        for bands in ((32,) if case.startswith("lc") else (32, 8, 1, 0)):
            group = [r for r in rows if r["case"] == case and r["bands"] == bands]
            overheads = [100 * (r["bfp_work"] / r["ref_work"] - 1) for r in group]
            summaries.append({"case": case, "bands": bands,
                              "max_pcm_error_lsb": max(max(r["max_l"], r["max_r"]) for r in group),
                              "samples_per_run": group[0]["samples"],
                              "over_one_per_run": [r["over_one"] for r in group],
                              "instruction_overhead_median_percent": round(statistics.median(overheads), 3),
                              "instruction_overhead_range_percent": [round(min(overheads), 3), round(max(overheads), 3)]})
    return {"precision_limit_lsb": 1, "precision_pass": all(not r["over_one"] for r in rows),
            "ram_saved_bytes": 0, "timing_unit": "QEMU guest instructions, not hardware CPU time",
            "summaries": summaries, "runs": rows}


def run(args):
    build = args.build.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    config = (build / "config/sdkconfig.h").read_text()
    for key in ("YORADIO_QEMU", "YORADIO_QEMU_AAC_TEST", "YORADIO_QEMU_AAC_BFP16_TEST",
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
    result = parse_log((output / "qemu.log").read_text(errors="replace"))
    result["provenance"] = {"codec_sha256": sha256(archive),
                            "elf_sha256": sha256(build / "yoradio_esp32c3_oled_native.elf"),
                            "sdkconfig_sha256": sha256(build / "sdkconfig"),
                            "fixtures": manifest, "qemu_command": command,
                            "qemu_log_sha256": sha256(output / "qemu.log")}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n", newline="\n")
    for row in result["summaries"]:
        print(f"{row['case']:20s} bands={row['bands']:2d} max_error={row['max_pcm_error_lsb']:4d} LSB "
              f"instructions={row['instruction_overhead_median_percent']:+.3f}%")
    print("PCM precision:", "PASS (corpus only)" if result["precision_pass"] else "FAIL (>1 LSB)")
    return 0 if result["precision_pass"] else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=ROOT / "idf/esp32c3-oled-native/build-qemu-aac-bfp16")
    parser.add_argument("--dependency-root", type=Path, default=ROOT / ".idf")
    parser.add_argument("--output", type=Path, default=ROOT / ".build/aac-bfp16")
    parser.add_argument("--qemu", required=True, help="Executable path in the selected Windows/WSL environment")
    parser.add_argument("--bios", required=True, help="QEMU BIOS directory in the selected environment")
    parser.add_argument("--wsl", action="store_true", help="Run Linux QEMU via WSL from Windows")
    parser.add_argument("--timeout", type=int, default=600)
    sys.exit(run(parser.parse_args()))
