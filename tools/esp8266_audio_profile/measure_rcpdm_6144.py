"""Same-frequency PDM128 vs predictive RC feedback, full/half TPDF.

Numerical quality only. No device access, fitted gains or fitted delays.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import numpy as np
import measure_pdm_matrix as model
from measure_rcpdm_feedback_ab import save, complex_json, assert_saved_scores
from measure_rcpdm_dither_amplitude import summarize_windows

ROOT = model.ROOT
RATE, BITS, CARRIER = 48000, 128, 6144000
SEED = 2654435769
NAMES = ("pdm128", "rc128-full", "rc128-half", "simple128-full", "simple128-half")
CONFIGS = {
    "pdm128": dict(method="pdm", bits=BITS, bit_rate_hz=CARRIER, interpolate=False, state_bytes=4, fixed_delay_seconds=0),
    **{name: dict(method="simple_feedback" if name.startswith("simple") else "predictive_feedback", bits=BITS, bit_rate_hz=CARRIER, shift=6, alpha=1/64,
        internal_rc_us=float(-1e6/(CARRIER*np.log1p(-1/64))), feedback_shift=0, feedback_enabled=True,
        dither=dither, dither_relative_to_original=scale, interpolate=True, state_bytes=16,
        fixed_delay_seconds=(BITS-1)/(2*CARRIER))
       for name, dither, scale in (("rc128-full", 2, 1), ("rc128-half", 4, .5), ("simple128-full", 2, 1), ("simple128-half", 4, .5))}}


def generate(exe, file, prefix, seed):
    proof = json.loads(subprocess.check_output([str(exe), str(file), str(prefix), str(seed)], text=True))
    if (proof["bits_per_sample"] != BITS or proof["rc_shift"] != 6 or not proof["same_prng"]
            or proof["reference_frames_per_variant"] != proof["frames"] or proof["variants"] != 5):
        raise ValueError("Wrong configuration/reference check")
    return {name: Path(str(prefix)+"."+name+".bin") for name in NAMES}, proof


def radio_delay(pcm, paths):
    n = RATE * BITS
    frequency = np.arange(20, 20001)
    window = .5 - .5*np.cos(2*np.pi*np.arange(n)/n)
    aperture = np.sinc(frequency/CARRIER)*np.exp(-1j*np.pi*frequency/CARRIER)
    rotations = {name: np.exp(-2j*np.pi*frequency*CONFIGS[name]["fixed_delay_seconds"]) for name in paths}
    filters = model.original.filters(frequency)
    words = {name: np.fromfile(path, dtype="<u4") for name, path in paths.items()}
    signal = 0.
    errors = {name: {filt: dict(raw=0., aligned=0.) for filt in filters} for name in paths}
    for start in range(RATE//4, len(pcm)-RATE//4-RATE+1, RATE):
        x = np.fft.rfft(np.repeat(pcm[start:start+RATE].astype(np.float64)/32768, BITS)*window)[20:20001]*aperture
        signal += float(np.sum(abs(x)**2))
        for name in paths:
            y0 = np.fft.rfft(model.bits_to_grid(words[name][start*4:(start+RATE)*4], BITS)*window)[20:20001]*aperture
            for filt, h in filters.items():
                y = y0*h
                errors[name][filt]["raw"] += float(np.sum(abs(y-x)**2))
                errors[name][filt]["aligned"] += float(np.sum(abs(y-x*rotations[name])**2))
    return {name: {filt: {key+"_snr_db": model.original.db_ratio(signal, value) for key, value in row.items()}
                   for filt, row in data.items()} for name, data in errors.items()}


def coherent_windows(words):
    if len(words) < 396000*4:
        raise ValueError("Need eight seconds after 250ms startup")
    phase = np.exp(-2j*np.pi*np.arange(6144)/6144)
    aperture = np.sinc(1000/CARRIER)*np.exp(-1j*np.pi*1000/CARRIER)
    transfer = aperture/(1+2j*np.pi*1000*1e-5)
    coefficients, means = [], []
    for start in range(12000, 396000, RATE):
        chunk = words[start*4:(start+RATE)*4]
        bits = ((chunk[:, None] >> np.arange(31, -1, -1, dtype=np.uint32)) & 1).astype(np.uint8).reshape(-1)
        average = bits.reshape(-1, 6144).mean(axis=0)*2-1
        coefficients.append(2*np.dot(average, phase)/6144*transfer)
        means.append(float((bits.mean()*2-1)*32768))
    return coefficients, means


def measure_lsb(exe, output):
    output.mkdir(parents=True, exist_ok=True)
    half = np.round(np.sin(2*np.pi*(np.arange(24)+.5)/48)).astype("<i2")
    period = np.r_[half, -half]
    assert period.sum() == 0 and min(period) == -1 and max(period) == 1
    signals = {"zero": np.zeros(480000, dtype="<i2"), "dc-plus": np.ones(480000, dtype="<i2"),
               "dc-minus": -np.ones(480000, dtype="<i2"), "tone-plus": np.tile(period, 10000), "tone-minus": -np.tile(period, 10000)}
    files = {}
    for name, pcm in signals.items():
        files[name] = output/(name+".s16le");pcm.tofile(files[name])
    phase = np.exp(-2j*np.pi*np.arange(6144)/6144)
    aperture = np.sinc(1000/CARRIER)*np.exp(-1j*np.pi*1000/CARRIER)
    reference = 2*np.dot(np.repeat(period.astype(np.float64)/32768, BITS), phase)/6144*aperture
    result = dict(total_seconds=10, window_seconds=1, windows_per_seed=8, trim_start_seconds=.25,
        reference=complex_json(reference), pcm_sha256={name: model.original.sha(path) for name, path in files.items()},
        seeds=[], summaries={})
    all_gains = {name: [] for name in NAMES}
    for seed in (1, 8266, SEED):
        rows = {name: {} for name in NAMES}
        for signal, file in files.items():
            paths, proof = generate(exe, file, output/f"{signal}-{seed}", seed)
            for name, path in paths.items():
                values, means = coherent_windows(np.fromfile(path, dtype="<u4"))
                rows[name][signal] = dict(bitstream_sha256=model.original.sha(path), proof=proof,
                    coherent_windows=[complex_json(v) for v in values], mean_pcm_lsb=float(np.mean(means)))
        for name in NAMES:
            gains = [(complex(**p)-complex(**m))/(2*reference) for p, m in zip(
                rows[name]["tone-plus"]["coherent_windows"], rows[name]["tone-minus"]["coherent_windows"])]
            all_gains[name].extend(gains)
            rows[name]["gains"] = [complex_json(g) for g in gains]
            rows[name]["summary"] = summarize_windows(gains)
            rows[name]["dc_plus_lsb"] = rows[name]["dc-plus"]["mean_pcm_lsb"]-rows[name]["zero"]["mean_pcm_lsb"]
            rows[name]["dc_minus_lsb"] = rows[name]["dc-minus"]["mean_pcm_lsb"]-rows[name]["zero"]["mean_pcm_lsb"]
        result["seeds"].append(dict(seed=seed, models=rows))
        print("LSB: completed seed", seed, flush=True)
    for name in NAMES:
        result["summaries"][name] = {**summarize_windows(all_gains[name]),
            "dc_plus_lsb": float(np.mean([s["models"][name]["dc_plus_lsb"] for s in result["seeds"]])),
            "dc_minus_lsb": float(np.mean([s["models"][name]["dc_minus_lsb"] for s in result["seeds"]])),
            "seeds_are_independent_noise_trials": name != "pdm128"}
    for row in result["seeds"][1:]:
        for signal in signals:
            if row["models"]["pdm128"][signal]["bitstream_sha256"] != result["seeds"][0]["models"]["pdm128"][signal]["bitstream_sha256"]:
                raise ValueError("PDM depends on dither seed")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args();args.output.mkdir(parents=True, exist_ok=True)
    exe = Path(subprocess.check_output(["node", str(ROOT/"tools/esp8266_audio_profile/build_rcpdm8_quality.js"),
        str(args.output/"build"), "rcpdm_6144_quality"], text=True).strip())
    checks = json.loads(subprocess.check_output([str(exe), "--self-test"], text=True))
    source_dir = ROOT/"tools/esp8266_audio_profile"
    sources = [Path(__file__), ROOT/"esp8266/rtos-sdk-native/main/rc_pdm_feedback.h",
        ROOT/"esp8266/rtos-sdk-native/main/native_audio_output.c", ROOT/"tests/native/rcpdm_feedback_reference.h"] + [source_dir/name for name in (
        "rcpdm_6144_quality.cpp", "build_rcpdm8_quality.js", "measure_pdm_matrix.py", "measure_rcpdm8_quality.py",
        "measure_rcpdm_feedback_ab.py", "measure_rcpdm_dither_amplitude.py", "inspect_rcpdm_no_dither.py")]
    baseline_paths = {"pdm128": ROOT/"docs/benchmarks/esp8266-pdm-frequency-matrix-2026-09-06/results.json",
                      "rc128-full": ROOT/"docs/benchmarks/esp8266-rcpdm-feedback-2026-09-06/quality.json"}
    controls = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in baseline_paths.items()}
    input_path = ROOT/"docs/benchmarks/esp8266-rcpdm-feedback-ab-2026-09-06/results.json"
    inputs = json.loads(input_path.read_text(encoding="utf-8"))
    result = dict(complete=False, measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256={str(p.relative_to(ROOT)): model.original.sha(p) for p in sources}, self_test=checks,
        baseline_reports={name: dict(path=str(path.relative_to(ROOT)), sha256=model.original.sha(path), reverified_cases=9) for name, path in baseline_paths.items()},
        input_report_sha256=model.original.sha(input_path), configs=CONFIGS, pcm_rate=RATE, bit_rate_hz=CARRIER,
        common_grid_rate=CARRIER, band_hz=[20, 20000], seed=SEED, firmware_flashed=False,
        note="Offline quality. 128 new decisions per PCM sample, not repeated bits. No hardware timing. No second-order error filter added.", cases=[])
    print("Self-test", checks, flush=True)
    for number, old in enumerate(inputs["cases"], 1):
        file = ROOT/old["pcm"]
        if model.original.sha(file) != old["pcm_sha256"]:
            raise ValueError("Input changed: "+old["id"])
        paths, proof = generate(exe, file, args.output/old["id"], SEED)
        hashes = {name: model.original.sha(path) for name, path in paths.items()}
        pcm = np.fromfile(file, dtype="<i2")
        quality = model.analyze(pcm, paths, CONFIGS, old.get("hz"),
            lambda n: print(f"{number}/12 {old['id']}: FFT window {n}", flush=True))
        for name, control in controls.items():
            baseline = next((c for c in control["cases"] if c["id"] == old["id"]), None)
            if baseline is None:
                continue
            variant = "feedback128" if name == "rc128-full" else name
            if baseline["pcm_sha256"] != old["pcm_sha256"] or hashes[name] != baseline["bitstream_sha256"][variant]:
                raise ValueError("Archived bitstream changed: "+name)
            assert_saved_scores(quality["models"][name], baseline["quality"]["models"][variant])
        row = {key: old[key] for key in ("id", "type", "hz", "level_dbfs", "pcm", "pcm_sha256") if key in old}
        row.update(quality=quality, bitstream_sha256=hashes, proof=proof)
        if old["type"] == "radio":
            row["delay"] = radio_delay(pcm, paths)
            for name in NAMES:
                for filt, metrics in row["delay"][name].items():
                    if abs(metrics["raw_snr_db"]-quality["models"][name][filt]["snr_to_input_db"]) > 1e-8:
                        raise ValueError("Delay/raw spectrum mismatch")
        result["cases"].append(row);save(args.output/"results.json", result)
        print("Completed", old["id"], flush=True)
    result["lsb"] = measure_lsb(exe, args.output/"lsb")
    for name, expected in result["source_sha256"].items():
        if model.original.sha(ROOT/name) != expected:
            raise ValueError("Source changed during measurement")
    result["complete"] = True
    save(args.output/"results.json", result);save(args.archive/"results.json", result)
    print("Complete; no hardware access", flush=True)


if __name__ == "__main__":
    main()
