"""Sweep reduced, exactly zero-mean TPDF dither; no firmware/device changes.

Feedback, interpolation, RC recurrence, bit rate and PRNG are held fixed.
Full/zero amplitude controls must reproduce the previously archived bitstreams.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess

import numpy as np
import measure_pdm_matrix as model
from measure_rcpdm_feedback_ab import save, assert_saved_scores, complex_json
from inspect_rcpdm_no_dither import REPORTS, lsb_windows, spurs

ROOT = model.ROOT
RATE, BITS, SEED = 48000, 32, 2654435769
CARRIER = RATE * BITS
VARIANTS = {"full": 0, **{f"div{1 << s}": s for s in range(1, 7)}, "none": None}


def generate(exe, pcm, prefix, seed, method, shift):
    command = [str(exe), str(pcm), str(prefix), str(seed)]
    if method == "simple":
        command.append("simple")
    command.append("no-dither" if shift is None else f"dither-shift={shift}")
    proof = json.loads(subprocess.check_output(command, text=True))
    if (proof["method"] != method or proof["dither"] != (0 if shift is None else 2)
            or proof["dither_shift"] != (shift or 0)
            or proof["frames"] != proof["on_reference_frames"]
            or not proof["prng_and_interpolation_identical"]):
        raise ValueError("Wrong modulator or failed bit/state reference")
    return Path(str(prefix) + ".on.bin"), proof


def fixed_delay(pcm, paths):
    """Identical fixed interpolation delay, not a fitted gain/delay."""
    n = RATE * model.GRID_BITS
    frequency = np.arange(20, 20001)
    window = .5 - .5 * np.cos(2 * np.pi * np.arange(n) / n)
    aperture = np.sinc(frequency / model.GRID_RATE) * np.exp(-1j * np.pi * frequency / model.GRID_RATE)
    delay = (BITS - 1) / (2 * CARRIER)
    rotation = np.exp(-2j * np.pi * frequency * delay)
    h = model.original.filters(frequency)["rc10us"]
    words = {name: np.fromfile(path, dtype="<u4") for name, path in paths.items()}
    signal = 0.
    errors = {name: dict(raw=0., aligned=0.) for name in paths}
    for start in range(RATE // 4, len(pcm) - RATE // 4 - RATE + 1, RATE):
        x = np.fft.rfft(np.repeat(pcm[start:start + RATE].astype(np.float64) / 32768, model.GRID_BITS) * window)[20:20001] * aperture
        signal += float(np.sum(abs(x) ** 2))
        for name in paths:
            y = np.fft.rfft(model.bits_to_grid(words[name][start:start + RATE], BITS) * window)[20:20001] * aperture * h
            errors[name]["raw"] += float(np.sum(abs(y - x) ** 2))
            errors[name]["aligned"] += float(np.sum(abs(y - x * rotation) ** 2))
    return dict(fixed_delay_seconds=delay, models={
        name: {key + "_snr_db": model.original.db_ratio(signal, value) for key, value in row.items()}
        for name, row in errors.items()})


def summarize_windows(gains):
    gains = np.asarray(gains)
    mean = complex(np.mean(gains))
    return dict(coherent_mean=complex_json(mean), gain_magnitude=float(abs(mean)),
        window_gain_min=float(np.min(abs(gains))), window_gain_max=float(np.max(abs(gains))),
        complex_deviation_rms=float(np.sqrt(np.mean(abs(gains - mean) ** 2))),
        complex_deviation_max=float(np.max(abs(gains - mean))))


def lsb_analysis(exe, output, method, controls):
    output.mkdir(parents=True, exist_ok=True)
    half = np.round(np.sin(2 * np.pi * (np.arange(24) + .5) / 48)).astype("<i2")
    period = np.r_[half, -half]
    assert period.sum() == 0 and min(period) == -1 and max(period) == 1
    signals = {"zero": np.zeros(480000, dtype="<i2"),
        "dc-plus": np.ones(480000, dtype="<i2"), "dc-minus": -np.ones(480000, dtype="<i2"),
        "tone-plus": np.tile(period, 10000), "tone-minus": -np.tile(period, 10000)}
    files = {}
    for name, pcm in signals.items():
        files[name] = output / (name + ".s16le")
        pcm.tofile(files[name])
        if model.original.sha(files[name]) != controls["full"]["lsb"]["pcm_sha256"][name]:
            raise ValueError("LSB input differs from baseline")
    phase = np.exp(-2j * np.pi * np.arange(1536) / 1536)
    aperture = np.sinc(1000 / CARRIER) * np.exp(-1j * np.pi * 1000 / CARRIER)
    transfer = aperture / (1 + 2j * np.pi * 1000 * 1e-5)
    reference = 2 * np.dot(np.repeat(period.astype(np.float64) / 32768, 32), phase) / 1536 * aperture
    result = dict(reference=complex_json(reference), total_seconds=10, window_seconds=1,
        windows_per_seed=8, trim_start_seconds=.25, band_model="rc10us",
        pcm_sha256={name: model.original.sha(path) for name, path in files.items()}, variants={})
    for variant, shift in VARIANTS.items():
        seed_rows, all_gains, dc_plus, dc_minus = [], [], [], []
        for seed in (1, 8266, SEED):
            measurements, paths = {}, {}
            for name, file in files.items():
                path, proof = generate(exe, file, output / f"{variant}-{name}-{seed}", seed, method, shift)
                sha = model.original.sha(path)
                if variant in controls:
                    baseline = next(s for s in controls[variant]["lsb"]["seeds"] if s["seed"] == seed)["models"]["on"][name]
                    if sha != baseline["bitstream_sha256"]:
                        raise ValueError("LSB control bitstream changed")
                words = np.fromfile(path, dtype="<u4")[12000:396000]
                bits = ((words[:, None] >> np.arange(31, -1, -1, dtype=np.uint32)) & 1).astype(np.uint8).reshape(-1)
                average = bits.reshape(-1, 1536).mean(axis=0) * 2 - 1
                coefficient = 2 * np.dot(average, phase) / 1536 * transfer
                measurements[name] = dict(bitstream_sha256=sha, proof=proof, coherent=complex_json(coefficient),
                    mean_pcm_lsb=float((bits.mean() * 2 - 1) * 32768))
                paths[name] = path
            positive, negative = [np.fromfile(paths["tone-" + polarity], dtype="<u4") for polarity in ("plus", "minus")]
            gains = lsb_windows(positive, negative, reference)
            coherent = (complex(**measurements["tone-plus"]["coherent"]) - complex(**measurements["tone-minus"]["coherent"])) / (2 * reference)
            if abs(np.mean(gains) - coherent) > 1e-10:
                raise ValueError("Windowed gain does not reproduce eight-second coherent gain")
            dp = measurements["dc-plus"]["mean_pcm_lsb"] - measurements["zero"]["mean_pcm_lsb"]
            dm = measurements["dc-minus"]["mean_pcm_lsb"] - measurements["zero"]["mean_pcm_lsb"]
            seed_rows.append(dict(seed=seed, measurements=measurements, gains=[complex_json(g) for g in gains],
                summary=summarize_windows(gains), dc_plus_lsb=dp, dc_minus_lsb=dm))
            all_gains.extend(gains);dc_plus.append(dp);dc_minus.append(dm)
            print(f"{method} {variant}: LSB seed {seed} complete", flush=True)
        if shift is None:
            for row in seed_rows[1:]:
                for name in signals:
                    if row["measurements"][name]["bitstream_sha256"] != seed_rows[0]["measurements"][name]["bitstream_sha256"]:
                        raise ValueError("No-dither output depends on seed")
        result["variants"][variant] = dict(seeds=seed_rows, seeds_are_independent_noise_trials=shift is not None,
            summary={**summarize_windows(all_gains), "dc_plus_lsb": float(np.mean(dc_plus)), "dc_minus_lsb": float(np.mean(dc_minus))})
        save(output / "results.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=("predictive", "simple"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    exe = Path(subprocess.check_output(["node", str(ROOT / "tools/esp8266_audio_profile/build_rcpdm8_quality.js"),
        str(args.output / "build"), "rcpdm_feedback_ab"], text=True).strip())
    checks = json.loads(subprocess.check_output([str(exe), "--self-test"], text=True))
    controls, control_meta = {}, {}
    for name, suffix in (("full", "dither"), ("none", "none")):
        file = ROOT / "docs/benchmarks" / REPORTS[args.method + "-" + suffix][0] / "results.json"
        controls[name] = json.loads(file.read_text(encoding="utf-8"))
        control_meta[name] = dict(path=str(file.relative_to(ROOT)), sha256=model.original.sha(file),
            regenerated_case_count=12, regenerated_lsb_count=15)
    configs = {name: dict(method=args.method, bits=BITS, bit_rate_hz=CARRIER, shift=4, alpha=1/16,
        feedback_enabled=True, feedback_shift=0, interpolate=True, dither=0 if shift is None else 2,
        dither_shift=shift, amplitude_relative_to_original=0 if shift is None else 2**(-shift),
        triangle_multiplier=0 if shift is None else 256 >> shift) for name, shift in VARIANTS.items()}
    sources = [Path(__file__), ROOT / "esp8266/rtos-sdk-native/main/rc_pdm_feedback.h",
        ROOT / "tests/native/rcpdm_feedback_reference.h"] + [ROOT / "tools/esp8266_audio_profile" / name for name in (
        "rcpdm_feedback_ab.cpp", "measure_rcpdm_feedback_ab.py", "inspect_rcpdm_no_dither.py",
        "measure_pdm_matrix.py", "measure_rcpdm8_quality.py", "build_rcpdm8_quality.js")]
    result = dict(complete=False, measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256={str(path.relative_to(ROOT)): model.original.sha(path) for path in sources},
        self_test=checks, controls=control_meta, configs=configs, method=args.method,
        pcm_rate=RATE, common_grid_rate=model.GRID_RATE, band_hz=[20, 20000], seed=SEED,
        firmware_flashed=False, note="Offline numerical simulation, no hardware timing or analog measurement. Only dither amplitude changes; error feedback stays enabled.", cases=[])
    for number, old in enumerate(controls["full"]["cases"], 1):
        file = ROOT / old["pcm"]
        if model.original.sha(file) != old["pcm_sha256"]:
            raise ValueError("Input PCM changed: " + old["id"])
        paths, proofs = {}, {}
        for name, shift in VARIANTS.items():
            paths[name], proofs[name] = generate(exe, file, args.output / (old["id"] + "-" + name), SEED, args.method, shift)
            if name in controls:
                baseline = next(c for c in controls[name]["cases"] if c["id"] == old["id"])
                if old["pcm_sha256"] != baseline["pcm_sha256"] or model.original.sha(paths[name]) != baseline["bitstream_sha256"]["on"]:
                    raise ValueError("Archived control changed")
        pcm = np.fromfile(file, dtype="<i2")
        quality = model.analyze(pcm, paths, configs, old.get("hz"),
            lambda n: print(f"{args.method} {number}/12 {old['id']}: FFT window {n}", flush=True))
        for name, control in controls.items():
            baseline = next(c for c in control["cases"] if c["id"] == old["id"])
            assert_saved_scores(quality["models"][name], baseline["quality"]["models"]["on"])
        row = {key: old[key] for key in ("id", "type", "hz", "level_dbfs", "pcm", "pcm_sha256") if key in old}
        row.update(quality=quality, proofs=proofs, bitstream_sha256={name: model.original.sha(path) for name, path in paths.items()})
        if old["type"] == "radio":
            row["delay"] = fixed_delay(pcm, paths)
            for name in paths:
                if abs(row["delay"]["models"][name]["raw_snr_db"] - quality["models"][name]["rc10us"]["snr_to_input_db"]) > 1e-8:
                    raise ValueError("Raw/delay spectrum mismatch")
        if old["id"] in ("zero", "tone-1000hz-40db", "tone-1000hz-80db"):
            row["spurs_rc10us"] = {name: spurs(np.fromfile(path, dtype="<u4"), old.get("hz")) for name, path in paths.items()}
        result["cases"].append(row)
        save(args.output / "results.json", result)
        print(args.method, "completed", old["id"], flush=True)
    result["lsb"] = lsb_analysis(exe, args.output / "lsb", args.method, controls)
    for name, expected in result["source_sha256"].items():
        if model.original.sha(ROOT / name) != expected:
            raise ValueError("Source changed during measurement")
    result["complete"] = True
    save(args.output / "results.json", result)
    save(args.archive / "results.json", result)
    print(args.method, "complete; firmware unchanged", flush=True)


if __name__ == "__main__":
    main()
