# FAAD2 float32 versus fixed-point PCM, 2026-10-01

## Result

Pristine FAAD2 floating-point and fixed-point decoding are **not generally
sample-equivalent** on this corpus. AAC-LC differs by at most 2 signed-16 PCM
LSB. The four Groove Salad captures reach 2–6 LSB. Synthetic HE/HEv2 and the
onset of PS in ABBA show much larger differences, already without any history
compression. The cause of those large differences has not been isolated.

These numbers measure **fixed PCM minus float PCM**. Floating-point is the
comparison reference, not a demonstrated bit-exact ground truth. This test does
not establish which path is more faithful to an independent reference decoder.

| Input | Actual output | Maximum absolute difference, LSB | RMS difference, LSB | Signal/difference, dB |
| --- | --- | ---: | ---: | ---: |
| Synthetic LC 22.05 kHz mono | 44.1 kHz mono (*) | 2 | 0.687543 | 77.16 |
| Synthetic LC 44.1 kHz stereo | 44.1 kHz stereo | 2 | 0.696694 | 77.38 |
| Synthetic LC 48 kHz stereo | 48 kHz stereo | 2 | 0.699449 | 77.36 |
| Synthetic HE 44.1 kHz stereo | 44.1 kHz stereo | **7233** | **985.784172** | 13.35 |
| Synthetic HE 48 kHz stereo | 48 kHz stereo | **5019** | **971.132926** | 13.58 |
| Synthetic HEv2 44.1 kHz stereo | 44.1 kHz stereo, PS | **7678** | **866.748495** | 14.50 |
| ABBA 64 kbps | 44.1 kHz mono, then stereo/PS | **10211** | **83.421390** | 38.01 |
| Groove Salad 16 kbps | 32 kHz mono, no PS | 5 | 0.827201 | 74.65 |
| Groove Salad 32 kbps | 44.1 kHz stereo | 6 | 0.818267 | 74.26 |
| Groove Salad 64 kbps | 44.1 kHz stereo | 3 | 0.786597 | 75.13 |
| Groove Salad 128 kbps, LC | 44.1 kHz stereo | 2 | 0.718915 | 76.69 |

(*) Unmodified FAAD's default implicit-SBR policy upsamples low-rate LC too:
`dontUpSampleImplicitSBR=0` produces `NO_SBR_UPSAMPLED`, not active SBR tools.
The test preserves that default equally in both builds. It imposes **no 22 kHz
ceiling** and does not resample either output to make the comparison match.
This default upsampling is distinct from the firmware's planned preservation
of the actual decoded stream rate.

RMS and signal/difference use all scalar samples, weighted by their count,
without removing DC bias, silence, transients or clipping. Signal/difference is
`10*log10(sum(float_pcm^2)/sum((fixed_pcm-float_pcm)^2))`; it is not an audible
quality score. Per-channel statistics, integer error histograms, mean bias,
95th/99th/99.9th percentiles and per-frame errors are retained in the results.

## Investigation of the large differences

- ABBA has 646 input frames. PS first becomes active at zero-based frame 11.
  The large differences occur at frames **11 and 12**, with maxima **10211 and
  841 LSB**. From frame 13 onward, the maximum is **4 LSB**, RMS **0.803862 LSB**.
  The main table includes the entire recording, including both transient frames.
- Synthetic HE/HEv2 differences persist across the signal. They are present in
  the first pass too, so repeating the short fixture is not their sole cause.
  There are no signed-16 rail samples in either synthetic HE/HEv2 output.
- Frame lengths, sample counts, rates, channels, public SBR status and active PS
  match exactly. Passive internal traces of `sbr->ret`, header count, `kx` and
  `M` also match between modes. Synthetic HE/v2 has `sbr->ret=0` throughout.
  Thus neither a differing reported sample rate nor a differing SBR error
  status explains those large synthetic differences.
- Real captures start midstream. Both modes report the same initial missing-SBR-
  header interval: ABBA 11 frames, Groove Salad 16 kbps 4 frames and 32 kbps
  9 frames. These frames remain in the comparison. Inspect the retained state
  traces for the other inputs. A public full-rate label alone is insufficient
  evidence of successful high-band processing.
- Every decode was repeated in a fresh process. PCM, frame and state hashes
  reproduce exactly. All fixed PCM hashes also match the pristine fixed baseline
  from the [earlier supplied PS patch test](FAAD2_PS_PATCH_QUALITY_20261001.md).

The small differences have a visible negative mean bias, around -0.47 to -0.50
LSB on LC/Groove Salad. The pinned `output.c` float path clips and calls `lrintf`;
the fixed path adds a sign-dependent half-unit and then arithmetic-shifts by
`REAL_BITS`. For negative values, subtracting half before an arithmetic shift
differs from round-to-nearest. This output conversion can contribute a one-LSB
negative bias. It does **not** explain the thousands-LSB HE/PS differences;
the comparison makes no correction for it.

## Method and scope

- Upstream [FAAD2](https://github.com/knik0/faad2/tree/e8e76f0a44db45aed773a3f62fe35a63c867a738),
  revision `e8e76f0a44db45aed773a3f62fe35a63c867a738`.
- Archive SHA-256: `36f5aa8cbfcc442cdaced7f29dbe66276c62a1432d3c639405c07bcdf47614ab`.
  Verify every extracted source file against the pinned archive before building.
- Build both from the same unmodified sources with GCC `-O2`,
  `-fno-strict-aliasing`, `-ffloat-store`, no fast-math. The arithmetic switch
  `-DFIXED_POINT=1` is the only configuration difference. Float uses ordinary
  32-bit `float`, not double; fixed uses 32-bit integers. Full complex SBR and PS
  are compiled in. No packed-history patch or storage quantizer is present.
- Request `FAAD_FMT_16BIT` in both. `defObjectType=LC` is the initialization
  fallback; the actual object type is read from ADTS. Feed each full ADTS frame
  in order, assert full consumption/no decode error, and retain each emitted
  sample. No additional end padding/drain is injected into either decoder.
- Six tracked synthetic LC/HE/v2 fixtures run for two continuous passes, keeping
  decoder state across the join. Five retained 30-second real ADTS captures run
  once. No source audio is re-encoded. This gives **22 main decodes plus 22
  independent repeatability controls**.
- Compare sample-for-sample without alignment, gain matching or resampling.
  Deinterleave per frame: ABBA initially emits mono before PS activates. Treating
  the complete file as stereo would corrupt the channel statistics.
- This matrix covers the listed rates and mono/stereo LC/HE/v2 samples only;
  it is not all-format conformance. Upstream fixed-point also undefines
  `MAIN_DEC` in `common.h`; these LC-based streams do not exercise AAC Main.
  Audit supported profiles before considering any firmware backend replacement.
- No C3 build, firmware change, board deployment, peak-memory measurement or
  C3 speed benchmark was performed. Equal 32-bit scalar storage in these two
  modes does not itself halve QMF history RAM.

## Consequence for memory optimization

The ±2 final / ±5 development LSB storage limits compare an optimized decoder
with **the same arithmetic backend without compression**. They must not be
reinterpreted as float-versus-fixed limits or relaxed because an existing
arithmetic-mode discrepancy is larger. The supplied PS patch's ≤2 LSB result
remains a fixed-versus-fixed result, not a claim of ≤2 LSB versus float.

Before selecting FAAD as a replacement backend, isolate the sustained synthetic
SBR discrepancy and the PS-onset transient, and compare with an independent
reference using matching timing/layout. Preserve full sample rates, SBR/PS and
channels throughout that work.

## Reproduce and validate

Run from the repository worktree, using Python 3.12 and GCC on Linux or WSL GCC
on Windows. The pinned archive and verified extraction are the ones prepared by
`tools/codec_benchmark/run_faad_history_comparison.py`. The default real recordings
directory is ignored and must contain the five original ADTS captures; missing
or different recordings cannot silently count as reproducing the retained run.

```text
python tools/codec_benchmark/run_faad_arithmetic_comparison.py
python tests/test-faad-arithmetic-comparison.py
```

Use `--archive`, `--recordings` and `--output` to select other existing paths.
Raw PCM and executables stay under ignored `.build/faad-arithmetic-20261001/`.
The [retained evidence](../tests/results/faad2-arithmetic-20261001/comparison.json)
contains source/input/output hashes and exact compiler commands. Adjacent logs,
frame/state traces and `*.errors.json` retain the diagnoses. The validation test
checks these measurements, including the large discrepancies; passing it does
not declare arithmetic equivalence or qualify a production decoder.
