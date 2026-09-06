"""Inspect spurs and time-varying weak-tone transfer in saved dither A/B bits.

No new modulation, hardware access, fitted gains or fitted delays. Reads the
hashed bitstreams made by measure_rcpdm_feedback_ab.py.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import measure_pdm_matrix as model

ROOT = model.ROOT
REPORTS = {
    "predictive-dither": ("esp8266-rcpdm-feedback-ab-2026-09-06", "rcpdm-feedback-ab-20260906"),
    "simple-dither": ("esp8266-rcpdm-simple-feedback-ab-2026-09-06", "rcpdm-simple-feedback-ab-20260906"),
    "predictive-none": ("esp8266-rcpdm-no-dither-2026-09-06/predictive", "rcpdm-predictive-no-dither-20260906"),
    "simple-none": ("esp8266-rcpdm-no-dither-2026-09-06/simple", "rcpdm-simple-no-dither-20260906"),
}


def read_words(path, expected):
    if model.original.sha(path) != expected:
        raise ValueError("Modified bitstream: " + str(path))
    return np.fromfile(path, dtype="<u4")


def spurs(words, tone):
    frequency = np.arange(20, 20001)
    n = 48000 * model.GRID_BITS
    window = .5 - .5 * np.cos(2 * np.pi * np.arange(n) / n)
    h = model.original.filters(frequency)["rc10us"]
    aperture = np.sinc(frequency / model.GRID_RATE) * np.exp(-1j * np.pi * frequency / model.GRID_RATE)
    total = np.zeros(frequency.size)
    count = 0
    for start in range(12000, len(words) - 12000 - 48000 + 1, 48000):
        y = np.fft.rfft(model.bits_to_grid(words[start:start + 48000], 32) * window)[20:20001] * h * aperture
        total += abs(y) ** 2 * (2 / (n * np.sum(window * window)))
        count += 1
    power = total / count
    eligible = np.ones(len(power), dtype=bool)
    if tone:
        eligible &= abs(frequency - tone) > 2
    peaks = []
    # Three-bin Hann-lobe power, useful for identifying tones, not a second
    # SINAD calculation. Do not label FFT roundoff as a physical spur.
    for _ in range(3):
        pos = int(np.argmax(np.where(eligible, power, -1)))
        value = float(power[max(0, pos - 1):pos + 2].sum())
        if value < 1e-24:
            break
        peaks.append(dict(hz=int(frequency[pos]), rms_dbfs=model.original.db_ratio(value, 1)))
        eligible[max(0, pos - 2):pos + 3] = False
    return dict(window_seconds=1, windows=count, strongest_nonfundamental_bins=peaks)


def lsb_windows(positive, negative, reference):
    phase = np.exp(-2j * np.pi * np.arange(1536) / 1536)
    aperture = np.sinc(1000 / 1536000) * np.exp(-1j * np.pi * 1000 / 1536000)
    h = aperture / (1 + 2j * np.pi * 1000 * 1e-5)
    gains = []
    for start in range(12000, 396000, 48000):
        coefficients = []
        for words in (positive, negative):
            bits = ((words[start:start + 48000, None] >> np.arange(31, -1, -1, dtype=np.uint32)) & 1).astype(np.uint8).reshape(-1)
            voltage = bits.reshape(-1, 1536).mean(axis=0) * 2 - 1
            coefficients.append(2 * np.dot(voltage, phase) / 1536 * h)
        gains.append((coefficients[0] - coefficients[1]) / (2 * reference))
    return gains


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = [Path(__file__), ROOT / "tools/esp8266_audio_profile/measure_pdm_matrix.py",
               ROOT / "tools/esp8266_audio_profile/measure_rcpdm8_quality.py"]
    result = dict(note="Offline RC10us, same saved bits. Peak bins exclude the intended fundamental; no perceptual claim.",
        source_sha256={str(path.relative_to(ROOT)): model.original.sha(path) for path in sources}, variants={})
    for name, (report_dir, capture_dir) in REPORTS.items():
        path = ROOT / "docs/benchmarks" / report_dir / "results.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        capture = ROOT / "radio_output" / capture_dir
        row = dict(report_sha256=model.original.sha(path), models={})
        for mode in ("on", "off"):
            values = dict(spectra={}, lsb={})
            for case_id in ("zero", "tone-1000hz-40db", "tone-1000hz-80db"):
                case = next(case for case in report["cases"] if case["id"] == case_id)
                words = read_words(capture / f"{case_id}.{mode}.bin", case["bitstream_sha256"][mode])
                values["spectra"][case_id] = spurs(words, case.get("hz"))
            seed = 2654435769
            reference = complex(**report["lsb"]["reference"])
            measurements = next(s for s in report["lsb"]["seeds"] if s["seed"] == seed)["models"][mode]
            positive, negative = [read_words(capture / "lsb" / f"tone-{polarity}-{seed}.{mode}.bin",
                                            measurements[f"tone-{polarity}"]["bitstream_sha256"])
                                  for polarity in ("plus", "minus")]
            gains = lsb_windows(positive, negative, reference)
            expected = complex(**measurements["differential_gain"])
            if abs(np.mean(gains) - expected) > 1e-10:
                raise ValueError("One-second windows do not reproduce archived coherent gain")
            values["lsb"] = dict(seed=seed, start_seconds=.25, window_seconds=1,
                gains=[dict(magnitude=float(abs(g)), phase_degrees=float(np.angle(g, deg=True))) for g in gains],
                coherent_mean_magnitude=float(abs(np.mean(gains))))
            row["models"][mode] = values
            print(name, mode, "LSB windows", [round(abs(g), 4) for g in gains], flush=True)
        result["variants"][name] = row
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
