"""Same-carrier legacy RC (no dither/feedback/interpolation) vs five newer paths.

Offline only. Reuses the actual legacy matrix and modern capture executables;
does not replace a production modulator or change a board profile.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import numpy as np
import measure_pdm_matrix as model
import measure_rcpdm_6144 as modern
import measure_rcpdm_6144_response as response
from measure_rcpdm_feedback_ab import save, complex_json, assert_saved_scores
from measure_rcpdm_dither_amplitude import summarize_windows

ROOT=model.ROOT
LEGACY={"rc128-legacy": "rc128-a64", "simple128-legacy": "simple128-a64"}
CONFIGS={**modern.CONFIGS, **{name: dict(method="predictive_legacy" if name.startswith("rc") else "simple_legacy",
    bits=128, bit_rate_hz=6144000, shift=6, alpha=1/64,
    internal_rc_us=modern.CONFIGS["rc128-half"]["internal_rc_us"], state_bytes=4,
    dither=0, feedback_enabled=False, interpolate=False, fixed_delay_seconds=0,
    state_scale="unsigned 32-bit; full rail UINT32_MAX; PCM target (pcm+32768)<<16") for name in LEGACY}}
FILTERS=("rc10us", "rc40us", "ladder10us")


def legacy_capture(exe, file, prefix):
    proof=json.loads(subprocess.check_output([str(exe), str(file), str(prefix), "--matched-6144"], text=True))
    if (proof["variants"]!=3 or proof["bits_per_sample"]!=128 or proof["rc_shift"]!=6
            or proof["reference_word_state_checks"]!=proof["samples"]*3*4):
        raise ValueError("Legacy capture parameters/reference check failed")
    paths={name: Path(str(prefix)+"."+old+".bin") for name, old in LEGACY.items()}
    paths["pdm128"]=Path(str(prefix)+".pdm128.bin")
    return paths, proof


def build(output, stem):
    return Path(subprocess.check_output(["node", str(ROOT/"tools/esp8266_audio_profile/build_rcpdm8_quality.js"),
        str(output/stem), stem], text=True).strip())


def legacy_lsb(exe, output, baseline):
    output.mkdir(parents=True, exist_ok=True)
    half=np.round(np.sin(2*np.pi*(np.arange(24)+.5)/48)).astype("<i2")
    period=np.r_[half, -half]
    signals={"zero": np.zeros(480000, dtype="<i2"), "dc-plus": np.ones(480000, dtype="<i2"),
        "dc-minus": -np.ones(480000, dtype="<i2"), "tone-plus": np.tile(period, 10000), "tone-minus": -np.tile(period, 10000)}
    rows={name: {} for name in (*LEGACY, "pdm128")}
    old=baseline["lsb"]["seeds"][0]["models"]["pdm128"]
    for signal, pcm in signals.items():
        file=output/(signal+".s16le");pcm.tofile(file)
        if model.original.sha(file)!=baseline["lsb"]["pcm_sha256"][signal]:
            raise ValueError("LSB input differs from archive")
        paths, proof=legacy_capture(exe, file, output/signal)
        for name, path in paths.items():
            values, means=modern.coherent_windows(np.fromfile(path, dtype="<u4"))
            rows[name][signal]=dict(bitstream_sha256=model.original.sha(path), proof=proof,
                coherent_windows=[complex_json(v) for v in values], mean_pcm_lsb=float(np.mean(means)))
        if rows["pdm128"][signal]["bitstream_sha256"]!=old[signal]["bitstream_sha256"]:
            raise ValueError("LSB PDM control changed")
        print("LSB", signal, "complete", flush=True)
    reference=complex(**baseline["lsb"]["reference"])
    for name, row in rows.items():
        gains=[(complex(**p)-complex(**m))/(2*reference) for p, m in zip(
            row["tone-plus"]["coherent_windows"], row["tone-minus"]["coherent_windows"])]
        row["summary"]={**summarize_windows(gains),
            "dc_plus_lsb": row["dc-plus"]["mean_pcm_lsb"]-row["zero"]["mean_pcm_lsb"],
            "dc_minus_lsb": row["dc-minus"]["mean_pcm_lsb"]-row["zero"]["mean_pcm_lsb"],
            "seeds_are_independent_noise_trials": False}
        row["gains"]=[complex_json(v) for v in gains]
    return dict(window_seconds=1, windows=8, seed_independent=True, models=rows,
        modern_summaries=baseline["lsb"]["summaries"],
        note="Modern three-seed summaries copied from the linked archive; legacy and PDM are deterministic, measured once.")


def plot(result, file):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    styles=(("pdm128", "PDM128", "#d97706", "-"),
        ("rc128-legacy", "RC-PDM исходный", "#9333ea", "-"),
        ("simple128-legacy", "Simple исходный", "#dc2626", "--"),
        ("rc128-full", "RC feedback, full dither", "#60a5fa", ":"),
        ("rc128-half", "RC feedback, half dither", "#1d4ed8", "-"),
        ("simple128-full", "Simple feedback, full dither", "#86b58b", ":"),
        ("simple128-half", "Simple feedback, half dither", "#15803d", "--"))
    fig, axes=plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    for name, label, color, style in styles:
        data=result["curves"][name]["rc10us"]
        for ax, key in zip(axes, ("gain_db", "raw_phase_degrees", "group_delay_us")):
            ax.semilogx(data["frequencies_hz"], data[key], style, color=color, label=label, linewidth=1.8)
    for ax in axes:
        ax.grid(True, which="both", alpha=.25);ax.set_xlim(20, 20000)
    for ax, label in zip(axes, ("Основная гармоника, дБ", "Фаза относительно PCM, °", "Групповая задержка, мкс")):
        ax.set_ylabel(label)
    axes[2].set_xlabel("Частота аудиотона, Гц")
    ticks=[20,50,100,200,500,1000,2000,5000,10000,20000]
    axes[2].set_xticks(ticks, [str(f) for f in ticks])
    axes[0].legend(loc="lower left", ncol=2, fontsize=8)
    fig.suptitle("6,144 МГц • RC 10 мкс • PCM 48 кГц, −3 dBFS\nИсходный RC-PDM без dither, feedback и интерполяции", fontsize=13)
    fig.text(.5,.012,"Симуляция основной гармоники; задержка не компенсирована. Производная фазы по 21 точке.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0,.035,1,.94));fig.savefig(file,dpi=160);plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--skip-radio", action="store_true", help="Only generated inputs; no local radio recordings needed")
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    import matplotlib
    reports={"modern": ROOT/"docs/benchmarks/esp8266-rcpdm-6144-2026-09-06/results.json",
        "response": ROOT/"docs/benchmarks/esp8266-rcpdm-6144-response-2026-09-06/results.json",
        "legacy": ROOT/"docs/benchmarks/esp8266-pdm-frequency-matrix-2026-09-06/results.json"}
    old={key: json.loads(file.read_text(encoding="utf-8")) for key,file in reports.items()}
    exe=build(args.output/"build", "rcpdm_6144_quality")
    legacy=build(args.output/"build", "pdm_matrix_quality")
    sources=[Path(__file__), ROOT/"esp8266/rtos-sdk-native/main/rc_pdm.h", ROOT/"tests/native/rcpdm_simple.h"]
    sources += [ROOT/path for path in old["response"]["source_sha256"]]
    sources += [ROOT/"tools/esp8266_audio_profile/pdm_matrix_quality.cpp"]
    result=dict(complete=False, measured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_sha256={str(p.relative_to(ROOT)): model.original.sha(p) for p in sources},
        controls={key: dict(path=str(file.relative_to(ROOT)),sha256=model.original.sha(file)) for key,file in reports.items()},
        configs=CONFIGS, bit_rate_hz=6144000, pcm_rate=48000, firmware_flashed=False,
        self_tests={name: json.loads(subprocess.check_output([str(program),"--self-test"],text=True)) for name,program in (("modern",exe),("legacy",legacy))},
        numpy_version=np.__version__,matplotlib_version=matplotlib.__version__,
        audio_band_hz=[20,20000],quality_integration_band_hz=[20,20001],
        legacy_definition="Original unsigned fixed32 algorithm; no interpolation/dither/error feedback. Only bit count 32->128 and RC shift 4->6 adapted for the same ~10us RC.",
        cases=[])
    jobs=[dict(id=f"tone-{hz}hz-3db", type="tone", hz=hz, level_dbfs=-3) for hz in response.FREQUENCIES]
    jobs += [dict(row) for row in old["modern"]["cases"] if row["type"]!="tone" or row["level_dbfs"]!=-3]
    if args.skip_radio: jobs=[job for job in jobs if job["type"]!="radio"]
    for index, job in enumerate(jobs,1):
        file=args.output/(job["id"]+".s16le")
        if job["type"]=="radio":file=ROOT/job["pcm"]
        elif job["type"]=="silence":np.zeros(144000,dtype="<i2").tofile(file)
        else:
            np.round(32767*10**(job["level_dbfs"]/20)*np.sin(2*np.pi*job["hz"]*np.arange(144000)/48000)).astype("<i2").tofile(file)
        pcm=np.fromfile(file,dtype="<i2");pcm_hash=model.original.sha(file)
        if "pcm_sha256" in job and pcm_hash!=job["pcm_sha256"]:raise ValueError("Input mismatch")
        paths, modern_proof=modern.generate(exe,file,args.output/job["id"],modern.SEED)
        legacy_paths, legacy_proof=legacy_capture(legacy,file,args.output/(job["id"]+"-legacy"))
        if model.original.sha(paths["pdm128"])!=model.original.sha(legacy_paths.pop("pdm128")):
            raise ValueError("Separate PDM implementations differ")
        paths.update(legacy_paths)
        hashes={name:model.original.sha(path) for name,path in paths.items()}
        quality=model.analyze(pcm,paths,CONFIGS,job.get("hz"),band_high_hz=20001)
        row={key:job[key] for key in ("id","type","hz","level_dbfs") if key in job}
        row.update(pcm=str(file.resolve()),pcm_sha256=pcm_hash,bitstream_sha256=hashes,quality=quality,
            proofs=dict(modern=modern_proof,legacy=legacy_proof),reverified=[])
        before_response=next((c for c in old["response"]["cases"] if c["hz"]==job.get("hz") and job.get("level_dbfs")==-3),None)
        if before_response:
            row["response"]=response.measure_transfer(pcm,paths,job["hz"])
            for name in modern.NAMES:
                if hashes[name]!=before_response["bitstream_sha256"][name]:raise ValueError("Response control bits changed")
                assert_saved_scores(quality["models"][name],before_response["quality"]["models"][name])
                if row["response"][name]!=before_response["response"][name]:raise ValueError("Complex response changed")
            if pcm_hash!=before_response["pcm_sha256"]:raise ValueError("Response input changed")
            row["reverified"].append("response")
        before_modern=next((c for c in old["modern"]["cases"] if c["id"]==job["id"]),None)
        before_legacy=next((c for c in old["legacy"]["cases"] if c["id"]==job["id"]),None)
        if before_modern or before_legacy:
            historical=model.analyze(pcm,paths,CONFIGS,job.get("hz"))
            row["quality_historical_band"]=historical
            for tag, before, mappings in (("modern",before_modern,{name:name for name in modern.NAMES}),
                    ("legacy",before_legacy,{**LEGACY,"pdm128":"pdm128"})):
                if not before:continue
                if pcm_hash!=before["pcm_sha256"]:raise ValueError("Historical PCM changed")
                for name, archived in mappings.items():
                    if hashes[name]!=before["bitstream_sha256"][archived]:raise ValueError("Historical bits changed")
                    assert_saved_scores(historical["models"][name],before["quality"]["models"][archived])
                row["reverified"].append(tag)
        row["idle"]={}
        for name,path in paths.items():
            words=np.fromfile(path,dtype="<u4")[12000*4:-12000*4]
            row["idle"][name]=dict(words_checked=len(words),constant_word=f"0x{int(words[0]):08x}" if np.all(words==words[0]) else None,
                alternating_only=bool(np.all(np.isin(words,[0x55555555,0xaaaaaaaa]))))
        result["cases"].append(row);save(args.output/"results.json",result)
        print(f"{index}/{len(jobs)} {job['id']}: seven variants complete",flush=True)
    tones=[c for c in result["cases"] if "response" in c]
    result["curves"]={name:{filt:response.curve(response.FREQUENCIES,
        [complex(**c["response"][name][filt]["transfer"]) for c in tones],cfg["fixed_delay_seconds"])
        for filt in FILTERS} for name,cfg in CONFIGS.items()}
    result["lsb"]=legacy_lsb(legacy,args.output/"lsb",old["modern"])
    for name,expected in result["source_sha256"].items():
        if model.original.sha(ROOT/name)!=expected:raise ValueError("Source changed during measurement")
    args.archive.mkdir(parents=True,exist_ok=True);plot(result,args.archive/"response-rc10us.png")
    result["complete"]=True;save(args.output/"results.json",result);save(args.archive/"results.json",result)
    print("Complete; firmware unchanged",flush=True)


if __name__=="__main__":main()
