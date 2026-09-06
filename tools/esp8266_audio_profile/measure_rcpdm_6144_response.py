"""Tone sweep: amplitude/phase/group delay and 10/20-kHz quality at 6.144 MHz.

All results are numerical simulations. No physical board or network access.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import numpy as np
import measure_pdm_matrix as model
import measure_rcpdm_6144 as comparison
from measure_rcpdm_feedback_ab import save, complex_json, assert_saved_scores

ROOT = model.ROOT
RATE, BITS, CARRIER = 48000, 128, 6144000
FREQUENCIES = (20, 30, 50, 80, 100, 150, 200, 300, 500, 700, 1000, 1500,
               2000, 3000, 5000, 7000, 10000, 12000, 15000, 18000, 20000)


def measure_transfer(pcm, paths, tone):
    if not isinstance(tone, int) or not 20 <= tone <= 20000:
        raise ValueError("Expected an integer audio frequency in 20..20000 Hz")
    n=RATE*BITS
    window=.5-.5*np.cos(2*np.pi*np.arange(n)/n)
    frequency=np.arange(tone-1, tone+2)
    aperture=np.sinc(frequency/CARRIER)*np.exp(-1j*np.pi*frequency/CARRIER)
    filters=model.original.filters(frequency)
    words={name: np.fromfile(path, dtype="<u4") for name, path in paths.items()}
    if any(len(data) != len(pcm)*4 for data in words.values()):
        raise ValueError("Packed output size mismatch")
    cross={name: {filt: [] for filt in filters} for name in paths}
    powers=[]
    for start in range(RATE//4, len(pcm)-RATE//4-RATE+1, RATE):
        x=np.fft.rfft(np.repeat(pcm[start:start+RATE].astype(np.float64)/32768, BITS)*window)[tone-1:tone+2]*aperture
        power=float(np.sum(abs(x)**2));powers.append(power)
        for name in paths:
            bits=model.bits_to_grid(words[name][start*4:(start+RATE)*4], BITS)
            y=np.fft.rfft(bits*window)[tone-1:tone+2]*aperture
            for filt, h in filters.items():
                cross[name][filt].append(complex(np.sum(y*h*np.conj(x))))
    if not powers or min(powers)<=0:
        raise ValueError("No coherent input tone")
    result={}
    for name, values in cross.items():
        result[name]={}
        for filt, products in values.items():
            h=sum(products)/sum(powers)
            windows=[product/power for product, power in zip(products, powers)]
            result[name][filt]=dict(transfer=complex_json(h), gain_db=float(20*np.log10(abs(h))),
                phase_degrees=float(np.angle(h, deg=True)),
                window_transfers=[complex_json(value) for value in windows])
    return result


def curve(frequencies, transfers, known_delay):
    frequencies=np.asarray(frequencies, dtype=float)
    if (len(frequencies)<3 or len(transfers)!=len(frequencies)
            or not np.all(np.diff(frequencies)>0) or not np.all(np.isfinite(transfers))
            or np.any(np.abs(transfers)==0)):
        raise ValueError("Need at least three ordered frequencies and nonzero finite transfers")
    phase=np.unwrap(np.angle(np.asarray(transfers, dtype=complex)))
    group=-np.gradient(phase, 2*np.pi*frequencies, edge_order=2)
    return dict(frequencies_hz=frequencies.astype(int).tolist(),
        gain_db=(20*np.log10(abs(np.asarray(transfers)))).tolist(),
        raw_phase_degrees=np.rad2deg(phase).tolist(),
        interpolation_compensated_phase_degrees=np.rad2deg(phase+2*np.pi*frequencies*known_delay).tolist(),
        group_delay_us=(group*1e6).tolist(),
        interpolation_compensated_group_delay_us=((group-known_delay)*1e6).tolist())


def plot_curves(result, file):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes=plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    styles=(("pdm128", "PDM128", "#d97706", "-"),
            ("rc128-half", "RC-PDM, половинный dither", "#2563eb", "-"),
            ("simple128-half", "Simple, половинный dither", "#15803d", "--"))
    for name, label, color, style in styles:
        data=result["curves"][name]["rc10us"]
        for ax, key in zip(axes, ("gain_db", "raw_phase_degrees", "group_delay_us")):
            ax.semilogx(data["frequencies_hz"], data[key], style, color=color, label=label, linewidth=2)
    for ax in axes:
        ax.grid(True, which="both", alpha=.25)
        ax.set_xlim(20, 20000)
    axes[0].set_ylabel("Основная гармоника, дБ")
    axes[1].set_ylabel("Фаза относительно PCM, °")
    axes[2].set_ylabel("Групповая задержка, мкс")
    axes[2].set_xlabel("Частота аудиотона, Гц (логарифмическая шкала)")
    ticks=[20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    axes[2].set_xticks(ticks, [str(value) for value in ticks])
    axes[0].legend(loc="lower left", fontsize=9)
    fig.suptitle("6,144 МГц • RC 10 мкс • PCM 48 кГц, −3 dBFS\nСимуляция; фаза и задержка без компенсации интерполяции", fontsize=14)
    fig.text(.5, .013, "Групповая задержка — численная производная по 21 точке. Это не измерение платы.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .035, 1, .94))
    fig.savefig(file, dpi=160)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args=parser.parse_args();args.output.mkdir(parents=True, exist_ok=True)
    # Fail before the long simulation when the optional plot dependency is absent.
    import matplotlib
    exe=Path(subprocess.check_output(["node", str(ROOT/"tools/esp8266_audio_profile/build_rcpdm8_quality.js"),
        str(args.output/"build"), "rcpdm_6144_quality"], text=True).strip())
    checks=json.loads(subprocess.check_output([str(exe), "--self-test"], text=True))
    baseline_path=ROOT/"docs/benchmarks/esp8266-rcpdm-6144-2026-09-06/results.json"
    baseline=json.loads(baseline_path.read_text(encoding="utf-8"))
    dependencies=[Path(__file__), ROOT/"esp8266/rtos-sdk-native/main/rc_pdm_feedback.h",
        ROOT/"esp8266/rtos-sdk-native/main/native_audio_output.c", ROOT/"tests/native/rcpdm_feedback_reference.h"]
    dependencies += [ROOT/"tools/esp8266_audio_profile"/name for name in (
        "measure_rcpdm_6144.py", "rcpdm_6144_quality.cpp", "build_rcpdm8_quality.js", "measure_pdm_matrix.py",
        "measure_rcpdm8_quality.py", "measure_rcpdm_feedback_ab.py", "measure_rcpdm_dither_amplitude.py", "inspect_rcpdm_no_dither.py")]
    result=dict(complete=False, measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256={str(p.relative_to(ROOT)): model.original.sha(p) for p in dependencies},
        baseline_path=str(baseline_path.relative_to(ROOT)), baseline_sha256=model.original.sha(baseline_path),
        controls_hz=[1000, 7000], self_test=checks, configs=comparison.CONFIGS,
        pcm_rate=RATE, bit_rate_hz=CARRIER, tone_level_dbfs=-3, seed=comparison.SEED,
        audio_band_hz=[20, 20000], quality_integration_band_hz=[20, 20001],
        guard_note="One extra 1-Hz bin includes the upper Hann lobe of a 20-kHz tone or harmonic; used for ALL new rows.",
        phase_reference="Input PCM held for 128 bits, same ZOH aperture; coherent cross-spectrum over all three fundamental bins.",
        group_delay_method="Negative derivative of unwrapped phase by nonuniform three-point finite differences; edge estimates are one-sided.",
        firmware_flashed=False, numpy_version=np.__version__, matplotlib_version=matplotlib.__version__, cases=[])
    for index, hz in enumerate(FREQUENCIES, 1):
        old=next((c for c in baseline["cases"] if c.get("hz")==hz and c.get("level_dbfs")==-3), None)
        # All inputs are synthetic. Regenerate archived controls as well, but
        # require their exact historical hashes; no private radio files needed.
        file=args.output/f"tone-{hz}hz-3db.s16le"
        pcm=np.round(32767*10**(-3/20)*np.sin(2*np.pi*hz*np.arange(RATE*3)/RATE)).astype("<i2")
        pcm.tofile(file)
        if old and model.original.sha(file)!=old["pcm_sha256"]:
            raise ValueError("Generated control differs from archived input")
        pcm=np.fromfile(file, dtype="<i2")
        paths, proof=comparison.generate(exe, file, args.output/f"tone-{hz}hz-3db", comparison.SEED)
        hashes={name: model.original.sha(path) for name, path in paths.items()}
        row=dict(hz=hz, pcm=str(file.resolve()), pcm_sha256=model.original.sha(file), bitstream_sha256=hashes, proof=proof)
        if old:
            if hashes!=old["bitstream_sha256"]:
                raise ValueError("Control bitstream changed")
            historical=model.analyze(pcm, paths, comparison.CONFIGS, hz)
            for name in paths:
                assert_saved_scores(historical["models"][name], old["quality"]["models"][name])
            row["historical_control_reverified"]=True
        row["quality"]=model.analyze(pcm, paths, comparison.CONFIGS, hz, band_high_hz=20001)
        row["response"]=measure_transfer(pcm, paths, hz)
        result["cases"].append(row);save(args.output/"results.json", result)
        print(f"{index}/{len(FREQUENCIES)} {hz} Hz: quality and phase complete", flush=True)
    result["curves"]={name: {filt: curve(FREQUENCIES,
        [complex(**row["response"][name][filt]["transfer"]) for row in result["cases"]], cfg["fixed_delay_seconds"])
        for filt in ("rc10us", "rc40us", "ladder10us")} for name, cfg in comparison.CONFIGS.items()}
    for name, expected in result["source_sha256"].items():
        if model.original.sha(ROOT/name)!=expected:
            raise ValueError("Source changed during measurement")
    args.archive.mkdir(parents=True, exist_ok=True)
    plot_curves(result, args.archive/"response-rc10us.png")
    result["complete"]=True
    save(args.output/"results.json", result);save(args.archive/"results.json", result)
    print("Completed 21-point sweep; no hardware access", flush=True)


if __name__=="__main__":
    main()
