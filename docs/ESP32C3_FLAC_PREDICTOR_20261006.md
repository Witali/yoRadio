# FLAC LPC reconstruction cost on ESP32-C3

## Problem and exact optimization

The [source-depth qualification](ESP32C3_FLAC_DEPTHS_20261005.md) exposed CPU
saturation on legal high-order LPC streams. Short WebUI/EOF checks passed, but
20/24-bit test streams delivered too little audio per second and emitted
diagnostic register dumps. Most decoded program counters were in the predictor.

`restoreLinearPrediction` now skips trailing zero coefficients while preserving
the encoded warm-up/residual positions. For a history wholly inside one workspace
segment, it resolves the sample pointer once per output sample. Histories crossing
separate allocations still use the checked segment lookup for each tap; pointer
arithmetic never crosses allocation boundaries. The same loop supports contiguous
Arduino storage. All multiply/accumulate and residual addition remain signed
64-bit, with the existing representability check before storing signed 32-bit.
No coefficient quantization, PCM precision reduction or format limit is added.

## Follow-up: four-tap groups (6 October 2026)

The inner loop now processes four consecutive coefficients per iteration, then
handles the remaining zero to three coefficients. This removes repeated loop
control and address updates on RV32. The production `-O3` compiler further
expands these groups; the retained disassembly shows the actual generated code.
Histories crossing workspace allocations retain the original indexed path.

The predictor still uses signed 64-bit products and sums, performs the original
right shift only after summing, and checks residual addition before storing the
result. The dependency on preceding reconstructed samples is unchanged. These
requirements follow [RFC 9639 section 9.2.6](https://www.rfc-editor.org/rfc/rfc9639.html#section-9.2.6).
Reducing the accumulator to 32 bits without a proven range bound is unsafe for
high-depth streams; see the [integer-width discussion](https://www.rfc-editor.org/rfc/rfc9639.html#appendix-A.3).

The new image is `firmware/development/esp32c3-flac-unroll/app.bin`, built with
the same configuration as `esp32c3-flac-predictor`. App size increases by
**1,056 bytes**, to 1,577,600 bytes. IRAM, static DRAM and RTC section sizes are
unchanged; no heap allocation or persistent workspace is added. The generated
predictor stack frame is 64 bytes; this is not a claim of zero stack usage.

Host validation passes **2,444 scalar-reference predictor cases**, including
all orders 0..32, every legal shift 0..15, coefficient extrema, asymmetric
coefficients, all four-tap remainders and a partially allocated final segment.
Both storage modes pass ASan/UBSan. **375 full decoder comparisons** match
known PCM and FFmpeg: 120 format fixtures, four real 24-bit/8192-block files,
and the 64-second dense LPC32 file, each through three decoder paths. The
truncation/overflow regressions pass in both storage modes.

The immediate before/after physical test uses the identical 64-second,
24-bit stereo, dense LPC32 fixture, 60 seconds of playback with frequent WebUI
polling, and the same firmware configuration. The first 10 seconds are excluded
from timing statistics using the existing rule.

| Measurement | Previous predictor | Four-tap groups |
| --- | ---: | ---: |
| Decode-call time per second of audio | 599.1 ms | 481.5 ms |
| Audio duration / elapsed duration | 0.8788 | 0.9867 |
| Mean / peak CPU | 100 / 100% | 100 / 100% |
| CPU acceptance gate | FAIL | FAIL |
| Runtime diagnostic gate | FAIL | FAIL |
| Heap recovery after Stop | PASS | PASS |

This pair shows **19.6% less elapsed decode-call time per audio second**
(about 1.24x decoder throughput). It is not a measurement of the LPC function
alone: decode-call timing includes the rest of FLAC and task interruptions.
The CPU remains saturated and runtime register dumps remain present, so the
candidate is **not production-qualified** and this is not a real-time playback
PASS. OTA while AAC played passed and retained Wi-Fi, playlist and settings.

A second candidate run confirms the direction: 475.2 ms of decode-call time
per audio second (20.7% below the control), audio/wall 0.9885, CPU 100%, and
the original CPU/runtime gates still FAIL. The 60-second HE-AACv2 regression
passes CPU, runtime and Stop recovery: mean/peak CPU 66.71/67.9%, audio/wall
1.00138, minimum heap/largest block 44,984/32,768 bytes. Its maximum WebUI
response is 140 ms. This short regression does not resolve the earlier
30-minute HE-AACv2 heap failure.

The 60-second 16-bit FLAC control also passes CPU, runtime and Stop recovery:
mean/peak CPU 67.16/68.0%, audio/wall 1.00161, decode-call/audio 24.05%, and
minimum heap/largest block 71,048/55,296 bytes. These are observed regression
results, not an isolated predictor benchmark or a long-stream qualification.

The follow-up measurements, frozen sources and disassembly are retained in
[`esp32c3-flac-unroll-20261006`](../tests/results/esp32c3-flac-unroll-20261006/manifest.json).
The earlier results below describe the preceding optimization and remain
unchanged. Large-frame memory failures and the long HE-AACv2 heap gate are
separate unresolved issues.

## Follow-up: move address calculations outside the sample loop

The next candidate, `esp32c3-flac-spans`, resolves the workspace segment,
destination pointer and end pointer once per contiguous span. The normal
sample loop then advances the destination pointer directly. Only the first
`activeCoefficients` samples of a new allocation use per-tap segment lookup;
their history can belong to the preceding allocation. The first span already
has its warm-up samples. The final span is capped by the actual frame length,
including partially allocated segments. No history is copied into a cache.

The shift is validated once against its legal 0..15 range. This adds a guard
against invalid direct calls; the compiler still lowers the signed 64-bit
shift generically, so the guard alone is not claimed as a speed improvement.
The coefficient count, trimming of trailing zero coefficients and group
offsets were already outside the sample loop in the previous RV32 code.
Products and sums depend on newly reconstructed samples and remain inside.

The retained RV32 disassembly confirms that the main sample loop has no
segment-number/offset calculation or segment-table load. The boundary prefix
retains checked indexing. Both candidates have a 64-byte predictor stack
frame and identical static RAM/IRAM/RTC sizes. The new app is 1,577,696 bytes,
**96 bytes larger** than the four-tap candidate.

The same **2,444 predictor comparisons and 375 full decoder comparisons** pass
again under ASan/UBSan with exact PCM. New negative tests reject shifts 16,
32, 64 and 255 before accessing or shifting sample values. The actual
segmented and contiguous implementations are exercised, including all
allocation boundaries and the partial final segment.

In the physical dense LPC32 run, decode-call time is **481.1 ms per audio
second**, audio/wall 0.98834, and CPU 100%. This is inside the preceding
four-tap candidate's 475.2..481.5 ms range: **no additional LPC32 speedup is
demonstrated by this experiment**. CPU and runtime gates still fail; Stop
recovery passes. The 60-second HE-AACv2 regression passes CPU/runtime/recovery
with mean/peak CPU 66.83/67.7%, audio/wall 1.00096 and minimum heap/largest
block 44,704/32,768 bytes. OTA while playing AAC passes in 21.47 seconds with
settings, playlist and Wi-Fi retained. This does not qualify the candidate
for production or replace long-stream testing.

The 16-bit FLAC control passes CPU/runtime/recovery: mean/peak CPU
66.78/67.8%, audio/wall 1.00150 and decode-call/audio 23.18%, versus 24.05%
in the preceding run (3.6% less elapsed decode-call time in this pair).
This small difference is not an isolated or repeated performance proof.
The span organization is retained for its explicit allocation boundaries;
no additional LPC32 acceleration is claimed.

Reports, exact sources and disassembly are retained in
[`esp32c3-flac-spans-20261006`](../tests/results/esp32c3-flac-spans-20261006/manifest.json).

## Exact rolling prediction for repeated coefficient runs

For order `N`, let the unshifted prediction be
`P(i) = sum(c[j] * x[i-1-j], j=0..N-1)`. For either `s=+1` or `s=-1`,
the identical next prediction is:

```text
P(i+1) = s*P(i) + c[0]*x[i]
         + sum((c[j] - s*c[j-1])*x[i-j], j=1..N-1)
         - s*c[N-1]*x[i-N]
```

Equal neighbouring coefficients cancel for `s=+1`; alternating coefficients
cancel for `s=-1`. The decoder counts these differences once per subframe and
uses the update only for order >= 8, at most four nonzero interior differences,
and at least a halving of the multiply count including the two endpoints.
Other coefficients retain the ordinary dot product. Matching/opposite
endpoint coefficients combine into one product of an added/subtracted sample
pair. Thus the alternating 32-tap fixture needs one product per subsequent
prediction, after its initial 32-product seed. This is a coefficient-dependent
optimization, **not a general removal of 31 LPC32 multiplications**.

The carried value is the full signed 64-bit sum. Rounding occurs only at the
original prediction shift when reconstructing each sample; no rounded PCM
prediction is fed back. Coefficients and warm-up positions are unchanged.
Endpoint arithmetic is 64-bit because two valid int32 samples can form a
33-bit sum/difference. With <=32 signed 15-bit coefficients and int32 history,
the original prediction is bounded in magnitude by 2^50; the update's
intermediate terms also fit signed 64-bit. The original final int32 check
still rejects overflowing reconstruction before storage.

The candidate `esp32c3-flac-rolling` uses no additional heap or static storage.
Its app size is 1,580,096 bytes (+2,400 from `esp32c3-flac-spans`). IRAM/DRAM/RTC
sizes remain identical. Its predictor stack frame is **112 bytes**, versus
64 before (+48 bytes within the existing task stack). Four delta coefficients
and four offsets occupy 20 bytes of local storage; no full history copy or
mutable coefficient cache is added.

Host tests pass **8,984 independent predictor comparisons** covering all
orders/shifts, equal and alternating coefficients, piecewise coefficient
runs, random coefficients and allocation boundaries. They also check 33-bit
endpoint sums and an overflow reached after the initial prediction.
**378 full decoder comparisons** match known PCM and FFmpeg: the prior
120-case matrix, four large-block files, and two long dense LPC32 files,
each through segmented/contiguous/adapter paths, under ASan/UBSan.

The new `--irregular-lpc` fixture has deterministic nonperiodic, nonzero
coefficients. It prevents the optimized alternating fixture from becoming
the only performance example. Its complete decoded PCM is checked too.

### Rolling-predictor board measurements

The rolling image was installed by native WebUI OTA while AAC played;
Wi-Fi, playlist and settings comparisons pass. Each load run lasts 60 seconds
with frequent WebUI polling and the existing 10-second timing warm-up.
The same DIO80/no-sleep/full-AAC configuration is used throughout.

| Input | Decode-call ms / audio second before | After | CPU mean / peak after | Audio / wall after | CPU gate / runtime gate |
| --- | ---: | ---: | ---: | ---: | --- |
| 24-bit LPC32, alternating equal-magnitude coefficients | 481.1 | 207.9 | 85.48 / 86.2% | 1.00154 | FAIL / PASS |
| 24-bit LPC32, nonperiodic coefficients | 465.6 | 485.7 | 100 / 100% | 0.94087 | FAIL / FAIL |
| 16-bit FLAC control | 231.8 | 229.6 | 67.19 / 68.5% | 1.00152 | PASS / PASS |

The alternating case uses **56.8% less elapsed decode-call time**, about
**2.31x throughput**, and restores real-time delivery in this observation.
Its peak CPU remains above the unchanged 85% acceptance threshold, so the
CPU gate is still FAIL. There are no captured runtime faults in that case.
Maximum WebUI times are 156/203/125 ms respectively; RSSI minima are -67 dBm.
All three Stop-recovery checks and final saved-station restoration pass.

The nonperiodic case has 31 nonzero differences for either sign and uses the
general dot product. Its control run gives audio/wall 0.95119; the candidate
gives 0.94087. Elapsed decode-call time is 4.3% higher in this pair. This
includes task interruptions and is not an isolated measurement of selector
overhead; **no absence of slowdown is claimed**. A preceding control capture
lost part of one CPU line and failed with `Incomplete CPU/heap evidence`;
both that failure and the complete repeated control are retained. General
high-order LPC performance remains unresolved. The short 16-bit control is
stable; it does not establish all-format or long-stream qualification.

The firmware remains **not production-qualified**. The earlier 8192-block
FLAC memory failures and long HE-AACv2 heap failure are not resolved by this
change. The latest image's AAC verification here is the OTA playback check;
the full 60-second HE-AACv2 load measurement above belongs to the span image.

Frozen sources, build identities, disassembly and all passing/failed results:
[`esp32c3-flac-rolling-20261006`](../tests/results/esp32c3-flac-rolling-20261006/manifest.json).
Replay with `python tests/test-flac-rolling-evidence.py`. Regenerate the
general LPC32 input with `generate_flac_depths.py --physical --irregular-lpc
--depth 24 --seconds 64 --output NEW_DIRECTORY`, then validate it with
`run_flac_depths.py --fixtures NEW_DIRECTORY --output NEW_HOST_RESULT` before
running the shared board load harness. Compare it alongside `--dense-lpc`;
testing only the coefficient pattern benefiting from the shortcut is insufficient.

## Host coverage for the earlier predictor

- 198 independent scalar-reference cases per storage mode: orders 0 through 32,
  both channels, dense/late-nonzero/all-zero coefficients, 8192 samples spanning
  every allocation boundary. All **396 cases pass ASan/UBSan**.
- **387 full decoder comparisons** pass: 120 depth/channel/predictor fixtures,
  four FFmpeg 24-bit/8192-frame files, and four new dense LPC32 tone files, each
  through segmented core, contiguous core and streaming adapter, plus the
  64-second dense-LPC load fixture through all three paths. Output matches
  both known signed-16 PCM and FFmpeg exactly.
- The 16-case truncated-input regression passes in both modes, including corrupt
  predictor overflow. Dense fixtures use 32 nonzero signed 15-bit coefficients;
  they prevent the sparse LPC fixture from being the only performance example.

## Build and physical evidence

The candidate is `firmware/development/esp32c3-flac-predictor/app.bin`, with the
exact same SDK configuration as the control `esp32c3-flac-depths`: no deep sleep,
DIO 80 MHz, full-rate PC19 AAC, experimental whole-block DMA output.

| Linked storage | Control | Candidate |
| --- | ---: | ---: |
| IRAM text | 43,354 B | 43,354 B |
| DRAM data | 12,620 B | 12,620 B |
| DRAM BSS | 29,464 B | 29,464 B |
| RTC data | 2,688 B | 2,688 B |
| App image | 1,576,432 B | 1,576,544 B |

No new heap allocation or persistent PCM workspace is introduced. OTA from the
control while AAC played passed in 21.44 seconds; Wi-Fi, playlist and settings
comparison passed. The candidate remains **not production-qualified**.

The 12-second runs contain two complete decoder profiling windows per AUTO/
explicit-codec mode. The ranges below show both runs. Elapsed decode-call time
includes interruption by other tasks; it is not the total CPU utilization.

| Stream | Decode-call time / audio before | After | Audio / wall before | After | Candidate runtime check |
| --- | ---: | ---: | ---: | ---: | --- |
| 20-bit sparse LPC32 | 74.88–75.63% | 18.72–19.61% | 0.915–0.916 | 1.003 | PASS in both runs |
| 24-bit sparse LPC32 | 72.23–73.19% | 20.24–20.70% | 0.847 | 1.003–1.004 | PASS in both runs |
| 24-bit dense LPC32 | 79.50–85.56% | 57.45–57.84% | 0.788–0.798 | 0.936–0.941 | **FAIL in both runs** |

All six candidate playback/EOF status checks, natural-EOF heap recovery and
Stop heap recovery pass. The combined runtime gate still fails because the
dense case saturates the CPU and emits register dumps. Its improvement does
not make it real-time, and no failed gate is promoted to PASS.

### Sustained 60-second WebUI-load checks

These use frequent status polling (target interval 100 ms), discard the original
first 10 seconds for CPU statistics, and retain all original gate results. They
are stricter than the short EOF observations above.

| Input | CPU mean / peak | Minimum heap / largest block | Audio / wall | Result |
| --- | ---: | ---: | ---: | --- |
| 16-bit FLAC control before | 69.43 / 70.3% | 69,184 / 55,296 B | 1.00154 | PASS |
| 16-bit FLAC candidate | 69.81 / 70.7% | 68,660 / 53,248 B | 1.00161 | PASS |
| 24-bit FFmpeg independent stereo, block 4608 | 88.62 / 89.1% | 61,832 / 47,104 B | 0.95347 | **FAIL: CPU budget** |
| 24-bit dense LPC32, block 1024 | 99.42 / 100% | 109,484 / 90,112 B | 0.87004 | **FAIL: CPU budget and runtime** |
| HE-AACv2, full 44.1 kHz stereo | 69.86 / 70.7% | 44,972 / 32,768 B | 1.00098 | PASS |

The 16-bit comparison shows no material timing change in this pair; it does not
prove a general speedup. All three candidate FLAC runs recover heap after Stop.
The dense case has ample free heap while saturating CPU. The 4608-block case has
no captured allocation/decoder/runtime fault but still fails the CPU threshold
and real-time audio ratio. Maximum WebUI times are 141 ms (16-bit), 141 ms
(24-bit FFmpeg), and 1250 ms (dense LPC32). The original 8192-block allocation
failures are a separate unresolved case; those files have only host PCM coverage
on this arithmetic candidate, not a repeat of their physical memory tests.

The HE-AACv2 regression also passes its runtime and Stop-recovery checks, with a
maximum HTTP response of 141 ms. Its 60-second duration does **not** resolve the
earlier [30-minute progressive-heap failure](ESP32C3_HEV2_SOAK_20261005.md) or
satisfy the one-hour acceptance requirement. AAC code and configuration are
unchanged; this is a regression check of the newly installed full-radio image.

Next timing experiments should profile/unroll the dense LPC dot product and
audit the 64-bit bitreader's RV32 cost, retaining exact PCM. For larger frames,
measure time waiting for encoded input and PCM queue space as well as decoder
execution; CPU averages alone do not attribute the observed audio shortfall.

The original dense-LPC control is retained: both EOF status checks pass, but
runtime health fails and CPU reaches 100%. Its two short profiling runs deliver
only 0.788/0.798 seconds of audio per wall-clock second. A correct status flag is
not proof of real-time playback. `summarize_terminal_cpu.py` keeps those original
verdicts and separately describes complete decoder timing records; short windows
cannot establish sustained load or acoustic continuity.

The separate large-block allocation failures remain unresolved by this arithmetic
optimization. They require reducing live encoded-frame/workspace/network memory,
then repeating the failed cases. HE-AACv2's progressive live-heap decline and the
one-hour multi-format/HTTPS requirements also remain open.

A concrete lossless FLAC memory experiment is to fuse residual reading and LPC
reconstruction for the second channel. Prediction needs at most 32 preceding
samples, not a second complete 8192-sample residual array. After reconstruction
and stereo decorrelation, a pair of final s16 output samples can occupy the
first channel's existing 32-bit slot. The maximum theoretical workspace saving
is 32,768 bytes minus the small predictor history; **this is not implemented or
measured saving**. Before changing it, audit allocation/reset, residual partition
warm-up, fixed/LPC reconstruction, wasted bits, all stereo assignments and output
chunking. Preserve 25-bit side values and 64-bit accumulation until final PCM
conversion, then compare every sample and fault/reopen behavior under sanitizers
and on the physical C3. Do not merely truncate residuals to fit smaller storage.

## Reproduction

```text
python tools/codec_benchmark/run_flac_bounds.py --output NEW_BOUNDS
python tools/codec_benchmark/run_flac_bounds.py --contiguous --output NEW_CONTIGUOUS
python tools/audio_test_server/generate_flac_depths.py --physical --dense-lpc --output NEW_DENSE_FIXTURES
python tools/codec_benchmark/run_flac_depths.py --fixtures NEW_DENSE_FIXTURES --output NEW_HOST_RESULT
python tools/esp32c3_tests/diagnostic.py terminal_memory --board http://BOARD_IP --host HOST_IP --serial-port COM_PORT --fixture-manifest NEW_DENSE_FIXTURES/manifest.json --case flac-24bit-stereo-lpc32dense --output NEW_BOARD_RESULT
python tools/esp32c3_tests/summarize_terminal_cpu.py --input NEW_BOARD_RESULT --output SUMMARY.json
python tests/test-flac-predictor-evidence.py
```

The [retained reports and source identities](../tests/results/esp32c3-flac-predictor-20261006/manifest.json)
include every original failed gate, the control image identity, host source
snapshots, actual board observations and exact firmware/config hashes. Large
fixtures are reproduced with the frozen generator and verified by recorded
encoded/source-PCM hashes. Firmware remains an unreleased development artifact.
