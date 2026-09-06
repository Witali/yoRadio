"""Offline RCPDM8 vs ordinary PDM8/PDM32. NumPy only; no device access.

Spectrum-domain, common 1.536-MHz zero-order-hold grid. RC transfer functions
and the analysis band are identical for every modulator. Results are numerical
model estimates, not an analog recording or perceptual codec score.
"""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PCM_RATE = 48000
GRID_RATE = PCM_RATE * 32
VARIANTS = {"pdm8": 8, "pdm32": 32, "rc8-a16": 8, "rc8-a4": 8,
            "rc8-matched": 8, "rc32": 32}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def db_ratio(a, b):
    if a <= 0 or b <= 0:
        return None  # Do not serialize infinities as invalid JSON.
    return float(10 * np.log10(a / b))


def bits_to_grid(words, width):
    if width == 8:
        bits = np.unpackbits(np.asarray(words, dtype=np.uint8), bitorder="big")
        return np.repeat(bits.astype(np.float64) * 2 - 1, 4)
    bits = ((np.asarray(words, dtype=np.uint32)[:, None] >> np.arange(31, -1, -1, dtype=np.uint32)) & 1)
    return bits.reshape(-1).astype(np.float64) * 2 - 1


def filters(frequency):
    s = 2j * np.pi * frequency
    # Unbuffered passive ladder: R1=R2=1k, C1=C2=10n, high-impedance load.
    return {"rc10us": 1 / (1 + s * 1e-5),
            "rc40us": 1 / (1 + s * 4e-5),
            "ladder10us": 1 / (1 + 3 * s * 1e-5 + (s * 1e-5) ** 2)}


def analyze(pcm, paths, tone=None):
    # One-second periodic Hann windows, no overlap. Omit at least 250ms at
    # both clip edges. Mean powers use identical windows/grid for every path.
    frames = PCM_RATE
    n = frames * 32
    window = .5 - .5 * np.cos(2 * np.pi * np.arange(n) / n)
    frequency = np.fft.rfftfreq(n, 1 / GRID_RATE)
    band = (frequency >= 20) & (frequency <= 20000)
    # Analog zero-order-hold aperture of the common-grid voltage representation.
    aperture = np.sinc(frequency / GRID_RATE) * np.exp(-1j * np.pi * frequency / GRID_RATE)
    models = filters(frequency)
    power_scale = 2 / (n * np.sum(window * window))
    fundamental = abs(frequency - tone) < 1.01 if tone else None
    harmonics = np.zeros(len(frequency), dtype=bool)
    if tone:
        for k in range(2, int(20000 // tone) + 1):
            harmonics |= abs(frequency - k * tone) < 1.01
    source_words = {name: np.fromfile(path, dtype="u1" if VARIANTS[name] == 8 else "<u4") for name, path in paths.items()}
    if any(len(words) != len(pcm) for words in source_words.values()):
        raise ValueError("Packed output size mismatch")
    sums = {name: {model: dict(input=0., ideal_rc=0., output=0., error_to_input=0.,
                              error_to_ideal_rc=0., fundamental=0., input_fundamental=0., harmonics=0.)
                   for model in models} for name in paths}
    segments = 0
    for start in range(PCM_RATE // 4, len(pcm) - PCM_RATE // 4 - frames + 1, frames):
        x = np.fft.rfft(np.repeat(pcm[start:start + frames].astype(np.float64) / 32768., 32) * window) * aperture
        for name, width in VARIANTS.items():
            y0 = np.fft.rfft(bits_to_grid(source_words[name][start:start + frames], width) * window) * aperture
            for model, h in models.items():
                y, ideal = y0 * h, x * h
                metrics = sums[name][model]
                for key, spectrum in (("input", x), ("ideal_rc", ideal), ("output", y),
                                      ("error_to_input", y - x), ("error_to_ideal_rc", y - ideal)):
                    metrics[key] += float(np.sum(abs(spectrum[band]) ** 2) * power_scale)
                if tone:
                    metrics["fundamental"] += float(np.sum(abs(y[fundamental]) ** 2) * power_scale)
                    metrics["input_fundamental"] += float(np.sum(abs(x[fundamental]) ** 2) * power_scale)
                    metrics["harmonics"] += float(np.sum(abs(y[harmonics & band]) ** 2) * power_scale)
        segments += 1
    if not segments:
        raise ValueError("Need at least 1.5 seconds of PCM")
    result = {"segments": segments, "frames": len(pcm), "models": {}}
    for name, model_sums in sums.items():
        result["models"][name] = {}
        for model, m in model_sums.items():
            row = {"snr_to_input_db": db_ratio(m["input"], m["error_to_input"]),
                   "snr_to_ideal_rc_db": db_ratio(m["ideal_rc"], m["error_to_ideal_rc"]),
                   "output_rms_dbfs": db_ratio(m["output"] / segments, 1),
                   "error_to_ideal_rc_rms_dbfs": db_ratio(m["error_to_ideal_rc"] / segments, 1)}
            if tone:
                noise_distortion = max(0., m["output"] - m["fundamental"])
                # A constant alternating bitstream has no audio-band tone;
                # ratios between floating-point roundoff bins are meaningless.
                detected = m["fundamental"] / segments > 1e-18
                row.update(tone_detected=detected,
                           sinad_db=db_ratio(m["fundamental"], noise_distortion) if detected else None,
                           thd_db=db_ratio(m["harmonics"], m["fundamental"]) if detected and m["harmonics"] / segments > 1e-24 else None,
                           fundamental_gain_db=db_ratio(m["fundamental"], m["input_fundamental"]) if detected else None)
            if m["output"] / segments < 1e-24:
                row["output_rms_dbfs"] = None
                row["below_numerical_floor"] = True
            result["models"][name][model] = row
    return result


def listening_wav(words, width, file, count=96000):
    # First 2 seconds, ideal 20-kHz band limit plus the single 10-us RC pole.
    # Circular FFT boundary response is hidden by a common 10ms endpoint fade.
    values = bits_to_grid(words[:count], width)
    f = np.fft.rfftfreq(len(values), 1 / GRID_RATE)
    spectrum = np.fft.rfft(values) / (1 + 2j * np.pi * f * 1e-5)
    spectrum *= np.sinc(f / GRID_RATE) * np.exp(-1j * np.pi * f / GRID_RATE)
    spectrum[f > 20000] = 0
    out_count = len(values) // 32
    reconstructed = np.fft.irfft(spectrum[:out_count // 2 + 1] / 32, n=out_count)
    fade = np.linspace(0, 1, 480)
    reconstructed[:480] *= fade
    reconstructed[-480:] *= fade[::-1]
    # Same -3.10 dB listening gain for all files, no per-file normalization.
    reconstructed *= .7
    clipped = int(np.count_nonzero(abs(reconstructed) >= 1))
    if clipped:
        raise ValueError("Listening waveform would clip")
    with wave.open(str(file), "wb") as stream:
        stream.setnchannels(1); stream.setsampwidth(2); stream.setframerate(PCM_RATE)
        stream.writeframes(np.round(reconstructed * 32767).astype("<i2").tobytes())
    return {"sha256": sha(file), "frames": out_count, "gain": .7, "clipped": clipped}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", type=Path, default=ROOT / "radio_output/rcpdm-real-radio-20260906")
    parser.add_argument("--output", type=Path, default=ROOT / "radio_output/rcpdm8-quality")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    exe = args.output / "build" / ("rcpdm8-quality.exe" if platform.system() == "Windows" else "rcpdm8-quality")
    subprocess.run(["node", str(ROOT / "tools/esp8266_audio_profile/build_rcpdm8_quality.js"), str(exe.parent)], check=True)
    test = json.loads(subprocess.check_output([str(exe), "--self-test"], text=True))
    manifest = json.loads((args.capture / "manifest.json").read_text(encoding="utf-8"))
    cases = []
    for clip in manifest["clips"]:
        path = args.capture / "benchmark-repeat" / (clip["id"] + "-v254.mono48.s16le")
        if not path.exists():
            raise ValueError("Run the existing real-radio benchmark first")
        previous = json.loads((args.capture / "benchmark-repeat/results.json").read_text(encoding="utf-8"))
        saved = next(c for c in previous["cases"] if c["id"] == clip["id"] and c["volume"] == 254)
        if sha(path) != saved["savedOutputs"][path.name]:
            raise ValueError("Modified mono PCM")
        cases.append(dict(id=clip["id"], type="radio", pcm=path, pcm_sha256=sha(path), source=clip["url"]))
    # Deterministic tone probes, not broadcast material. 3 seconds per case.
    for hz, level in [(1000, -3), (1000, -20), (1000, -40), (7000, -3)]:
        case_id = f"tone-{hz}hz-{abs(level)}db"
        t = np.arange(PCM_RATE * 3) / PCM_RATE
        pcm = np.round(32767 * 10 ** (level / 20) * np.sin(2 * np.pi * hz * t)).astype("<i2")
        path = args.output / (case_id + ".s16le")
        pcm.tofile(path)
        cases.append(dict(id=case_id, type="tone", hz=hz, level_dbfs=level, pcm=path, pcm_sha256=sha(path)))
    source_files = ["tests/native/rcpdm8.h", "tools/esp8266_audio_profile/rcpdm8_quality.cpp",
                    "tools/esp8266_audio_profile/measure_rcpdm8_quality.py",
                    "esp8266/rtos-sdk-native/main/rc_pdm.h", "esp8266/rtos-sdk-native/main/native_audio_output.c"]
    output = dict(measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  source_sha256={name: sha(ROOT / name) for name in source_files},
                  platform=platform.platform(), numpy=np.__version__, self_test=test,
                  pcm_rate=PCM_RATE, common_grid_rate=GRID_RATE, band_hz=[20, 20000],
                  models="Single RC 10us; single RC 40us; unloaded output of unbuffered equal 1k/10n RC ladder",
                  note="Numerical spectrum-domain analog model, not a physical measurement. No automatic delay/gain alignment.",
                  cases=[])
    for case in cases:
        pcm = np.fromfile(case["pcm"], dtype="<i2")
        prefix = args.output / case["id"]
        packed = json.loads(subprocess.check_output([str(exe), str(case["pcm"]), str(prefix)], text=True))
        paths = {name: Path(str(prefix) + "." + name + ".bin") for name in VARIANTS}
        row = {k: str(v) if isinstance(v, Path) else v for k, v in case.items()}
        row.update(packed=packed, bitstream_sha256={name: sha(path) for name, path in paths.items()})
        row["quality"] = analyze(pcm, paths, case.get("hz"))
        row["listening"] = {}
        row["constant_alternating_only"] = {}
        for name, width in VARIANTS.items():
            words = np.fromfile(paths[name], dtype="u1" if width == 8 else "<u4")
            idle = (0xaa, 0x55) if width == 8 else (0xaaaaaaaa, 0x55555555)
            row["constant_alternating_only"][name] = bool(words[0] in idle and np.all(words == words[0]))
            row["listening"][name] = listening_wav(words, width, Path(str(prefix) + "." + name + ".wav"))
        output["cases"].append(row)
        (args.output / "results.json").write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        field = "sinad_db" if case["type"] == "tone" else "snr_to_ideal_rc_db"
        print(case["id"], field, {name: None if row["quality"]["models"][name]["rc10us"][field] is None else round(row["quality"]["models"][name]["rc10us"][field], 2) for name in VARIANTS}, flush=True)


if __name__ == "__main__":
    main()
