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

Implementation started. Each completed experiment will be recorded below with
measured gains, quality, overhead and remaining limits.
