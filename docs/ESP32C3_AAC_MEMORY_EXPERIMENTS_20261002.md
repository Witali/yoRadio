# HE AAC memory compression experiments

This is the working checklist for reducing ESP32-C3 AAC memory while preserving
AAC-LC, SBR, PS, output rates and channels. Each experiment records storage bytes,
actual allocation savings, maximum and RMS signed-16 PCM error, and decoding
work. A smaller representation inside an unchanged allocation saves **zero heap**.
Layout changes must be bit-exact. Lossy experiments use the temporary maximum
error limit of 5 LSB per sample/channel; the final limit remains 2 LSB.

## Memory areas and execution order

Sizes describe the original stereo allocation unless stated otherwise. PS
overlays the right channel: estimates overlap and must not be added together.

| Order | Area | Current bytes | Experiment | Status |
| --- | --- | ---: | --- | --- |
| 1 | PS decorrelation delays, 617 complex pairs | 4936 native; 2780 PC16 | Keep 32-bit mantissa words; put the two extra mantissa bits with the exponent, five six-bit entries per metadata word; compare four byte entries and separate component exponents | Pending |
| 2 | Low-band QMF matrices, two channels | 20480 | Separate retained history from current work; evaluate shared workspace and compact complex history independently | Pending |
| 3 | High-band QMF history, two channels | 4608 | Compare compact history independently from low-band history | Pending |
| 4 | Gain/noise smoothing matrices | 10240 | Audit four retained rows plus current scratch instead of copying a fifth row; preserve all five filter taps | Pending |
| 5 | Smoothing exponents, included above | 5120 | Observe/check int16 range, preserving int32 arithmetic; candidate saving 2560 bytes with five rows | Pending |
| 6 | Right channel in PS mode | 24848 with compact pointer tables | Separate PS-specific allocation and preserve all transitions; recompute overlaps with relocated PS control | Pending |
| 7 | Hybrid-filter history | 288 | Isolate its quantization effect; distinguish frame-boundary probe from actual within-frame writes | Pending |
| 8 | Core IMDCT overlap, two channels | 8192 | Examine ranges and persistent-history packing, including short/long windows | Pending |
| 9 | Synthesis history, two channels | 4608 | Already int16; prioritize ring/lifetime changes over blind narrowing | Pending |
| 10 | Shared transform and SBR scratch | 12288 | Map all phase lifetimes; PS accesses reach the allocation end, so no unconditional halving | Pending |
| 11 | IID/ICC, harmonic flags and other bounded control fields | Distributed | Audit every reader/writer, then range-check narrower exact storage | Pending |

The existing lossless table compaction saves 1888 requested bytes; PS relocation
saves 3532 requested bytes. Their combined prototype requests 49708 rather than
55128 bytes. Its production integration is unfinished in the separate
`codex/esp32c3-stream-format` worktree; this experiment branch does not copy or
silently promote that unfinished adapter.

## Packing preference

Keep ordinary aligned 32-bit words containing the low 16 bits of Re and Im.
For the 17-bit experiment, a metadata entry contains a four-bit shift plus one
additional bit for each component. Five six-bit entries fit in one word without
cross-word accesses. Four byte entries are an alternative with simpler indexing.
These are 17-bit **mantissas**, not 17-bit exponents. The user's initial complexity
concern is addressed by measuring both layouts rather than densely interleaving
17-bit values across word boundaries.

| PS representation | Bytes for 617 pairs, including word rounding | Difference from current PC16 |
| --- | ---: | ---: |
| Original int32 Re and Im | 4936 | +2156 |
| PC16, eight exponent nibbles per word | 2780 | 0 |
| PC17, five six-bit metadata entries per word | 2964 | +184 |
| PC17, four byte metadata entries per word | 3088 | +308 |
| PC16, separate Re and Im exponent nibbles | 3088 | +308 |

## Required procedure for each area

1. Identify every initializer, reader, writer, reset/free path and storage alias
   using the checked RV32 layouts and complete native function inventory.
2. Name verified constants and fields. Preserve unknown values as explicitly
   unresolved; do not manufacture semantics from decompiler output.
3. Check quantizer arithmetic, overflow, rounding, metadata neighbours and tails
   against an independent wide-integer oracle. Check block/scalar equivalence.
4. Compare separate original/candidate decoders with identical inputs. Keep
   bypass and lossless controls, full output shape, error histograms and actual
   path-coverage counters. Test six synthetic fixtures and five retained ADTS
   recordings; label inactive paths rather than counting them as quality passes.
5. Distinguish frame-boundary accuracy probes from actual compact writes and
   from a smaller owner allocation. Do not present one as another.
6. Retain failed trials as well as passing ones. Report QEMU guest instructions
   separately from physical CPU/cache measurements. A slowdown needs follow-up.
7. Before enabling a firmware option, verify real allocation reduction, lifetime,
   failure cleanup, transitions, reset, malformed inputs, full-radio heap, CPU
   and OTA. No automatic production promotion follows a short corpus test.

## Evidence

Starting points: [existing execution plan](ESP32C3_HE_AAC_RAM_EXECUTION_20261001.md),
[native memory audit](ESP32C3_AAC_DECOMPILATION_RAM_20260930.md),
[PC16 actual writes](ESP32C3_AAC_PC16_WRITES_20261001.md), and
[checked symbolic structures](audits/esp32c3-aac-core-symbolic-20261001/README.md).
New experiment results and their exact source/configuration hashes will be
linked here as each stage completes. Pending entries are not measured savings.
