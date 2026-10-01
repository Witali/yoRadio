# HE-AAC RAM reduction: implementation and measurement plan

## Acceptance rules

Preserve the current decoder's formats, SBR, PS, channels and full output rates.
Layout-only changes must be bit-exact against the pinned Espressif decoder.
Lossy storage has a temporary development limit of ±5 signed-16 PCM LSB per
sample/channel; the final limit is ±2. Measure instruction demand separately
from physical CPU time. A slowdown must have an explicit optimization follow-up.

Count actual requested allocations and allocator/adapter overhead, including
peak live memory. Smaller payload in an unchanged allocation is not freed RAM.
Do not sum overlapping candidates. Keep failed trials and original controls.

## Execution sequence

1. **Baseline and harness.** Retain the 107508-byte decoder payload baseline
   (55128-byte SBR owner), native PCM controls, per-allocation guards and timing.
   Reuse the six synthetic files and five unchanged radio captures.
2. **Lossless PS state relocation.** Audit every PS-control access and mode
   transition. Test moving the 3536-byte embedded PS control into right-channel
   storage that is unused while PS is active, retaining only a small inactive
   sentinel. Reduce the actual allocator request and account for adapter state.
   Reject any alias that remains live. This is a candidate, not an assumed gain.
3. **Lifecycle and failure tests.** Exercise late PS, LC/HE/v2 and rate/channel
   changes, close/reopen, reset and allocation failures. Check allocation guards,
   cleanup and PCM against controls; explicitly distinguish native decoder bugs
   from new failures. Preserve supported formats rather than skipping failing ones.
4. **Compact PS storage and speed.** Combine the already tested packed-write
   strategy only where it yields additional allocation reduction. Measure each
   step against lossless storage. Replace slow exponent searches with an exact
   bounded implementation, and check bit equivalence and PCM before accepting.
   If packing has no net RAM benefit in the chosen layout, retain lossless storage.
5. **Other layout candidates.** Audit smoothing pointer tables (1888-byte
   estimate), shared low-band workspace (6144-byte estimate), and smoothing
   history (2048-byte estimate) against the remaining binary ABI. Implement
   candidates whose entire access/lifetime set can be changed consistently;
   record a concrete dependency for those requiring a larger source replacement.
6. **Integration and report.** Save reproducible options, raw results and a
   before/after table for RAM, maximum/RMS PCM error, formats and instruction
   overhead. Enable a production option only after its lifecycle checks pass.
   Run full-radio hardware acceptance when a qualified build and board are
   available; QEMU alone is not production heap/CPU/OTA qualification.

## Starting evidence

- [Allocation audit](ESP32C3_AAC_DECOMPILATION_RAM_20260930.md): decoder payload
  107508 bytes with SBR, excluding registration, caller buffers and allocator cost.
- [Actual packed PS writes](ESP32C3_AAC_PS_WRITE_PORT_20261001.md): 617 pairs,
  2468 bytes less delay payload, **zero heap saving**, maximum 3 LSB, and
  +26.681% / +40.658% QEMU instructions on synthetic HEv2 / ABBA.
- [Broader backlog](ESP32C3_MEMORY_STABILITY_TODO.md): full-radio HE/v2 currently
  lacks enough contiguous heap. The 22 kHz fallback is not an accepted solution.

## Progress

1. Full AAC archive inventory/decompilation is complete: 144 members, 186
   functions, zero export failures. This includes unreferenced and optimized
   filter-bank functions. Pseudocode is an audit aid, not original C source.
2. [Lossless PS relocation](ESP32C3_AAC_SBR_LAYOUT_20261001.md) is implemented
   in a guarded QEMU build: requested SBR size 55128 → 51596 B; measured block
   size 55296 → 53248 B (2048 B saved). Test state totals 144 B. All 81 paired
   comparisons are bit-exact; extra guest instructions are 0.010–0.017% for SBR.
3. Close/reopen, 21 format segments and two allocation failures pass paired
   checks. [Direct reset is reproduced and repaired](ESP32C3_AAC_RESET_20261001.md):
   six contained vendor writes beyond the core, 24 reset calls, 887808 subsequent
   PCM samples identical with the source repair and relocated PS owner.
4. Packed PS writes are not combined with this layout: their holes do not shrink
   the full-stereo channel allocation and do not extend the free region needed
   for PS control. They add quantization and measured work without an additional
   heap saving here. Keep the lossless implementation; retain packed writes as
   a separate measured experiment for a future fully variable owner layout.
5. Smoothing pointer tables are the next lossless candidate. The decompilation
   shows five initialized entries in four 64-entry tables per channel, giving
   1888 B of potential payload reduction. All absolute offsets and the channel
   stride must change consistently before requesting a smaller allocation.
6. No production option is enabled yet. Remaining lifetime and hardware gates
   are listed in the relocation report; the full-radio memory shortage is not
   claimed fixed by a QEMU block-size measurement.

## Updated product objective

The user's objective is reliable radio playback across the existing codec
families, AAC first, without crashes or allocation failures. Prioritize full-radio
allocation ownership/reservation, peak RAM and physical playback acceptance over
additional representation studies. Keep the existing AAC quality/rate constraints
and test MP3, FLAC, Vorbis and Opus when changing shared memory or task resources.

The [full-radio RAM profile experiment](ESP32C3_AAC_RADIO_RAM_20261001.md) now
passes initial physical LC/HE/v2 playback at full rates. Early SBR reservation
was counterproductive; ordinary allocation order with smaller service stacks
and Wi-Fi pools succeeds. All-codec, stack, CPU, HTTPS and OTA qualification
remain open before changing defaults.

The subsequent broad matrix fails HE after station changes. Six dynamic Wi-Fi
buffers pass the initial finite/continuous tests but remain experimental.
[Early 12 KiB scratch placement](ESP32C3_AAC_SCRATCH_PLACEMENT_20261001.md)
is bit-exact in QEMU and passes ownership tests, but its physical switching
test still fails the 55128-byte owner with a 53248-byte largest block. Keep it
off alone. The lossless 51596-byte PS-relocated owner is now integrated into a
per-decoder context. Its physical switching trial still fails all six HE/v2
starts: the largest block is 43008 B in that image. Allocation geometry changed,
so the earlier 53248-byte observation did not guarantee combined success.

At the user's request, [16+16 with grouped exponents](ESP32C3_AAC_PC16_WRITES_20261001.md)
is also implemented as a separate, optional PS-write experiment. It passes
81 paired development checks (maximum 3 LSB), shrinks delay payload by 2156 B,
but frees no additional heap in the fixed owner and increases guest work.
Do not enable it by default or count it as the full-radio memory fix. Next
measure a small cache of reconstructed values against this exact baseline,
then pursue a layout that can actually release the unused owner bytes.
