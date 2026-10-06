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

## Host coverage

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
