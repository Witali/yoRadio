# HE AAC memory compression experiments

This is the working checklist for reducing ESP32-C3 AAC memory while preserving
AAC-LC, SBR, PS, output rates and channels. Each experiment records storage bytes,
actual allocation savings, maximum and RMS signed-16 PCM error, and decoding
work. A smaller representation inside an unchanged allocation saves **zero heap**.
Layout changes must be bit-exact. Lossy experiments use the temporary maximum
error limit of 5 LSB per sample/channel; the production limit is now 3 LSB. See [current policy](ESP32C3_AAC_PRECISION_POLICY.md).

## Memory areas and execution order

The [combined follow-up](ESP32C3_AAC_COMBINED_STORAGE_20261002.md) tests cumulative
error, rather than adding the isolated verdicts. Its mixed full combination
reaches at most 3 LSB on the retained corpus, with an estimated 21,096-byte
persistent SBR saving after PS/SBR overlap. This is not yet a measured combined
heap saving. The all-16-bit combination fails at 10 LSB.

Sizes describe the original stereo allocation unless stated otherwise. PS
overlays the right channel: estimates overlap and must not be added together.

| Order | Area | Current bytes | Experiment | Status |
| --- | --- | ---: | --- | --- |
| 1 | PS decorrelation delays, 617 complex pairs | 4936 native; 2780 PC16 | Shared/independent component exponents and high mantissa bits in metadata | Five actual-write variants tested, including 18+18: max 3 LSB, zero saturation, unchanged heap; owner integration pending |
| 2 | Low-band QMF matrices, two channels | 20480 | Lifetime split first; independent/shared exponent layouts remain alternatives | [Scoped low-QMF](ESP32C3_AAC_LOW_QMF_WORKSPACE_20261003.md) saves 10240 actual owner-block bytes with exact PCM. [Physical adapter](ESP32C3_AAC_LOW_QMF_PRODUCTION_20261003.md) uses the existing 16 KiB stack; full-radio qualification is still in progress |
| 3 | High-band QMF history, two channels | 4608 | Actual compact owner, including real-only and complex SBR | [Persistent PC18/PC16 follow-up](ESP32C3_AAC_HIGH_HISTORY_20261003.md): owner block 55,296 -> 49,152 B; 2,048 B additional block saving. PC18 max 2 LSB. [Production adapter](ESP32C3_AAC_HIGH_ADAPTER_20261003.md) integrated; QEMU concurrency/reset/failure gates pass; physical qualification tracked there |
| 4 | Gain/noise smoothing matrices | 10240 | Four retained rows plus a temporary fifth; preserve all five filter taps | [Actual four-row owner](ESP32C3_AAC_SMOOTHING_HISTORY_20261003.md): another 2048 B owner-block saving; 144 direct FIR cases bit-exact; combined PC18 corpus max 2 LSB. Adds 1024 B temporary payload / 1184 B compiled wrapper frame. [Physical adapter](ESP32C3_AAC_SMOOTHING_ADAPTER_20261003.md): local 14/14 passes, but public HE HTTP/HTTPS allocation failures remain |
| 5 | Smoothing exponents, included above | 5120 | Observe/check int16 range, preserving int32 arithmetic; candidate saving 2560 bytes with five rows | Checked int16 roundtrip bit-exact, observed -50..16; format-wide bound and compact allocation pending |
| 6 | Right channel in PS mode | 24848 with compact pointer tables | Separate PS-specific allocation and preserve all transitions; recompute overlaps with relocated PS control | Pending |
| 7 | Hybrid-filter history | 288 | Isolate its quantization effect; distinguish frame-boundary probe from actual within-frame writes | PC18 frame-history: max 3 LSB, potential saving 108 bytes; heap unchanged |
| 8 | Core IMDCT overlap, two channels | 8192 | Examine ranges and persistent-history packing, including short/long windows | PC18 rejected: synthetic HE error up to 2838 LSB despite <=5 LSB on real captures; both transforms/all four window sequences tested |
| 9 | Synthesis history, two channels | 4608 | Already int16; prioritize ring/lifetime changes over blind narrowing | Pending |
| 10 | Shared transform and SBR scratch | 12288 | Map all phase lifetimes; PS accesses reach the allocation end, so no unconditional halving | Pending |
| 11 | IID/ICC, harmonic flags and other bounded control fields | Distributed | Audit every reader/writer, then range-check narrower exact storage | Pending |

The [other-array report](ESP32C3_AAC_OTHER_ARRAYS_20261002.md) records 330 paired
comparisons for eight isolated areas, including previous PS mixing coefficients,
hybrid analysis output and PS energy histories. It distinguishes frame-boundary
probes from within-frame producers and lists remaining scratch/control exclusions.

The existing lossless table compaction saves 1888 requested bytes; PS relocation
saves 3532 requested bytes. Their combined prototype requests 49708 rather than
55128 bytes. The [production adapter experiment](ESP32C3_AAC_COMPACT_OWNER_20261002.md)
is integrated into this branch, with retained failed physical HE-AAC/network
qualification. The new high-history production adapter builds on that layout.
Its QEMU ownership tests pass; physical CPU, streaming and OTA results are
tracked in the adapter report before considering a production default.

## Next allocation experiment after physical four-row testing

Prioritize low-QMF storage, and compare a lifetime split before introducing more
quantization. The native initializer sets 40 rows, 32 new columns, write offset
8 and read offset 2. At the end of `sbr_dec`, eight trailing rows are copied to
the beginning for the next call. A candidate can retain those rows and provide
the complete native matrix only for the duration of decoding.

The [actual lifetime probe](ESP32C3_AAC_LOW_QMF_LIFETIME_20261003.md) now passes:
poisoning rows 8..39 preserves all control PCM and five capture hashes/counts.
Poisoning retained row 7 instead fails precision as expected. This confirms the
next allocation experiment on this corpus. The subsequent scoped-workspace
implementation now shrinks the actual owner from 45932 to 35900 bytes (10240
allocator bytes saved). It preserves the right PS overlay and exact PCM, with
2824 bytes of measured remaining physical decoder stack in the controlled AAC
tests. Public-network acceptance is tracked in the physical adapter report.

Before changing allocation, audit all row readers and PS aliases again:
`sbr_dec` analysis/generation/synthesis/copy paths, `init_sbr_dec`, both reset
modes, `sbr_open`, and `ps_allocate_decoder`. The right channel's apparent QMF
area holds PS controls/delays and must not be discarded. A full temporary
complex matrix costs 10,240 bytes before the decoder's other stack frames;
the measured free stack is only a feasibility hint, not qualification. Preserve
inactive imaginary history in real-only mode, task isolation and every pointer
lifetime. Require exact PCM against the existing adapter, the pointer audit,
measured allocation reduction and physical radio tests before promotion.

## Packing preference

The [FAAD Q14 audit](FAAD2_Q14_APPLICABILITY_20261003.md) distinguishes
14 fractional bits in unchanged int32 arithmetic from compact 14-bit mantissa
storage. A binary-point change alone saves no RAM. Continue per-area packing
and combined PCM qualification; no global Q14 arithmetic rewrite is selected.

The initial QMF experiment uses independent four-bit Re and Im exponents:
one 32-bit metadata word for four complex pairs, with a separate 32-bit mantissa
word per pair. This needs 12,800 bytes of row-aligned stereo payload instead of
20,480 bytes (37.5% less), before workspace and PS aliasing are accounted for.
The experiment currently saves zero allocated heap. See
[QMF and PS measurements](ESP32C3_AAC_QMF_STORAGE_20261002.md) for quality, work,
the consumer audit and exact scope. Shared 17-bit variants remain comparison
candidates rather than an assumed default.

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
| PC18, shared exponent and two extra bits per component | 3088 | +308 |

The [18-bit follow-up](ESP32C3_AAC_STORAGE18_20261002.md) uses the full metadata
byte: four shift bits plus two high/sign bits for each mantissa. It lowers RMS
error at the same payload as separate 16-bit exponents. It meets the current
3-LSB precision gate on this corpus; actual allocation reduction and speed
qualification remain open.

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

The [pointer ownership audit](ESP32C3_AAC_POINTER_AUDIT_20261003.md) records
exact targets and lifetimes for the PC18 + four-row smoothing adapter,
including PS overlays and scoped stack rows. Retain these checks when changing
an area's size or layout. Its address results do not replace PCM comparisons
or physical radio qualification.

Starting points: [existing execution plan](ESP32C3_HE_AAC_RAM_EXECUTION_20261001.md),
[native memory audit](ESP32C3_AAC_DECOMPILATION_RAM_20260930.md),
[PC16 actual writes](ESP32C3_AAC_PC16_WRITES_20261001.md), and
[checked symbolic structures](audits/esp32c3-aac-core-symbolic-20261001/README.md).
The first batch is saved in [the storage experiment report](ESP32C3_AAC_QMF_STORAGE_20261002.md)
and [raw evidence](../tests/results/esp32c3-aac-storage-20261002/), including exact
source/configuration hashes. Pending entries are not measured savings.
