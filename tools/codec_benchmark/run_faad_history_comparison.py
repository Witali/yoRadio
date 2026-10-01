#!/usr/bin/env python3
"""Download pinned FAAD2 and compare fixed/float history quantization on a host.

Uses WSL GCC on Windows or native GCC on Linux. Never flashes or changes the
firmware backend. The original supplied FAAD experiment source is unavailable;
this is a new, explicitly scoped comparison, not a reproduction of its claims.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
REVISION = "e8e76f0a44db45aed773a3f62fe35a63c867a738"
ARCHIVE_SHA256 = "36f5aa8cbfcc442cdaced7f29dbe66276c62a1432d3c639405c07bcdf47614ab"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def host_path(path):
    path = path.resolve()
    if sys.platform == "win32":
        return "/mnt/" + path.drive[0].lower() + path.as_posix()[2:]
    return str(path)


def host_command(args):
    return (["wsl.exe", "--exec"] if sys.platform == "win32" else []) + args


def run(output, recordings):
    output.mkdir(parents=True, exist_ok=True)
    url = f"https://codeload.github.com/knik0/faad2/tar.gz/{REVISION}"
    archive = output / f"faad2-{REVISION}.tar.gz"
    if not archive.exists():
        with urllib.request.urlopen(url, timeout=90) as response:
            archive.write_bytes(response.read())
    if digest(archive) != ARCHIVE_SHA256:
        raise ValueError("FAAD source archive hash changed")
    source = output / f"faad2-{REVISION}"
    if not source.exists():
        with tarfile.open(archive) as bundle:
            bundle.extractall(output, filter="data")
    # Verify even an existing extraction before compiling or quoting its files.
    with tarfile.open(archive) as bundle:
        for entry in bundle.getmembers():
            if entry.isfile():
                if (output / entry.name).read_bytes() != bundle.extractfile(entry).read():
                    raise ValueError(f"Modified reference source: {entry.name}")
    common = ["gcc", "-O2", "-fno-strict-aliasing", "-ffloat-store",
              "-DHAVE_INTTYPES_H=1", "-DHAVE_MEMCPY=1", "-DHAVE_STRING_H=1",
              "-DHAVE_STRINGS_H=1", "-DHAVE_SYS_STAT_H=1", "-DHAVE_SYS_TYPES_H=1",
              "-DHAVE_LRINTF=1", '-DPACKAGE_VERSION="comparison"', "-DAPPLY_DRC"]
    common += ["-I" + host_path(source / "include"), "-I" + host_path(source / "libfaad"),
               "-I" + host_path(ROOT / "idf/esp32c3-oled-native/main")]
    common += [host_path(p) for p in sorted((source / "libfaad").glob("*.c"))]
    common += [host_path(ROOT / "tools/codec_benchmark/faad_history_probe.c"), "-lm"]
    commands = {}

    def build(mode):
        command = common + (["-DFIXED_POINT=1"] if mode == "fixed" else [])
        command += ["-o", host_path(output / f"probe-{mode}")]
        with (output / f"build-{mode}.log").open("w") as log:
            subprocess.run(host_command(command), stdout=log, stderr=subprocess.STDOUT, check=True)
        commands[mode] = command

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(build, ("fixed", "float")))
    scale_test = json.loads(subprocess.check_output(
        host_command([host_path(output / "probe-fixed"), "--quantizer-scale-test"]), text=True))
    inputs = {"synthetic_hev2": ROOT / "tests/fixtures/aac_stream_format/hev2-44100-stereo.aac"}
    for name in ("abba64", "groovesalad16", "groovesalad64", "groovesalad128"):
        inputs[name] = recordings / f"{name}.aac"
    rows = []
    for name, path in inputs.items():
        repeats = 2 if name == "synthetic_hev2" else 1
        expected_rate = 32000 if name == "groovesalad16" else 44100
        expected_channels = 1 if name == "groovesalad16" else 2
        for mode, scale in (("fixed", 1), ("float", 512), ("float", 16384)):
            for scope in range(4):
                command = [host_path(output / f"probe-{mode}"), host_path(path), str(scope), str(scale), str(repeats)]
                completed = subprocess.run(host_command(command), text=True, capture_output=True)
                (output / f"{name}-{mode}-{scale}-{scope}.log").write_text(
                    completed.stdout + completed.stderr, encoding="utf-8")
                completed.check_returncode()
                row = json.loads(completed.stdout)
                if row["samples"] <= 0 or row["frames"] < 10 or row["channels"] != expected_channels or row["rate"] != expected_rate:
                    raise ValueError(f"Missing full-rate comparison: {name}, {row}")
                if name in ("synthetic_hev2", "abba64") and not row["ps_frames"]:
                    raise ValueError("Required PS path not exercised")
                if scope == 0 and (row["different"] or row["maximum"]):
                    raise ValueError("Lossless control differs")
                row.update(input=name, mode=mode, repeats=repeats, input_sha256=digest(path),
                           pcm_rms_error_lsb=math.sqrt(row["square_error"] / row["samples"]),
                           reference_dbfs=10 * math.log10(row["square_signal"] / row["samples"] / 32768**2))
                row["representable"] = not any(h["out_of_range"] or h["saturated"] for h in row["history"])
                rows.append(row)
                print(name, mode, scale, scope, "max", row["maximum"], "rms", round(row["pcm_rms_error_lsb"], 4))
    result = {"scale_invariance": scale_test,
              "provenance": {"repository": "https://github.com/knik0/faad2", "revision": REVISION,
               "archive_url": url, "archive_sha256": digest(archive),
               "compiler": subprocess.check_output(host_command(["gcc", "--version"]), text=True).splitlines()[0],
               "build_commands": commands,
               "probe_sha256": digest(ROOT / "tools/codec_benchmark/faad_history_probe.c"),
               "quantizer_sha256": digest(ROOT / "idf/esp32c3-oled-native/main/packed_complex14.h")},
              "scope": {"1": "retained Xsbr rows only", "2": "PS four delay arrays only, excludes gains/phase/hybrid",
                        "3": "both", "0": "control"},
              "note": "A separate reference-backend experiment; not the supplied study, not ESP32 CPU timing or production qualification",
              "rows": rows}
    (output / "comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/faad2-comparison")
    parser.add_argument("--recordings", type=Path, default=ROOT / ".build/aac-bfp16-real-20260930/inputs")
    args = parser.parse_args()
    run(args.output.resolve(), args.recordings.resolve())
