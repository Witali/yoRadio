"""Offline direct-comparator RCPDM vs predictive RCPDM and ordinary PDM.

Reuses the previously saved PCM and analog reconstruction model. No network
capture, device access or production firmware changes.
"""
import argparse
import datetime
import json
from pathlib import Path
import platform
import subprocess

import numpy as np
import measure_rcpdm8_quality as model

ROOT = model.ROOT
VARIANTS = {"pdm8": 8, "pdm32": 32, "rc8-a16": 8, "rc8-a16-simple": 8,
            "rc8-a4": 8, "rc8-a4-simple": 8, "rc32": 32, "rc32-simple": 32}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", type=Path, default=ROOT / "docs/benchmarks/esp8266-rcpdm8-quality-2026-09-06/results.json")
    parser.add_argument("--output", type=Path, default=ROOT / "radio_output/rcpdm-simple")
    parser.add_argument("--archive", type=Path, help="Save verified results and regression logs, without broadcast PCM")
    args = parser.parse_args()
    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    if len(previous["cases"]) != 9:
        raise ValueError("Expected all five saved radio clips and four tones")
    args.output.mkdir(parents=True, exist_ok=True)
    exe = args.output / "build" / ("rcpdm-simple-quality.exe" if platform.system() == "Windows" else "rcpdm-simple-quality")
    subprocess.run(["node", str(ROOT / "tools/esp8266_audio_profile/build_rcpdm8_quality.js"),
                    str(exe.parent), "rcpdm_simple_quality"], check=True)
    checks = json.loads(subprocess.check_output([str(exe), "--self-test"], text=True))
    source_files = ["tests/native/rcpdm_simple.h", "tools/esp8266_audio_profile/rcpdm_simple_quality.cpp",
                    "tools/esp8266_audio_profile/measure_rcpdm_simple.py",
                    "tools/esp8266_audio_profile/build_rcpdm8_quality.js",
                    "tools/esp8266_audio_profile/measure_rcpdm8_quality.py",
                    "tests/native/rcpdm8.h", "esp8266/rtos-sdk-native/main/rc_pdm.h",
                    "esp8266/rtos-sdk-native/main/native_audio_output.c"]
    result = dict(measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source_sha256={name: model.sha(ROOT / name) for name in source_files},
                  previous_sha256=model.sha(args.previous), platform=platform.platform(),
                  numpy=np.__version__, self_test=checks, variants=VARIANTS,
                  pcm_rate=model.PCM_RATE, common_grid_rate=model.GRID_RATE,
                  band_hz=[20, 20000], models=previous["models"], note=previous["note"], cases=[])
    model.VARIANTS = VARIANTS  # Only this standalone process, not the original source.
    popcount = np.array([i.bit_count() for i in range(256)], dtype=np.uint8)
    for old in previous["cases"]:
        pcm_path = ROOT / old["pcm"]
        if model.sha(pcm_path) != old["pcm_sha256"]:
            raise ValueError(f"Modified PCM: {old['id']}")
        prefix = args.output / old["id"]
        subprocess.run([str(exe), str(pcm_path), str(prefix)], check=True, stdout=subprocess.DEVNULL)
        paths = {name: Path(f"{prefix}.{name}.bin") for name in VARIANTS}
        hashes = {name: model.sha(file) for name, file in paths.items()}
        for name in ("pdm8", "pdm32", "rc8-a16", "rc8-a4", "rc32"):
            if hashes[name] != old["bitstream_sha256"][name]:
                raise ValueError(f"Baseline bitstream mismatch: {old['id']} {name}")
        row = {key: old[key] for key in ("id", "type", "pcm_sha256", "source", "hz", "level_dbfs") if key in old}
        row["pcm"] = pcm_path.relative_to(ROOT).as_posix()
        row["bitstream_sha256"] = hashes
        row["quality"] = model.analyze(np.fromfile(pcm_path, dtype="<i2"), paths, old.get("hz"))
        row["constant_alternating_only"] = {}
        row["bit_difference_from_predictive"] = {}
        row["listening"] = {}
        for name, width in VARIANTS.items():
            words = np.fromfile(paths[name], dtype="u1" if width == 8 else "<u4")
            idle = (0xaa, 0x55) if width == 8 else (0xaaaaaaaa, 0x55555555)
            row["constant_alternating_only"][name] = bool(words[0] in idle and np.all(words == words[0]))
            row["listening"][name] = model.listening_wav(words, width, Path(f"{prefix}.{name}.wav"))
            if name.endswith("-simple"):
                baseline = np.fromfile(paths[name.removesuffix("-simple")], dtype="u1")
                difference = np.fromfile(paths[name], dtype="u1") ^ baseline
                row["bit_difference_from_predictive"][name] = dict(changed_bits=int(popcount[difference].sum()), total_bits=len(baseline)*8)
        result["cases"].append(row)
        (args.output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        field = "sinad_db" if old["type"] == "tone" else "snr_to_input_db"
        values = {name: row["quality"]["models"][name]["rc10us"][field] for name in VARIANTS}
        print(f"{len(result['cases'])}/9 {old['id']} {field}: {values}", flush=True)
    if args.archive:
        args.archive.mkdir(parents=True, exist_ok=True)
        for name, expected in result["source_sha256"].items():
            if model.sha(ROOT / name) != expected:
                raise ValueError("Source changed during measurement")
        tests = subprocess.run(["node", "--test", "tests/esp8266-rcpdm-simple.test.js",
                                "tests/esp8266-rcpdm-precision.test.js", "tests/esp8266-rcpdm8-quality.test.js",
                                "tests/esp8266-rcpdm.test.js"], cwd=ROOT, check=True, capture_output=True, text=True)
        (args.archive / "native-tests.log").write_text(tests.stdout+tests.stderr, encoding="utf-8")
        import sys
        tests = subprocess.run([sys.executable, "tests/rcpdm8_quality_model_test.py"],
                               cwd=ROOT, check=True, capture_output=True, text=True)
        (args.archive / "model-tests.log").write_text(tests.stdout+tests.stderr, encoding="utf-8")
        (args.archive / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        print(f"Archived 9 cases and regression logs: {args.archive}", flush=True)


if __name__ == "__main__":
    main()
