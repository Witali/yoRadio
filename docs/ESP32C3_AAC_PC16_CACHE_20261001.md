# Small cache for reconstructed PC16 complex values

**Current policy (2026-10-02): production permits +/-3 PCM LSB; development permits +/-5.**
The older acceptance statements below describe the limits at measurement time.
Measured errors and archived evidence are unchanged. See [current precision policy](ESP32C3_AAC_PRECISION_POLICY.md).

## Result and selection

Implemented `CONFIG_YORADIO_AAC_PS_PC16_CACHE`, **default off**. It requires
the experimental PC16 PS option or its paired QEMU test. Add
`sdkconfig.aac-pc16-cache.defaults` after the existing PC16 defaults to enable it.

The cache preserves decoded values, but this version **increases instruction
work by 12.3–13.6% over PC16 without caching**. It is retained as a measured
opt-in experiment, not enabled in the default profile or installed on the board.
The [PC16 storage report](ESP32C3_AAC_PC16_WRITES_20261001.md) remains the baseline.

## Design and memory

Four cache lines each hold eight reconstructed complex pairs. Line 0 serves
main/sub-QMF delays, and lines 1–3 serve their corresponding all-pass links.
Every sample index has a stable line owner within a decorrelation call, even
when adjacent packed words are prefetched by different lines.

- State is **288 bytes on the existing decoder stack**; there is no heap
  allocation or shared global cache.
- It starts empty for each PS decorrelation call, so another decoder, owner
  reuse, format change or close/reopen cannot inherit cached values.
- Writes immediately update packed storage and invalidate that sample in its
  owning line. A subsequent read uses the reconstructed, rounded value;
  pre-rounding values cannot bypass quantization through the cache.
- Fills decode up to eight existing samples from one exponent word. The final
  partial group is bounded, with no padded input or speculative overread.
- RV32 disassembly shows `aac_ps_pc16_decode`'s own stack frame growing from
  **128 to 448 bytes (+320 B)** in builds without paired-test counters.
  This includes compiler temporaries/alignment, but excludes callers/callees.
  The already allocated task stack is unchanged; do not count the cache as
  an additional heap allocation or as extra codec-memory saving.

## Measurements

| Active PS input | Hit rate | PC16 work over binary | PC16 + cache work over binary | Cache cost over PC16 | PCM maximum against binary |
| --- | ---: | ---: | ---: | ---: | ---: |
| Synthetic HEv2 44.1 kHz | 68.299% | +32.387% | +50.359% | **+13.575%** | 2 LSB |
| ABBA 64 kbps | 70.096% | +42.733% | +60.266% | **+12.284%** | 3 LSB |

These are median QEMU guest instruction counts from paired runs 2/3, including
wrappers, assertions and counters. They are not physical CPU percentages or
cache-corrected timing. A hit includes a value prefetched during another miss,
so the hit rate alone does not demonstrate avoided work. The decoder touches
many delay indices only once per call; prefetched neighbors may go unused, and
tag/valid-bit handling adds work. This explains why this cache can be slower
despite a high hit rate.

Acceptance is deliberately unchanged: ±5 LSB during development, ±2 finally.
The cache's **45 paired comparisons** retain the same error counts as uncached
PC16. ABBA has 178 samples beyond ±2 out of 2646016, maximum 3; no sample exceeds
±5. Native-source and binary controls remain exact. Saturation counts are zero.

The production-hook integration test compares every byte of the post-conversion
PCM to the retained uncached-PC16 output: **328770 stereo frames, 0 LSB change**.
Its PCM SHA-256 is
`66484d0f5d3b813335db9f5ebc9ebf426de871bf6ff131b2afbf824d902aadfe`.
The known unchanged-header implicit-SBR limitation is still recorded; this is
not exhaustive format or lifecycle conformance.

Host ASan/UBSan testing checks **2026654 reads**, including immediate rereads,
write invalidation, independent stream ownership, fresh owners and lengths
1..17, 617 and 1029. All reconstructed values match direct PC16 unpacking.

[Raw logs, configurations, fingerprints and comparison table](../tests/results/esp32c3-aac-pc16-cache-20261001/).

## Reproduce

Use the paired PC16 defaults plus `sdkconfig.aac-pc16-cache.defaults`, with
build directory `build-qemu-aac-pc16-cache`. Run
`tools/codec_benchmark/run_aac_pc16_cache.py` with `--dependency-root`, `--qemu`,
`--bios`, `--wsl`, `--output`, and optionally `--input recording.aac`.
Run `tests/run-aac-pc16-cache.py` with a host C compiler/ASan/UBSan, and
`tests/test-aac-pc16-cache.py` to verify saved evidence and strict parsing.

For byte-exact integration comparison, use the production-hook QEMU defaults
from the PC16 report plus the cache defaults. Run `run_aac_scratch.py` with
`--build` for that image and `--reference-wav` for uncached PC16 output.
The saved configuration must contain `CONFIG_YORADIO_AAC_PS_PC16_CACHE=y`.

The next speed experiment should target packing and exponent handling or a
history region with genuine temporal reuse. Do not make this cache larger or
enable it by default merely to increase its hit rate.
