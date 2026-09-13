# Opus ASM: physical ABBA, 2026-09-13

## Acceptance target

User target: Opus192kbps must fit within70% decoder CPU on ESP8266 at160MHz,
with lower RAM use and unchanged decoded PCM. This is decoder task time per
audio duration, not a70% wall-time ratio or fewer assembly source lines.
Measure network, normalization/PDM and idle separately; actual radio must
also play continuously for>=20s with no new DMA underruns. Target NOT met.

## Entropy-update experiment

Completed five ABBA cycles:10 full raw runs of GCC assembly (A),10 of
ec_dec_update-v1 (B). Only the entropy function implementation differed.
Eleven application-only OTA operations; no UART, adapter, partition or
SPIFFS changes. Both artifacts source51e32a8, CPU160/QIO40, scratch6144B,
word/ICDF/FIR optimizations, fixture hashes and all remaining settings matched.

Each run: own tone/noise packets loaded from flash to RAM,120 packets and
115200 mono48k samples per fixture, correct reference hashes in every run.
No audio network, Ogg, normalization or PDM. Wi-Fi/WebUI remain enabled.
Task counters exclude other tasks but include charged ISR/instrumentation;
wall timings include preemption. No slow/error attempts were discarded.

| Fixture | A CPU median | B CPU median | Relative time saving |
|---|---:|---:|---:|
| SILK mono12 |22.789%|23.343%|−2.428%|
| Hybrid mono24 |54.822%|55.432%|−1.113%|
| CELT stereo64→mono |65.785%|65.957%|−0.263%|
| CELT stereo128→mono |80.962%|80.035%|+1.146%|
| CELT stereo192→mono |93.481%|93.300%|+0.194%|

The192 improvement is tiny, with regressions elsewhere. Do not promote B
as a general speed optimization. Keep it as an independently selectable
experiment; the new loop-hoisting experiment starts from A, not B.
Reaching70% from A requires about25.12% less decode task time.

All PCM hashes, packet/sample counts and scratch peaks match. Decoder state
6582B; allocated DRAM scratch6144B; observed scratch peaks1808/2904/5488/
5488/5488B; IRAM arena16384B, peak up to15600B. Main audio stack5120B,
minimum observed free watermark1660B. This experiment adds no static RAM
and does not reduce either allocation or task-stack size.

There were no HTTP observation errors. However A reached3288B sampled free
DRAM in one192 case, below the live4096B reserve target. Its minimum DRAM
after cleanup was19788B vs usual~26KiB. B sampled minimum7816B overall.
Identical static sections do not make these dynamic differences evidence
of memory savings or leak freedom. Raw benchmark startup checks2048B;
the live decoder guard remains4096B. These runs do NOT qualify live RAM safety.

Maximum single decode wall calls at192:74.138ms A,81.254ms B, including
preemption. Average CPU alone therefore cannot guarantee DMA deadlines.
No analog audio recording or live continuity claim is made for this series.

[Complete raw reports, logs, OTA provenance and comparison](../firmware/development/esp8266-opus-asm-library/board-abba-20260913/raw/comparison.json).

## Next isolated candidate: invariant SAR

`hoisted-asm` moves the unchanged right-shift setup before loops in
alg_unquant and renormalise_vector. Every multiplication, rounding, load/store
and resulting register/SAR value is preserved; no calls or other SAR writes
occur inside these loops. SDK context save/restore preserves SAR across IRQs.
No new register spills, arrays, heap or task. Baseline remains unchanged.

10000 executable snippet-model cases compare all registers, complete memory
and SAR. Guards reject external loop entries, calls, shift changes and
mutation of the invariant. LF/CRLF preservation is explicitly tested after
the first generator draft failed this test; that draft was never flashed.
All9 local tests pass. This is semantics evidence, NOT physical speed proof.

Target object alg_unquant806→806B; renormalise_vector181→184B because GAS
changes density/padding around the moved loop. All other functions, data and
relocations are identical. Stack112/32B unchanged. The possible benefit is
one fewer executed SAR write per later iteration, not smaller flash.

Whole-library inventory covers229 functions/114 names linked in the control
ELF. Static instruction/load/SAR/stack counts are a search index, not measured
hotness or attribution of every narrow load to flash. Focus further analysis
on quant_all_bands, quant_partition, alg_unquant, transforms and SILK decode
using actual stage profiles. [Inventory](../firmware/development/esp8266-opus-hoisted-asm-library/algorithm-inventory.json).

- [x] Exact snippet semantics and target build/section inspection.
- [x] Full physical PCM/hash test and matched10+10 CPU measurements (negative result below).
- [ ] Further loop-invariant experiments where profiles show material cost.
- [ ]192kbps <=70% decoder CPU, RAM safety and continuous real-radio output.

### Physical result: invariant SAR is not a speed improvement

Five matched ABBA cycles, 10 runs per variant, source ab2b244, with no
discarded attempts. All five fixture PCM hashes and counts match exactly.

| Fixture | GCC ASM CPU median | Hoisted SAR CPU median |
|---|---:|---:|
| mono12 |22.774%|22.813%|
| mono24 |54.818%|54.662%|
| stereo64 -> mono |65.838%|65.779%|
| stereo128 -> mono |80.957%|81.602%|
| stereo192 -> mono |93.449%|94.833%|

At192 the change is **1.481% slower**, not faster. Keep it diagnostic-only;
do not change the default backend. Moving fewer source instructions is not
proof of a faster linked program. Both apps are902992B and have identical
static RAM sections; no RAM saving was achieved. The lowest sampled free
DRAM was868B (control) /688B (candidate). These samples are below the live
4096B reserve and do not qualify safe live playback. Post-cleanup minimum
DRAM17220/17216B; no observation errors. Do not discard low-memory trials.

[All20 raw trials, OTA reports and matched comparison](../firmware/development/esp8266-opus-hoisted-asm-library/board-abba-20260913/raw/comparison.json).

## CELT/PVQ stage8 profile

Ten additional raw runs of the C stage8 diagnostic build all match the PCM
reference. At192kbps, `quant_all_bands` and its callees account for a median
**61.884% of decode wall time** (range61.419..62.526%). This is inclusive
wall time with preemption, not exclusive function CPU. The separate
instrumented build measured90.072% median decoder CPU; it is not a matched
speed comparison with the ASM builds above. The stage8 median share is
48.525% at64kbps and56.519% at128kbps.

Minimum sampled DRAM2632B, and several mono12 task/wall timing-window
inconsistencies are retained in the report. Neither a clean hash nor the
diagnostic runner's `passed` flag certifies CPU deadlines or RAM safety.
The next isolated experiment tests placement of two small PVQ functions in
unused IRAM, without changing arithmetic, DRAM buffers or the16KiB arena.
Poll benchmark status less frequently in both arms to reduce observer load;
do not compare those measurements as a matched test against this series.

[Stage8 summary and all10 retained trials](../firmware/development/esp8266-opus-stage8-192-20260913/board-20260913/summary.json).
