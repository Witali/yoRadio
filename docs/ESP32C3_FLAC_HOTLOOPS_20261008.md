# FLAC hot-loop experiments — 2026-10-08

## Decision and scope

Prioritize residual decoding and ordinary LPC reconstruction. Together they
account for 82–86% of the exclusive **host decoder CPU time** in the existing
20-file radio corpus. The Rice experiment is the best measured candidate so
far: less host decode time and less RV32 object code. It still needs a physical
ESP32-C3 comparison before becoming a production default.

Two GPT-6.1 Sol subtasks prepared the isolated experiments. The parent reviewed
the arithmetic, buffer consumption, tests and generated instructions; ran the
whole-file comparisons; and independently compared the RV32 ELF sections.
One additional compiler experiment was rejected because its instructions did
not change. Model suggestions alone were not treated as validation.

Both retained switches are **off by default**, including explicit `=0`:

- `FLAC_BYTEWISE_RICE=1`: inspect the remaining byte at once when decoding the
  unary Rice quotient, instead of calling the generic bit reader per zero.
- `FLAC_LPC_NO_AUTO_UNROLL=1`: retain manual four-tap groups, but prevent GCC
  from further expanding that loop across all 32 taps.

The initial host study used experimental C++ compile definitions. The
[physical follow-up](ESP32C3_FLAC_RICE_PHYSICAL_20261008.md) adds a default-off
Kconfig option for Rice and compares matched application images on the C3.
No application image or board state was changed by the host study itself.
RAM allocations and the existing 4–24-bit, mono/stereo,
maximum-8192-sample-block support remain unchanged. PCM output remains s16.

## What is hot

The [existing corpus](ESP32C3_FLAC_RADIO_20261006.md) contains ten different
120-second radio excerpts, each encoded as 24-bit FLAC twice, allowing maximum
LPC orders 12 and 32. The maximum is allowed, not forced. This is a deliberately
demanding corpus from one broadcaster, not a representative FLAC prevalence
survey. Original broadcast audio remains local and is omitted from Git.

`profile_flac_hotloops.py` instruments **a frozen copy** of the actual shared
decoder. Nested scopes subtract child time, giving non-overlapping stages.
Probes are per block/subframe, never per sample, bit or coefficient.
`CLOCK_THREAD_CPUTIME_ID` excludes descheduling; file I/O and the harness's PCM
copy are outside the timed decoder. Each file is decoded three times.

| Exclusive stage | LPC maximum 12 | LPC maximum 32 | Relevant code |
| --- | ---: | ---: | --- |
| Residual decoding, including Rice/bit reader | 53.99% | 43.16% | `decodeResiduals`, `readRiceSignedInt`, `readUint` |
| Prediction reconstruction | 28.19% | 42.57% | `restoreLinearPrediction` |
| Subframe headers, warm-up/coefficient parsing, sample validation | 5.93% | 4.75% | `decodeSubframe` and subframe setup |
| Frame parsing and PCM output | 9.11% | 7.25% | exclusive `FLACDecode` |
| Stereo reconstruction and subframe dispatch | 2.78% | 2.27% | exclusive `decodeSubframes` |

Percentages divide summed stage CPU time by the summed five stages for ten
files per group. Profiling overhead and the extra outer timing calls mean this
is not a partition of all process time. The separate uninstrumented benchmark
below is used for speed comparisons. Raw measurements, including the unusually
slow original `thetrip-lpc12` host observation, are retained.

These measurements use x86-64 GCC 13.3 in WSL. ESP32-C3 has different multiply,
CLZ and flash/cache costs. The old calibration for the Espressif FLAC backend
does **not** convert these host results to timings for this custom decoder.

## Measured alternatives

### Code size on the target architecture

RV32 GCC 15.2 uses the actual IDF 6.1 project's compile flags, segmented workspace,
512 output frames and `-O3`. The core also has its existing `Ofast` pragma.
The final audit compiles frozen source/header/response-file inputs into separate
objects and redirects all generated dependencies into the experiment directory.

| Variant | Sum of `.text*` object sections | Change | Ordinary LPC function body |
| --- | ---: | ---: | ---: |
| Current scalar reader | 13,592 B | — | 1,596 B |
| Bytewise Rice | 13,118 B | −474 B | 1,596 B |
| Restrict further LPC unrolling | 12,886 B | −706 B | 890 B |
| Both | 12,412 B | −1,180 B | 890 B |

These are **relocatable object sizes**, not final linked firmware savings.
Inlining, dead-code elimination and linker relaxation can change the final
result. All non-code allocated sections are identical. The parent independently
compiled the original `f284fa12` core and verified that every allocated section
matches the final default-off object, not just its total size.

### Decode time on the host

Four complete files cover lower/higher average LPC orders. Four measurement
rounds alternate forward/reverse variant order; each invocation decodes the
file three times. Values below compare the median total decode CPU time with
the scalar control. Negative means less time. Raw individual times are saved.

| File | Bytewise Rice | Restrict LPC unrolling | Both |
| --- | ---: | ---: | ---: |
| Groove Salad, maximum LPC12 | −13.15% | −1.75% | −9.93% |
| Groove Salad, maximum LPC32 | −7.58% | +5.89% | +3.89% |
| Bossa Beyond, maximum LPC12 | −9.66% | −0.59% | −9.53% |
| Bossa Beyond, maximum LPC32 | −8.79% | +6.23% | −1.70% |

Thus smaller LPC code is not automatically faster. Retain that switch for
target cache experiments; prioritize Rice for the physical A/B test. Neither
the host results nor the code-size reduction establish that HTTPS/DMA stalls
are fixed: the [previous physical profile](ESP32C3_TLS_PATH_PROFILE_20261008.md)
also showed substantial TLS/network work outside FLAC decoding.

## Exactness and review

The Rice change preserves the existing byte refill boundary: it never reads
ahead of the byte needed for the current code. This matters because frame
consumption accounting and the next frame share the reader state. It guards
`clz(0)`, bounds the quotient, rejects the forbidden folded `UINT32_MAX`, and
preserves the scalar reader's error and partial-cache state on truncation.
The unchanged zigzag and remainder code follows
[RFC 9639, sections 9.2.7.2–9.2.7.3](https://www.rfc-editor.org/rfc/rfc9639.html#section-9.2.7.2).

Validation completed:

- Independent scalar Rice reference under ASan/UBSan: **294,888 cases /
  941,077 read comparisons per variant**, for default, explicit scalar and
  bytewise implementations. Includes all parameters 0–30, cached offsets 0–7,
  quotient overflow, invalid parameters, every byte cut in selected codes,
  random/chained reads, and full cache/byte/error-state comparisons. Parent
  reran this against the final implementation.
- **120 synthetic files × 3 paths = 360 exact PCM comparisons** against
  known PCM and a fresh FFmpeg decode, with ASan/UBSan. Segmented core,
  contiguous Arduino core and C3 streaming adapter are covered with both
  experiments enabled. Allocation-failure and reopen checks pass for all 120
  files.
- **20 complete radio files × 3 paths = 60 more exact PCM comparisons**
  against fresh FFmpeg output under ASan/UBSan with both experiments enabled.
- Boundary and predictor suites cover truncated inputs, malformed fields,
  wide stereo side samples, dense/sparse/zero/random coefficients, all
  prediction shifts and segment boundaries: 16 input-length cases and 4,492
  predictor cases in each of the segmented and contiguous configurations.
- All 20 radio files match the retained FFmpeg PCM hashes in both ordinary
  and instrumented Rice runs. The alternating four-variant benchmark also
  verifies the complete PCM hash after each invocation.

Neither experiment reduces stored sample precision or narrows the predictor
sum. Wide arithmetic remains necessary for valid high-depth LPC. See
[RFC 9639 Appendix A.3](https://www.rfc-editor.org/rfc/rfc9639.html#appendix-A.3).

## Other candidates, in priority order

1. **Partition-local Rice reader and destination spans.** Resolve the
   parameter limit and output segment once per span/partition, and keep reader
   state local across several residuals. This targets the hottest measured
   stage. Preserve exact state on every error and never step pointers across
   separate allocations. Compare against the current bytewise experiment.
2. **Conditional narrow LPC accumulation with a proved bound.** A sufficient
   bound is `2^(sampleDepth-1) * sum(abs(coef)) <= INT32_MAX`. It is only safe
   when every reconstructed sample is checked before it becomes history.
   Current depth validation is after the subframe, so merely changing `int64_t`
   to `int32_t` would be unsafe on malformed data. Keep a wide fallback and
   wide residual addition; measure the cost of the additional validation.
3. **Specialized fixed-order predictors.** Fixed orders 0–4 currently use the
   general LPC mechanism. Exact finite-difference or specialized formulas
   may remove products, but the radio corpus is predominantly LPC. Measure
   a representative fixed-predictor workload before prioritizing this.
4. **Lower-cost PCM/stereo/validation spans.** Resolve segmented pointers and
   constant scale factors outside sample loops; retain validation. These stages
   are smaller than the two primary targets.
5. **Sparse recurrence details.** An already range-checked reconstructed
   sample can be explicitly narrowed before a wide multiply, and sparse
   history addressing could use spans. Do not narrow endpoint sums/differences,
   which can need 33 bits. No corpus subframe used this recurrence, so it has
   lower priority than ordinary LPC and residuals.

**Rejected:** exposing the valid 0–15 predictor shift by adding a mask in the
ordinary lambda. Although the assembly has a wide-shift branch, GCC removes
the redundant mask early. The frozen experiment produced identical allocated
sections and instructions. Its source and disassembly are retained as rejected
evidence; the extra switch was removed from production source.

## Reproduction and evidence

Run from the worktree root with the normal Python environment, WSL g++ and
FFmpeg installed. Each `NEW_*` destination should be fresh.

```text
python tools/codec_benchmark/profile_flac_hotloops.py --fixtures LOCAL_RECORDINGS --output .build/NEW_PROFILE
python tools/codec_benchmark/profile_flac_hotloops.py --fixtures LOCAL_RECORDINGS --output .build/NEW_RICE_PROFILE --define FLAC_BYTEWISE_RICE=1
python tools/codec_benchmark/compare_flac_hotloops.py --fixtures LOCAL_RECORDINGS --output .build/NEW_COMPARE --case radio-groovesalad-lpc12 --case radio-groovesalad-lpc32 --case radio-bossa-lpc12 --case radio-bossa-lpc32
python tools/codec_benchmark/run_flac_rice.py --output .build/NEW_RICE
python tools/codec_benchmark/run_flac_bounds.py --output .build/NEW_BOUNDS --define FLAC_BYTEWISE_RICE=1 --define FLAC_LPC_NO_AUTO_UNROLL=1
python tools/codec_benchmark/run_flac_bounds.py --contiguous --output .build/NEW_CONTIGUOUS --define FLAC_BYTEWISE_RICE=1 --define FLAC_LPC_NO_AUTO_UNROLL=1
python tools/codec_benchmark/run_flac_depths.py --output .build/NEW_MATRIX --allocation-failures --define FLAC_BYTEWISE_RICE=1 --define FLAC_LPC_NO_AUTO_UNROLL=1
python tools/codec_benchmark/run_flac_depths.py --fixtures LOCAL_RECORDINGS --output .build/NEW_RADIO --define FLAC_BYTEWISE_RICE=1 --define FLAC_LPC_NO_AUTO_UNROLL=1
python tests/test-flac-hotloops-evidence.py
```

The [retained evidence](../tests/results/esp32c3-flac-hotloops-20261008/index.json)
contains reports, logs, input hashes, source snapshots, target compiler commands
and compressed disassembly. Host binaries, PCM and radio recordings are excluded.
Archive snapshots preserve the actual source revision used by each measurement;
minor guard/line-ending revisions are kept separately. The final defaults and
RAM were checked independently against the original RV32 object.
