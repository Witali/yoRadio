"""Controlled feedback/dither on/off simulation. No device or firmware changes.

Both paths retain interpolation, RC alpha, dither amplitude and the exact PRNG
sequence. The on path must reproduce archived production bitstreams/scores.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import measure_pdm_matrix as model

ROOT = model.ROOT
SEED = 2654435769
RATE = 48000
BITS = 32
CARRIER = RATE * BITS
MODES = ("on", "off")


def save(path, result):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def generate(exe, pcm, prefix, seed, method="predictive", dither=2):
    command = [str(exe), str(pcm), str(prefix), str(seed)] + (["simple"] if method == "simple" else [])
    if dither == 0:
        command.append("no-dither")
    proof = json.loads(subprocess.check_output(command, text=True))
    if proof["method"] != method:
        raise ValueError("Wrong decision rule")
    if proof["dither"] != dither:
        raise ValueError("Wrong dither mode")
    if not proof["prng_and_interpolation_identical"] or proof["on_reference_frames"] != proof["frames"]:
        raise ValueError("Ablation or production-reference check failed")
    return {mode: Path(str(prefix) + "." + mode + ".bin") for mode in MODES}, proof


def fixed_delay_radio(pcm, paths):
    # Same fixed interpolation delay for both modes, never an optimized fit.
    n = RATE * model.GRID_BITS
    frequency = np.arange(20, 20001)
    window = .5 - .5 * np.cos(2 * np.pi * np.arange(n) / n)
    aperture = np.sinc(frequency / model.GRID_RATE) * np.exp(-1j * np.pi * frequency / model.GRID_RATE)
    delay = (BITS - 1) / (2 * CARRIER)
    rotation = np.exp(-2j * np.pi * frequency * delay)
    h = model.original.filters(frequency)["rc10us"]
    words = {name: np.fromfile(file, dtype="<u4") for name, file in paths.items()}
    signal = 0.
    errors = {mode: dict(raw=0., aligned=0.) for mode in MODES}
    for start in range(RATE // 4, len(pcm) - RATE // 4 - RATE + 1, RATE):
        x = np.fft.rfft(np.repeat(pcm[start:start + RATE].astype(np.float64) / 32768, model.GRID_BITS) * window)[20:20001] * aperture
        signal += float(np.sum(abs(x) ** 2))
        for mode in MODES:
            y = np.fft.rfft(model.bits_to_grid(words[mode][start:start + RATE], BITS) * window)[20:20001] * aperture * h
            errors[mode]["raw"] += float(np.sum(abs(y - x) ** 2))
            errors[mode]["aligned"] += float(np.sum(abs(y - x * rotation) ** 2))
    return dict(fixed_delay_seconds=delay, models={
        mode: {key + "_snr_db": model.original.db_ratio(signal, value) for key, value in row.items()}
        for mode, row in errors.items()})


def assert_saved_scores(got, expected):
    for filt, metrics in expected.items():
        for key, value in metrics.items():
            current = got[filt][key]
            if value is None or isinstance(value, bool):
                if current != value:
                    raise ValueError("Archived baseline detection changed")
            elif abs(current - value) > 1e-8:
                raise ValueError(f"Archived baseline score changed: {filt}/{key}")


def complex_json(value):
    return dict(real=float(value.real), imag=float(value.imag))


def lsb_analysis(exe, output, method, dither, dither_control=None):
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
    phase = np.exp(-2j * np.pi * np.arange(1536) / 1536)
    aperture = np.sinc(1000 / CARRIER) * np.exp(-1j * np.pi * 1000 / CARRIER)
    transfer = aperture / (1 + 2j * np.pi * 1000 * 1e-5)
    reference = 2 * np.dot(np.repeat(period.astype(np.float64) / 32768, 32), phase) / 1536 * aperture
    archived = json.loads((ROOT / "docs/benchmarks/esp8266-rcpdm-feedback-2026-09-06/lsb.json").read_text(encoding="utf-8"))
    result = dict(window_seconds=8, total_seconds=10, trim_start_seconds=.25,
                  dither=dither, seeds_are_independent_noise_trials=dither != 0,
                  reference=complex_json(reference), seeds=[], summaries={},
                  pcm_sha256={name: model.original.sha(file) for name, file in files.items()})
    coherent = {mode: {name: [] for name in signals} for mode in MODES}
    means = {mode: {name: [] for name in signals} for mode in MODES}
    for seed in (1, 8266, SEED):
        rows = {mode: {} for mode in MODES}
        old = next(row for row in archived["seeds"] if row["seed"] == seed)
        for name, file in files.items():
            paths, proof = generate(exe, file, output / f"{name}-{seed}", seed, method, dither)
            if dither_control is not None:
                controls, _ = generate(exe, file, output / f"{name}-{seed}-control", seed, method, 2)
                baseline = next(row for row in dither_control["lsb"]["seeds"] if row["seed"] == seed)
                for mode, path in controls.items():
                    if model.original.sha(path) != baseline["models"][mode][name]["bitstream_sha256"]:
                        raise ValueError("Dither-on LSB control changed")
            if dither == 2 and method == "predictive" and model.original.sha(paths["on"]) != old["measurements"][name]["bitstream_sha256"]:
                raise ValueError("Archived enabled LSB bits changed")
            for mode, path in paths.items():
                words = np.fromfile(path, dtype="<u4")[12000:396000]
                bits = ((words[:, None] >> np.arange(31, -1, -1, dtype=np.uint32)) & 1).astype(np.uint8).reshape(-1)
                average = bits.reshape(-1, 1536).mean(axis=0) * 2 - 1
                coefficient = 2 * np.dot(average, phase) / 1536 * transfer
                mean = float((bits.mean() * 2 - 1) * 32768)
                coherent[mode][name].append(coefficient)
                means[mode][name].append(mean)
                rows[mode][name] = dict(coherent=complex_json(coefficient), mean_pcm_lsb=mean,
                    bitstream_sha256=model.original.sha(path), analysis_sha256=hashlib.sha256(words.tobytes()).hexdigest(),
                    constant_alternating_only=bool(words[0] in (0xaaaaaaaa, 0x55555555) and np.all(words == words[0])))
        for mode in MODES:
            gain = (coherent[mode]["tone-plus"][-1] - coherent[mode]["tone-minus"][-1]) / (2 * reference)
            rows[mode]["differential_gain"] = complex_json(gain)
        result["seeds"].append(dict(seed=seed, models=rows))
        print(f"LSB seed {seed}: on/off complete", flush=True)
    for mode in MODES:
        averages = {name: complex(np.mean(values)) for name, values in coherent[mode].items()}
        gain = (averages["tone-plus"] - averages["tone-minus"]) / (2 * reference)
        result["summaries"][mode] = dict(gain_magnitude=float(abs(gain)),
            gain_phase_degrees=float(np.angle(gain, deg=True)),
            zero_coherent_noise_relative_tone=float(abs(averages["zero"] / reference)),
            dc_plus_lsb=float(np.mean(means[mode]["dc-plus"]) - np.mean(means[mode]["zero"])),
            dc_minus_lsb=float(np.mean(means[mode]["dc-minus"]) - np.mean(means[mode]["zero"])))
    if dither == 0:
        for seed_row in result["seeds"][1:]:
            for mode in MODES:
                for name in signals:
                    if seed_row["models"][mode][name]["bitstream_sha256"] != result["seeds"][0]["models"][mode][name]["bitstream_sha256"]:
                        raise ValueError("No-dither output depends on seed")
        result["seed_independence_verified"] = True
    if dither == 2 and method == "predictive":
        for key, value in result["summaries"]["on"].items():
            if abs(value - archived["checks"][key]) > 1e-8:
                raise ValueError("Enabled LSB metrics changed")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--method", choices=("predictive", "simple"), default="predictive")
    parser.add_argument("--dither", type=int, choices=(0, 2), default=2, help="0: none; 2: original half-step TPDF")
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    if args.output is None:
        suffix = "-no-dither" if args.dither == 0 else ""
        args.output = ROOT / f"radio_output/rcpdm-{args.method}-feedback-ab{suffix}-20260906"
    args.output.mkdir(parents=True, exist_ok=True)
    exe = Path(subprocess.check_output(["node", str(ROOT / "tools/esp8266_audio_profile/build_rcpdm8_quality.js"),
        str(args.output / "build"), "rcpdm_feedback_ab"], text=True).strip())
    self_test = json.loads(subprocess.check_output([str(exe), "--self-test"], text=True))
    baseline = ROOT / "docs/benchmarks/esp8266-rcpdm-feedback-2026-09-06/quality.json"
    saved = json.loads(baseline.read_text(encoding="utf-8"))
    dither_control = None
    if args.dither == 0:
        control_name = "esp8266-rcpdm-feedback-ab-2026-09-06" if args.method == "predictive" else "esp8266-rcpdm-simple-feedback-ab-2026-09-06"
        control_path = ROOT / "docs/benchmarks" / control_name / "results.json"
        dither_control = json.loads(control_path.read_text(encoding="utf-8"))
    configs = {mode: dict(bits=32, bit_rate_hz=CARRIER, shift=4, alpha=1/16,
        dither=args.dither, interpolate=True, method=args.method, feedback_enabled=mode == "on") for mode in MODES}
    sources = ["esp8266/rtos-sdk-native/main/rc_pdm_feedback.h", "tests/native/rcpdm_feedback_reference.h",
        "tools/esp8266_audio_profile/rcpdm_feedback_ab.cpp", "tools/esp8266_audio_profile/measure_rcpdm_feedback_ab.py",
        "tools/esp8266_audio_profile/measure_pdm_matrix.py", "tools/esp8266_audio_profile/measure_rcpdm8_quality.py",
        "tools/esp8266_audio_profile/build_rcpdm8_quality.js"]
    result = dict(measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256={name: model.original.sha(ROOT / name) for name in sources},
        baseline_sha256=model.original.sha(baseline), self_test=self_test, configs=configs,
        method=args.method, dither=args.dither, pcm_rate=RATE, common_grid_rate=model.GRID_RATE, band_hz=[20, 20000], seed=SEED,
        firmware_flashed=False, note="Offline numerical model only; no hardware timing or analog measurement. Feedback on/off at a fixed dither setting, with archived dither-on controls for no-dither runs.",
        cases=[])
    if dither_control is not None:
        result["dither_control"] = dict(path=str(control_path.relative_to(ROOT)), sha256=model.original.sha(control_path),
            bitstreams_reverified=True, case_count=len(dither_control["cases"]), lsb_pairs=15)
    cases = list(saved["cases"])
    for level in (-60, -80):
        file = args.output / f"tone-1000hz-{abs(level)}db.s16le"
        pcm = np.round(32767 * 10 ** (level / 20) * np.sin(2 * np.pi * 1000 * np.arange(RATE * 3) / RATE)).astype("<i2")
        pcm.tofile(file)
        cases.append(dict(id=file.stem, type="tone", hz=1000, level_dbfs=level,
                          pcm=str(file.resolve()), pcm_sha256=model.original.sha(file)))
    file = args.output / "zero.s16le"
    np.zeros(RATE * 3, dtype="<i2").tofile(file)
    cases.append(dict(id="zero", type="silence", pcm=str(file.resolve()), pcm_sha256=model.original.sha(file)))
    for number, old in enumerate(cases, 1):
        file = ROOT / old["pcm"]
        if model.original.sha(file) != old["pcm_sha256"]:
            raise ValueError("Input PCM changed: " + old["id"])
        print(f"{number}/{len(cases)} {old['id']}: generating same-seed pair", flush=True)
        paths, proof = generate(exe, file, args.output / old["id"], SEED, args.method, args.dither)
        if dither_control is not None:
            control_row = next(row for row in dither_control["cases"] if row["id"] == old["id"])
            if control_row["pcm_sha256"] != old["pcm_sha256"]:
                raise ValueError("Dither-on input differs")
            controls, _ = generate(exe, file, args.output / (old["id"] + "-control"), SEED, args.method, 2)
            for mode, path in controls.items():
                if model.original.sha(path) != control_row["bitstream_sha256"][mode]:
                    raise ValueError("Dither-on control bits changed")
        hashes = {mode: model.original.sha(path) for mode, path in paths.items()}
        if args.dither == 2 and args.method == "predictive" and "bitstream_sha256" in old and hashes["on"] != old["bitstream_sha256"]["feedback32"]:
            raise ValueError("Archived enabled bits changed")
        pcm = np.fromfile(file, dtype="<i2")
        quality = model.analyze(pcm, paths, configs, old.get("hz"),
            lambda n: print(f"{number}/{len(cases)} {old['id']}: FFT window {n}", flush=True))
        if args.dither == 2 and args.method == "predictive" and "quality" in old:
            assert_saved_scores(quality["models"]["on"], old["quality"]["models"]["feedback32"])
        row = {key: old[key] for key in ("id", "type", "hz", "level_dbfs", "pcm", "pcm_sha256") if key in old}
        row.update(quality=quality, bitstream_sha256=hashes, proof=proof)
        row["activity"] = {}
        for mode, path in paths.items():
            words = np.fromfile(path, dtype="<u4")[RATE // 4:-RATE // 4]
            constant = bool(np.all(words == words[0]))
            row["activity"][mode] = dict(constant_word=hex(int(words[0])) if constant else None,
                constant_alternating_only=bool(constant and words[0] in (0xaaaaaaaa, 0x55555555)))
        if old["type"] == "radio":
            row["delay"] = fixed_delay_radio(pcm, paths)
            for mode in MODES:
                if abs(row["delay"]["models"][mode]["raw_snr_db"] - quality["models"][mode]["rc10us"]["snr_to_input_db"]) > 1e-8:
                    raise ValueError("Raw/delay spectrum mismatch")
        result["cases"].append(row)
        save(args.output / "results.json", result)
        print("Completed", old["id"], flush=True)
    result["lsb"] = lsb_analysis(exe, args.output / "lsb", args.method, args.dither, dither_control)
    for name, expected in result["source_sha256"].items():
        if model.original.sha(ROOT / name) != expected:
            raise ValueError("Source changed during measurement")
    result["complete"] = True
    save(args.output / "results.json", result)
    if args.archive:
        save(args.archive / "results.json", result)
    print("Simulation complete; firmware untouched", flush=True)


if __name__ == "__main__":
    main()
