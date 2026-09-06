"""Offline precision-only RCPDM experiment; reuse verified RCPDM8 PCM captures.

No capture, network, firmware build, flashing or device access. See the existing
RCPDM8 analyzer for common analog reconstruction and spectral measurement.
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
CONFIGS = {"rc8-a16": 8, "rc8-a4": 8, "rc32-a16": 32}
VARIANTS = {f"{name}-{precision}": bits for name, bits in CONFIGS.items()
            for precision in ("fixed32", "fixed48", "double")}
VARIANTS["pdm32"] = 32


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", type=Path, default=ROOT / "docs/benchmarks/esp8266-rcpdm8-quality-2026-09-06/results.json")
    parser.add_argument("--output", type=Path, default=ROOT / "radio_output/rcpdm-precision")
    parser.add_argument("--archive", type=Path, help="Save verified results and test log here (no broadcast PCM)")
    args = parser.parse_args()
    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    if len(previous["cases"]) != 9:
        raise ValueError("Expected all five saved radio clips and four tones")
    args.output.mkdir(parents=True, exist_ok=True)
    exe = args.output / "build" / ("rcpdm-precision.exe" if platform.system() == "Windows" else "rcpdm-precision")
    subprocess.run(["node", str(ROOT / "tools/esp8266_audio_profile/build_rcpdm8_quality.js"),
                    str(exe.parent), "rcpdm_precision"], check=True)
    checks = json.loads(subprocess.check_output([str(exe), "--self-test"], text=True))
    source_files = ["tools/esp8266_audio_profile/rcpdm_precision.cpp",
                    "tools/esp8266_audio_profile/measure_rcpdm_precision.py",
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
    # Standalone process: only change this instance's variant list, not the
    # original analyzer source or its previous results.
    model.VARIANTS = VARIANTS
    popcount = np.array([i.bit_count() for i in range(256)], dtype=np.uint8)
    for old in previous["cases"]:
        pcm_path = ROOT / old["pcm"]
        if model.sha(pcm_path) != old["pcm_sha256"]:
            raise ValueError(f"Modified PCM: {old['id']}")
        prefix = args.output / old["id"]
        subprocess.run([str(exe), str(pcm_path), str(prefix)], check=True, stdout=subprocess.DEVNULL)
        paths = {name: Path(f"{prefix}.{name}.bin") for name in VARIANTS}
        hashes = {name: model.sha(file) for name, file in paths.items()}
        # Actual original output MUST reproduce the earlier experiment exactly.
        for new, original in {"rc8-a16-fixed32": "rc8-a16", "rc8-a4-fixed32": "rc8-a4",
                              "rc32-a16-fixed32": "rc32", "pdm32": "pdm32"}.items():
            if hashes[new] != old["bitstream_sha256"][original]:
                raise ValueError(f"Baseline bitstream mismatch: {old['id']} {new}")
        row = {key: old[key] for key in ("id", "type", "pcm_sha256", "source", "hz", "level_dbfs") if key in old}
        row["pcm"] = pcm_path.relative_to(ROOT).as_posix()
        row["bitstream_sha256"] = hashes
        row["quality"] = model.analyze(np.fromfile(pcm_path, dtype="<i2"), paths, old.get("hz"))
        row["constant_alternating_only"] = {}
        row["bit_difference_from_fixed32"] = {}
        for name, width in VARIANTS.items():
            words = np.fromfile(paths[name], dtype="u1" if width == 8 else "<u4")
            idle = (0xaa, 0x55) if width == 8 else (0xaaaaaaaa, 0x55555555)
            row["constant_alternating_only"][name] = bool(words[0] in idle and np.all(words == words[0]))
            if name.endswith(("fixed48", "double")):
                base_name = name.rsplit("-", 1)[0] + "-fixed32"
                baseline = np.fromfile(paths[base_name], dtype="u1")
                difference = np.fromfile(paths[name], dtype="u1") ^ baseline
                row["bit_difference_from_fixed32"][name] = dict(changed_bits=int(popcount[difference].sum()), total_bits=len(baseline)*8)
        result["cases"].append(row)
        (args.output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        changed = {name: data["changed_bits"] for name, data in row["bit_difference_from_fixed32"].items()}
        print(f"{len(result['cases'])}/9 {old['id']}: changed bits {changed}", flush=True)
    if args.archive:
        args.archive.mkdir(parents=True, exist_ok=True)
        for name, expected in result["source_sha256"].items():
            if model.sha(ROOT / name) != expected:
                raise ValueError("Source changed during measurement")
        tests = subprocess.run(["node", "--test", "tests/esp8266-rcpdm-precision.test.js",
                                "tests/esp8266-rcpdm8-quality.test.js", "tests/esp8266-rcpdm.test.js"],
                               cwd=ROOT, check=True, capture_output=True, text=True)
        (args.archive / "native-tests.log").write_text(tests.stdout+tests.stderr, encoding="utf-8")
        (args.archive / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        print(f"Archived 9 cases and native regression log: {args.archive}", flush=True)


if __name__ == "__main__":
    main()
