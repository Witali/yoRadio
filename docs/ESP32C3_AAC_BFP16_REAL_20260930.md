# BFP16 on real AAC radio recordings — 2026-09-30

**Result: the measured BFP16 variants still fail the maximum 1-LSB PCM error
requirement on real programme audio.** With an exponent per complex QMF sample,
the maximum is 3 LSB, RMS error is 0.295–0.359 LSB, and 0.925–1.383% of samples
exceed 1 LSB across the four HE/v2 recordings. AAC-LC and unquantized controls
remain byte-identical.

This extends the [original BFP16 experiment](ESP32C3_AAC_BFP16_20260930.md).
The real Espressif AAC decoder executes in QEMU; **the data are real radio
recordings, the execution is emulated**. RAM saving remains zero: this is the
same pack/expand precision prototype with original int32 storage. Production
firmware and the physical board were not changed.

## Recordings and coverage

Five approximately 30-second ADTS recordings, two stations, captured without
re-encoding at 21:02–21:03 UTC on 2026-09-30:

| Recording | Broadcast | FFmpeg-verified profile | PCM rate / channels | Decoded frames | Scalar PCM samples (L+R) |
| --- | --- | --- | --- | ---: | ---: |
| `groovesalad64` | SomaFM Groove Salad, 64 kbit/s | HE-AAC | 44,100 Hz / 2 | 646 | 2,646,016 |
| `groovesalad32` | SomaFM Groove Salad, 32 kbit/s | HE-AAC | 44,100 Hz / 2 | 646 | 2,646,016 |
| `groovesalad16` | SomaFM Groove Salad, 16 kbit/s | HE-AAC v2 / PS | 32,000 Hz / 2 | 469 | 1,921,024 |
| `abba64` | 101.ru ABBA, 64 kbit/s | HE-AAC v2 / PS | 44,100 Hz / 2 | 646 | 2,646,016 |
| `groovesalad128` | SomaFM Groove Salad, 128 kbit/s | AAC-LC control | 44,100 Hz / 2 | 1,292 | 2,646,016 |

SomaFM URLs come from its [official direct-stream page](https://somafm.com/groovesalad/directstreamlinks.html);
the 101.ru station/endpoint comes from the repository playlist. Exact URLs,
input hashes, file completion times, library/ELF hashes and FFprobe output are
retained in each result JSON. [Independent FFprobe frame counts](../tests/results/esp32c3-aac-bfp16-real-20260930/ffprobe-frames.json)
match the number of frames produced by the SDK. No frame/format mismatch,
reduced-rate fallback or lost PS stereo passed the assertions.

There are **12,505,088 scalar samples per block-size comparison**, of which
9,859,072 belong to HE/v2. Each recording is decoded once continuously, without
looping, for block sizes 32, 8, 1 and an unmodified control. All four cases run
three times: **60 paired comparisons**. Statistics agree exactly across reruns;
the summary counts each recording once rather than treating repeated decoding
as additional independent audio. Groove Salad bitrate variants can contain
overlapping programme audio; this is not five independent music selections.

## Errors

Worst error and range across the four HE/v2 recordings:

| Subbands sharing an exponent | Maximum absolute error | RMS error range | Samples exceeding 1 LSB |
| --- | ---: | ---: | ---: |
| 32 | 161 LSB | 0.587–1.794 LSB | 3.872–5.793% |
| 8 | 24 LSB | 0.476–0.538 LSB | 2.489–3.108% |
| 1 complex sample | 3 LSB | 0.295–0.359 LSB | 0.925–1.383% |
| Unmodified controls | 0 LSB | 0 LSB | 0% |

Finest blocking, channels combined:

| Recording | Mean absolute error | RMS error | Maximum | >1 LSB | P99 absolute error | Signal/error energy ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Groove Salad 64 | 0.097992 LSB | 0.354348 LSB | 3 LSB | 1.347384% | 2 LSB | 82.05 dB |
| Groove Salad 32 | 0.095575 LSB | 0.349735 LSB | 3 LSB | 1.308609% | 2 LSB | 81.66 dB |
| Groove Salad 16 / PS | 0.068054 LSB | 0.294792 LSB | 3 LSB | 0.924507% | 1 LSB | 83.61 dB |
| ABBA 64 / PS | 0.100676 LSB | 0.359204 LSB | 3 LSB | 1.382531% | 2 LSB | 85.32 dB |

The largest observed deviation is in Groove Salad 32 with 32-subband blocks:
left channel at decoded sample **631,483**, approximately **14.319342 s**;
reference **4,462**, candidate **4,623**, difference **+161**. It is not a clipped
sample. Full-scale sample counts are unchanged between candidate and baseline
for all captured cases, though some source recordings already reach full scale.

[Complete tables](../tests/results/esp32c3-aac-bfp16-real-20260930/TABLES.md) cover
every block size and control. [Machine-readable summary](../tests/results/esp32c3-aac-bfp16-real-20260930/summary.json)
adds signed bias, error RMS in dBFS, identical-sample percentage, P50/P90/P95/P99/
P99.9, clipping counts, and the sample/time/value of the maximum. Each per-file
`result.json` contains separate L/R integer sums and histograms for every run.

## Meaning and validation of the statistics

For each raw signed 16-bit PCM sample, `e = candidate - reference`:

- MAE = `sum(abs(e)) / N`; RMS = `sqrt(sum(e*e) / N)`.
- Signed bias = `sum(e) / N`; the acceptance criterion is `max(abs(e)) <= 1`.
- Signal/error ratio = `10*log10(sum(reference*reference) / sum(e*e))`.
  It compares two decoder outputs, not the AAC stream with an uncompressed
  studio master, and is not a perceptual quality score.
- Error dBFS uses full scale 32,768. Zero error energy gives an infinite
  signal/error ratio; JSON stores undefined/infinite dB values as `null`.
- Histogram bins are exact at 0–4,095 LSB, then 4,096 LSB wide up to 65,535.
  Every observed error here is in the exact region. Future large-error
  percentiles are reported as bounds, never as an invented exact value.

Comparison occurs before output resampling, normalization and PDM, with no
alignment shift or gain correction. Both decoder instances receive identical
bytes; output lengths, channels, rate, bit depth and input consumption must
match. The host validates histogram totals against sample counts, exceedance
counts and error moments. Repeated runs must agree before summary generation.

The initial run exhausted the old **4 KiB QEMU smoke-task stack**; its
[failure log](../tests/results/esp32c3-aac-bfp16-real-20260930/initial-4k-stack.log)
is retained and rejected by the parser. The BFP16 test now uses the existing
codec-benchmark stack policy: 16 KiB decoder stack plus 4 KiB harness allowance.
The 32,888-byte histogram is separately allocated only for external recordings.
Subsequent runs completed with controls and guards intact. This changes the
emulator test task, not the production audio-task configuration.
The original 45 synthetic comparisons were also rerun: sample/frame counts,
error maxima, differing-sample counts and QMF coverage match the prior run.

Instruction counts are still captured, excluding the new PCM-statistics and
histogram-printing work. For finest blocking, median guest instruction overhead
is +11.221%, +10.455%, +9.500% and +6.223% respectively for the four HE/v2 rows
above. They remain QEMU instruction demand, not physical CPU/cache measurements;
the precision requirement fails before production acceptance.

## Reproduce and retain inputs

Build the BFP16 image as described in the original experiment. Capture a finite
fragment with FFmpeg 8.1.1 (the version used here); this copies encoded packets:

```powershell
ffmpeg -nostdin -hide_banner -loglevel warning -rw_timeout 15000000 -icy 0 `
  -i https://ice5.somafm.com/groovesalad-64-aac -t 30 -map 0:a:0 `
  -c:a copy -f adts -n .build/sample.aac

& C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe `
  tools/codec_benchmark/run_aac_bfp16.py --dependency-root C:/Work/yoRadio/.idf `
  --qemu .build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl `
  --input .build/sample.aac --source-url https://ice5.somafm.com/groovesalad-64-aac `
  --output .build/sample-results

python tools/codec_benchmark/summarize_aac_bfp16_real.py `
  .build/sample-results/result.json --output .build/sample-summary

python tests/test-aac-bfp16.py
python tests/test-aac-bfp16-real.py
```

Supply several result paths to combine recordings. The runner verifies the input
as ADTS with FFprobe and inserts it into the unused app1 area of a disposable
QEMU flash image. It never writes to a board. A completed precision failure
returns **2**; a harness failure returns **1**. AAC-LC controls return **0**.

Original recordings remain locally under
`.build/aac-bfp16-real-20260930/inputs/`; their audio is not checked into Git.
The repository retains scripts, hashes, logs and numerical evidence. Fresh live
captures contain different audio and will not reproduce these exact numbers;
use the retained local inputs for exact reruns. This corpus demonstrates a
failure of the current 1-LSB gate; it is not exhaustive AAC qualification or a
physical-radio playback/CPU test.
