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

Before reducing any allocation or array, record every function that allocates,
initializes, reads, writes, resets or frees it, including indirect pointer users
and overlapping storage. Verify index bounds and lifetime across frames and
format changes against native instructions. Change the size only after this
access map is complete and all affected callers can be updated consistently.
Use the checked types in `aac_sbr_abi.h` for fields and allocation sizes;
derive machine-code replacement offsets from the compiler layout object.
Keep numeric private-ABI expectations at the checked binary boundary.

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
5. [Compact smoothing pointer tables](ESP32C3_AAC_SMOOTHING_TABLES_20261001.md)
   now run in a guarded QEMU experiment. Standard and function-access audit confirm
   five time entries per table; all `[5][64]` data matrices remain. Seven native
   functions have consistent new offsets/strides. Payload falls by 1888 B; an
   unguarded allocator probe saves 2048 B (guarded block saving is zero due to bin
   rounding). All 81 paired comparisons (24 candidate and 57 control runs),
   explicit smoothing-mode tests, complete
   initialization/pointer comparison and lifecycle checks pass. Production reset,
   malformed-input and hardware gates remain; this is not enabled in the radio.
6. No production option is enabled yet. Remaining lifetime and hardware gates
   are listed in the relocation report; the full-radio memory shortage is not
   claimed fixed by a QEMU block-size measurement.
7. [Typed ABI access](ESP32C3_AAC_ABI_20261001.md) replaces raw field offsets in
   smoothing, PS relocation/PC16 and repaired reset. Compiler-derived patches
   reproduce the seven earlier objects exactly. Reset, PCM, ownership and host
   sanitizer checks pass. This adds no RAM saving; full-radio integration and
   the remaining QMF/hybrid/synthesis/IMDCT candidates still need qualification.

## Updated product objective

The [IRAM placement audit](ESP32C3_IRAM_REDUCTION_20261001.md) adds a separate
full-radio candidate: 23392 B more DRAM capacity using supported SDK placement
options and Flash Auto Suspend on XMC-D. This changes neither AAC representation
nor its owner allocation. Qualification and limitations are recorded there;
it does not promote the codec compression or global production defaults.

The [Wi-Fi buffer balance follow-up](ESP32C3_WIFI_BUFFER_BALANCE_20261001.md)
tests spending some of this headroom on dynamic RX/TX limits of 16. Keep full
AAC/SBR/PS and validate the other codec families under HTTP load; smaller Wi-Fi
limits must not be accepted merely because a short AAC test uses less heap.
The follow-up passed 21 mixed-codec switches and full-rate AAC load checks, but
later reproduced an `Illegal instruction` panic during OTA in the Auto Suspend
profile. Do not promote it. Recovery/startup verification and a conservative
IRAM placement trial take priority; MP3 heap trend and Opus CPU margin remain
open as well.

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
Do not enable it by default or count it as the full-radio memory fix. The
[288-byte reconstructed-value cache](ESP32C3_AAC_PC16_CACHE_20261001.md) is now
implemented and checked: PCM is unchanged, but work increases by 12.3–13.6%
over PC16. Keep it off. Physical PC16 passes short continuous AAC streams but
still fails four of twelve switches. Continue with packing-speed work and a
layout that can actually release the unused owner bytes; neither experiment
has achieved reliable full-radio HE playback yet.

The [dynamic TLS-buffer trial](ESP32C3_TLS_DYNAMIC_20261001.md) keeps full
16 KiB RX / 4 KiB TX capacity and certificate verification, while improving
observed LC/MP3 HTTPS free RAM by about 18–21 KiB. Public HE/v2 still fail
their 55128-byte allocation, with largest blocks of 47104–51200 bytes.
Keep the transport option experimental and combine future **measured** decoder
size reductions with headroom for live TLS records and network allocations.
Neither a payload estimate nor core-only fallback qualifies full playback.
