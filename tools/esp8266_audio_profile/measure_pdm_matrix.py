"""Same-frequency PDM / predictive RC-PDM / Simple comparisons, offline only.

Every path uses the same PCM, 6.144-MHz voltage grid and physical RC models.
Lower-rate bits are HELD on that grid; this does not add modulator decisions.
No codec, network, DMA or analog-board measurement is included.
"""
import argparse
import datetime
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import measure_rcpdm8_quality as original

ROOT = original.ROOT
PCM_RATE = 48000
GRID_BITS = 128
GRID_RATE = PCM_RATE * GRID_BITS
BITS = (8, 16, 32, 64, 128)


def variants():
    result = {}
    for bits, matched_shift in zip(BITS, range(2, 7)):
        result[f"pdm{bits}"] = dict(bits=bits, method="pdm", alpha=None, shift=None, role="comparison")
        for shift in dict.fromkeys((4, matched_shift)):
            for prefix, method in (("rc", "predictive"), ("simple", "simple")):
                result[f"{prefix}{bits}-a{1 << shift}"] = dict(
                    bits=bits, method=method, alpha=1 / (1 << shift), shift=shift,
                    role="comparison" if shift == matched_shift else "historical_fixed_alpha_control")
    for config in result.values():
        config["bit_rate_hz"] = PCM_RATE * config["bits"]
        if config["alpha"]:
            config["internal_rc_us"] = float(-1e6 / (
                config["bit_rate_hz"] * np.log1p(-config["alpha"])))
    return result


VARIANTS = variants()
# Exactly the same eight old paths must still emit exactly the same bytes.
BASELINES = {"pdm8": "pdm8", "pdm32": "pdm32", "rc8-a16": "rc8-a16",
             "simple8-a16": "rc8-a16-simple", "rc8-a4": "rc8-a4",
             "simple8-a4": "rc8-a4-simple", "rc32-a16": "rc32",
             "simple32-a16": "rc32-simple"}


def dtype(bits):
    if bits not in BITS:
        raise ValueError("Unsupported bits per PCM sample")
    return {8: "u1", 16: "<u2"}.get(bits, "<u4")


def words_per_frame(bits):
    return max(1, bits // 32)


def bits_to_grid(words, bits, grid_bits=GRID_BITS):
    if bits not in BITS or grid_bits % bits:
        raise ValueError("Grid must be a multiple of the carrier")
    width = min(32, bits)
    words = np.asarray(words, dtype=dtype(bits))
    if words.size % words_per_frame(bits):
        raise ValueError("Truncated PCM frame")
    shifts = np.arange(width - 1, -1, -1, dtype=np.uint32)
    bit_values = ((words[:, None] >> shifts) & 1).reshape(-1)
    return np.repeat(bit_values.astype(np.float64) * 2 - 1, grid_bits // bits)


def analyze(pcm, paths, configs, tone=None, progress=None):
    frames, n = PCM_RATE, PCM_RATE * GRID_BITS
    window = .5 - .5 * np.cos(2 * np.pi * np.arange(n) / n)
    # One-second FFT bins are integer Hz. Retain only audible bins to avoid
    # allocating three full-grid filter spectra for every path.
    frequency = np.arange(20, 20001, dtype=np.float64)
    band = slice(20, 20001)
    aperture = np.sinc(frequency / GRID_RATE) * np.exp(-1j * np.pi * frequency / GRID_RATE)
    models = original.filters(frequency)
    scale = 2 / (n * np.sum(window * window))
    fundamental = abs(frequency - tone) < 1.01 if tone else None
    harmonics = np.zeros(len(frequency), dtype=bool)
    if tone:
        for k in range(2, int(20000 // tone) + 1):
            harmonics |= abs(frequency - k * tone) < 1.01
    words = {name: np.fromfile(path, dtype=dtype(configs[name]["bits"])) for name, path in paths.items()}
    for name, data in words.items():
        if len(data) != len(pcm) * words_per_frame(configs[name]["bits"]):
            raise ValueError(f"Packed output size mismatch: {name}")
    sums = {name: {model: dict(input=0., ideal_rc=0., output=0., error_to_input=0.,
                              error_to_ideal_rc=0., fundamental=0., input_fundamental=0., harmonics=0.)
                   for model in models} for name in paths}
    segments = 0
    for start in range(PCM_RATE // 4, len(pcm) - PCM_RATE // 4 - frames + 1, frames):
        x = np.fft.rfft(np.repeat(pcm[start:start + frames].astype(np.float64) / 32768., GRID_BITS) * window)[band] * aperture
        for name in paths:
            bits = configs[name]["bits"]
            stride = words_per_frame(bits)
            signal = bits_to_grid(words[name][start * stride:(start + frames) * stride], bits)
            y0 = np.fft.rfft(signal * window)[band] * aperture
            for model, h in models.items():
                y, ideal = y0 * h, x * h
                m = sums[name][model]
                for key, spectrum in (("input", x), ("ideal_rc", ideal), ("output", y),
                                      ("error_to_input", y - x), ("error_to_ideal_rc", y - ideal)):
                    m[key] += float(np.sum(abs(spectrum) ** 2) * scale)
                if tone:
                    m["fundamental"] += float(np.sum(abs(y[fundamental]) ** 2) * scale)
                    m["input_fundamental"] += float(np.sum(abs(x[fundamental]) ** 2) * scale)
                    m["harmonics"] += float(np.sum(abs(y[harmonics]) ** 2) * scale)
        segments += 1
        if progress:
            progress(segments)
    if not segments:
        raise ValueError("Need at least 1.5 seconds of PCM")
    result = dict(segments=segments, frames=len(pcm), models={})
    for name, model_sums in sums.items():
        result["models"][name] = {}
        for model, m in model_sums.items():
            row = dict(snr_to_input_db=original.db_ratio(m["input"], m["error_to_input"]),
                       snr_to_ideal_rc_db=original.db_ratio(m["ideal_rc"], m["error_to_ideal_rc"]),
                       output_rms_dbfs=original.db_ratio(m["output"] / segments, 1),
                       error_to_ideal_rc_rms_dbfs=original.db_ratio(m["error_to_ideal_rc"] / segments, 1))
            if tone:
                detected = m["fundamental"] / segments > 1e-18
                row.update(tone_detected=detected,
                           sinad_db=original.db_ratio(m["fundamental"], max(0., m["output"] - m["fundamental"])) if detected else None,
                           thd_db=original.db_ratio(m["harmonics"], m["fundamental"]) if detected and m["harmonics"] / segments > 1e-24 else None,
                           fundamental_gain_db=original.db_ratio(m["fundamental"], m["input_fundamental"]) if detected else None)
            if m["output"] / segments < 1e-24:
                row.update(output_rms_dbfs=None, below_numerical_floor=True)
            result["models"][name][model] = row
    return result


def check_baseline_quality(new, old):
    largest = 0.
    for name, baseline in BASELINES.items():
        for model, row in new["models"][name].items():
            saved = old["models"][baseline][model]
            for key, value in row.items():
                previous = saved.get(key)
                if key.endswith("_db") or key.endswith("_dbfs"):
                    if value is None or previous is None:
                        if value != previous:
                            raise ValueError(f"Baseline detection changed: {name} {model} {key}")
                    else:
                        error = abs(value - previous)
                        largest = max(largest, error)
                        if error > .02:
                            raise ValueError(f"Baseline score changed >0.02dB: {name} {model} {key}: {error}")
                elif value != previous:
                    raise ValueError(f"Baseline flag changed: {name} {model} {key}")
    return largest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", type=Path, default=ROOT / "docs/benchmarks/esp8266-rcpdm-simple-2026-09-06/results.json")
    parser.add_argument("--output", type=Path, default=ROOT / "radio_output/pdm-frequency-matrix")
    parser.add_argument("--archive", type=Path, help="Save hashes/results/tests only; no radio PCM")
    args = parser.parse_args()
    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    if len(previous["cases"]) != 9:
        raise ValueError("Expected five saved radio clips and four tones")
    args.output.mkdir(parents=True, exist_ok=True)
    exe = args.output / "build" / ("pdm-matrix-quality.exe" if platform.system() == "Windows" else "pdm-matrix-quality")
    subprocess.run(["node", str(ROOT / "tools/esp8266_audio_profile/build_rcpdm8_quality.js"),
                    str(exe.parent), "pdm_matrix_quality"], check=True)
    checks = json.loads(subprocess.check_output([str(exe), "--self-test"], text=True))
    sources = ["tools/esp8266_audio_profile/pdm_matrix_quality.cpp",
               "tools/esp8266_audio_profile/measure_pdm_matrix.py",
               "tools/esp8266_audio_profile/build_rcpdm8_quality.js",
               "tools/esp8266_audio_profile/measure_rcpdm8_quality.py",
               "tests/esp8266-pdm-matrix.test.js", "tests/pdm_matrix_quality_model_test.py",
               "tests/native/rcpdm_simple.h", "esp8266/rtos-sdk-native/main/rc_pdm.h",
               "esp8266/rtos-sdk-native/main/native_audio_output.c"]
    result = dict(measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source_sha256={name: original.sha(ROOT / name) for name in sources},
                  previous_sha256=original.sha(args.previous), self_test=checks,
                  platform=platform.platform(), numpy=np.__version__, variants=VARIANTS,
                  pcm_rate=PCM_RATE, common_grid_rate=GRID_RATE, band_hz=[20, 20000],
                  models=previous["models"], note=previous["note"],
                  comparison_rule="Compare methods only at identical bit rate, PCM, physical filter and measurement windows. RC alpha is explicit.",
                  cases=[])
    print("Bit/state self-test:", checks, flush=True)
    for old in previous["cases"]:
        pcm_path = ROOT / old["pcm"]
        if original.sha(pcm_path) != old["pcm_sha256"]:
            raise ValueError(f"Modified PCM: {old['id']}")
        prefix = args.output / old["id"]
        subprocess.run([str(exe), str(pcm_path), str(prefix)], check=True, stdout=subprocess.DEVNULL)
        paths = {name: Path(f"{prefix}.{name}.bin") for name in VARIANTS}
        hashes = {name: original.sha(path) for name, path in paths.items()}
        for name, baseline in BASELINES.items():
            if hashes[name] != old["bitstream_sha256"][baseline]:
                raise ValueError(f"Baseline bits changed: {old['id']} {name}")
        row = {key: old[key] for key in ("id", "type", "pcm", "pcm_sha256", "source", "hz", "level_dbfs") if key in old}
        row["bitstream_sha256"] = hashes
        row["quality"] = analyze(np.fromfile(pcm_path, dtype="<i2"), paths, VARIANTS, old.get("hz"),
                                 lambda count: print(f"{len(result['cases'])+1}/9 {old['id']}: window {count}", flush=True))
        row["baseline_max_difference_db"] = check_baseline_quality(row["quality"], old["quality"])
        row["constant_alternating_only"] = {}
        for name, config in VARIANTS.items():
            bits = config["bits"]
            words = np.fromfile(paths[name], dtype=dtype(bits))
            idle = {8: (0xaa, 0x55), 16: (0xaaaa, 0x5555)}.get(bits, (0xaaaaaaaa, 0x55555555))
            row["constant_alternating_only"][name] = bool(words[0] in idle and np.all(words == words[0]))
        result["cases"].append(row)
        (args.output / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        print(f"Completed {old['id']}; old-grid score delta <= {row['baseline_max_difference_db']:.6f} dB", flush=True)
    for name, expected in result["source_sha256"].items():
        if original.sha(ROOT / name) != expected:
            raise ValueError("Source changed during measurement")
    if args.archive:
        tests = subprocess.run(["node", "--test", "tests/esp8266-pdm-matrix.test.js",
                                "tests/esp8266-direct-pdm.test.js", "tests/esp8266-rcpdm-simple.test.js",
                                "tests/esp8266-rcpdm8-quality.test.js"], cwd=ROOT, check=True, capture_output=True, text=True)
        model_tests = subprocess.run([sys.executable, "tests/pdm_matrix_quality_model_test.py"],
                                     cwd=ROOT, check=True, capture_output=True, text=True)
        args.archive.mkdir(parents=True, exist_ok=True)
        for name, content in (("native-tests.log", tests.stdout+tests.stderr),
                              ("model-tests.log", model_tests.stdout+model_tests.stderr),
                              ("results.json", json.dumps(result, indent=2, allow_nan=False)+"\n")):
            (args.archive / name).write_text(content, encoding="utf-8")
        print(f"Archived {len(result['cases'])} cases: {args.archive}", flush=True)


if __name__ == "__main__":
    main()
