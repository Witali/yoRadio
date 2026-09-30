# ESP32-C3 memory stability TODO

Goal: keep HTTPS radio playback reliable on the ESP32-C3 OLED board by
avoiding repeated allocation and release of large heap blocks.

## Physical AAC findings, 2026-09-30

See the [hardware report](ESP32C3_CACHE_HARDWARE_20260930.md). Isolated full-rate
AAC passes on this board, but the full radio has a separate heap limitation:

- [x] Reproduce the initial AAC-LC failure: a 12,288-byte allocation fails with
  14,848 bytes free and only 7,680 bytes in the largest block.
- [x] Disable Wi-Fi IRAM/RX IRAM speed optimizations for this C3 profile,
  freeing about 19 KiB; verify real 48 kHz stereo LC streaming with Wi-Fi,
  OLED updates, PDM output and WebUI polling.
- [ ] Make room for the additional **55,128-byte contiguous SBR allocation**,
  while keeping enough heap for Wi-Fi, WebUI and TLS. With the RAM-saving
  build it still failed with 27–36 KiB free and 8–16 KiB largest blocks.
- [ ] Prevent silent full-AAC degradation or clearly report it: the library
  fell back to 24 kHz stereo for HE-AAC and 22.05 kHz mono for HE-AAC v2 despite
  `CONFIG_YORADIO_AAC_PLUS=y`. This is not a configured frequency cap.
- [ ] Repeat full-rate HE/v2 playback, in-stream format transitions and total
  CPU measurements after the memory fix. Isolated decoder results do not prove
  that the complete radio can allocate the same decoder state.

Do not reduce the shared 16 KiB decoder task stack blindly: the retained Opus
benchmark used about 12.2 KiB. A fix must preserve other codecs and user settings.

## AAC memory reuse during decoding — planned, 2026-09-30

### Execution plan and decision gates

Status: **in progress**. The bounded SDK allocation tracer and its host checks
are implemented; real-decoder QEMU traces confirm allocation lifetimes and
close/reopen cleanup. Physical peak-budget qualification and the memory-saving
changes below remain pending. The baseline is the fixed EOF application
from `69410cd5`, archived and tested in `1bfc8b64`: DIO 80 MHz, no deep sleep,
Espressif AAC Plus, no PSRAM. The [EOF correction](ESP32C3_EOF_STATUS.md) is
complete; it does not resolve SBR memory allocation. Keep its regressions passing.

**Objective:** full-rate AAC-LC, HE-AAC v1 and HE-AAC v2 in the complete C3 radio,
with both output channels and all existing supported rates/bitrates preserved.
Do not obtain a memory saving by imposing a 22/24 kHz ceiling, disabling SBR/PS,
forcing mono, or replacing production AAC with the current LC-only Helix path.

The [measured allocation map](ESP32C3_AAC_MEMORY_20260930.md) is the starting
point, not a universal capacity calculation:

| Item | Recorded size / estimate | Planning consequence |
| --- | ---: | --- |
| SBR object plus control object | 55,128 + 1,180 bytes | The shipped binary needs the first object contiguous |
| Free heap at the measured failure | 36,192 bytes; largest block 13,312 bytes | Recover at least the 20,116-byte arithmetic deficit **plus** operating headroom; also address fragmentation |
| SDK state with SBR | Roughly 107 KiB before margin | Budget estimate, not a proven arena size for every stream |
| SDK state, ADTS wrapper and caller PCM | Roughly 127 KiB before margin | These allocations coexist; moving them into one pool does not reduce their total |
| Existing C3 Helix arena capacity | 24 KiB | Not resident in the production Espressif build; cannot count it as reclaimable RAM |

Proceed in this order; keep each accepted change and its evidence in a focused
commit. Record rejected candidates as well as improvements.

1. **Establish the peak live allocation budget.**
   - [ ] Trace allocation size, owner, lifetime and peak overlap through decoder
     open, first LC/SBR/PS frame, format changes, EOF, Stop and close. Use bounded,
     preallocated trace storage; do not allocate from the hook being measured.
   - [ ] Distinguish persistent history, frame-local scratch, input framing,
     caller PCM and queued/DMA-owned output. Separate decoder-owned allocations
     from registration/global objects that survive decoder close.
   - [ ] Measure total free RAM, largest block, stack margins and transient TLS/
     WebUI/OTA demand on the physical board, including the largest selectable
     audio buffer. Record instrumentation overhead and remeasure the quiet build.
   - Gate: save a lifetime diagram and a worst-observed concurrent budget. Do
     not add all allocation sizes together or count already shared memory twice.

2. **Recover RAM outside SBR before reserving a large arena.**
   - [x] In `audio_service.c`, evaluate an AAC-specific initial caller PCM
     workspace of 8,192 bytes instead of the shared 12,288-byte default: a
     saving of 4,096 requested bytes. AAC also shrinks a retained larger
     workspace after the previous decoder closes. Host checks cover transitions,
     grow/shrink failure and preservation of the old buffer; other codecs retain
     their capacity and needed-size growth. The real decoder's LC/HE/v2 QEMU
     output (328,770 stereo frames) matches the previous capture byte-for-byte
     with 8 KiB PCM plus an overrun guard. [Evidence](../tests/results/esp32c3-aac-pcm-20260930/pcm-equivalence.json).
     This alone cannot close the measured deficit; physical qualification follows.
   - [ ] Check bounded-output support before attempting smaller PCM chunks.
     The current adapter requires a complete 8,192-byte SBR stereo frame. Preserve
     the ability to receive legal ADTS frames up to the existing 8,191-byte limit;
     reducing a constant or splitting a network read is not a framing solution.
   - [ ] Audit system RAM candidates separately: stack reductions only after
     worst-path measurements, heap-function placement in flash only after a
     cache-disabled/ISR call audit, and Wi-Fi pool changes only with throughput,
     reconnect and concurrent WebUI tests. Preserve the shared 16 KiB decoder
     stack, full TLS receive capability and the user's buffer setting.
   - Gate: quantify actual peak savings. The already disabled Wi-Fi IRAM options
     and existing scratch overlays are baseline savings, not new gains.

3. **Prototype a common codec arena with correct ownership.**
   - [ ] Reuse the Helix arena's single-owner concept for Espressif AAC; avoid
     reserving independent pools for mutually exclusive decoder owners. Pin and
     verify the media allocator ABI and route only the intended allocations.
   - [ ] Implement alignment, zeroing, overflow checks, individual frees and
     realloc semantics, including preservation of old data on realloc failure.
     The existing bump allocator with no-op free is insufficient for repeated
     AAC reopen/configuration changes within one session.
   - [ ] Keep long-lived registration objects outside resets. Transfer ownership
     only after decoder close and release of all consumers; test open failure,
     repeated LC/HE/PS changes, Stop, cancellation and switching to other codecs.
   - Gate: reserve a measured budget early enough to avoid fragmentation **only
     once it fits the concurrent system budget**. An early reservation prototype
     may measure placement; it must not starve networking or be called a RAM saving.

4. **Reduce decoder-internal storage where source access permits.**
   - [ ] Obtain buildable compatible source or evaluate an equally capable
     source-available decoder. Rebuild all users of changed structures, including
     optimized routines. Allocator interception cannot split the shipped
     `SBRDECODER_DATA` object, whose fields are accessed at fixed offsets.
   - [ ] Separate persistent low-band QMF history from frame-local work; evaluate
     one workspace for sequential stereo channels. The investigation estimates
     **6,144 bytes** of potential ordinary-stereo savings, not a measured result
     and not an automatic saving for HEv2/PS.
   - [ ] Map a separate PS-safe layout: the right SBR channel already holds live
     PS state for a mono AAC core. Preserve filter delays, smoothing history,
     overlap, decorrelation and both output channels across frames.
   - [ ] Evaluate splitting large embedded arrays into smaller blocks and sharing
     envelope/synthesis scratch after its last reader. Splitting alone saves no
     payload RAM; never overlay input or PCM still owned by a queue/DMA consumer.
   - Gate: prove lifetimes and equivalence before combining optimizations. Do not
     add the estimated PCM and QMF savings unless they coexist in the same build.
     If compatible source is unavailable, retain internal-layout changes as blocked
     work; do not patch binary offsets or substitute an LC-only decoder.

5. **Prove compatibility and failure handling.**
   - [ ] Compare optimized PCM and persistent state with the unchanged same
     decoder, bit-exactly where applicable. Use FFmpeg/FDK for independent profile,
     layout, duration and drain checks; different decoder PCM is not assumed exact.
   - [ ] Cover LC/HE/v2, distinct left/right audio, window sequences, supported
     rates/bitrates and actual input paths; add missing fixture coverage explicitly.
     Test truncated/malformed input, allocation failure at every stage, failed
     realloc, backpressure, cancellation, reset, EOF and repeated owner changes.
   - [ ] Require correct LC -> SBR/PS transitions, including unchanged ADTS core
     headers. The existing detection/reopen limitation is a separate acceptance
     item; lower RAM consumption does not automatically fix it.
   - Gate: full decoded rate/channels and truthful OLED/WebUI metadata. AAC-core
     fallback is a failure of HE/v2 acceptance, even if audio and EOF still work.

6. **Qualify the complete radio and retain the result.**
   - [ ] Run the [C3 acceptance suites](ESP32C3_TESTING.md): HTTP and trusted
     HTTPS matrices, format transitions, EOF, faults, switching/heap recovery,
     WebSocket, concurrent load, one-hour LC/HE/v2 soaks and exact-image OTA.
     Recheck MP3, FLAC, Vorbis and Opus and inspect physical stereo output/OLED.
   - [ ] Compare total and decoder CPU, peak call time, RAM/largest-block minima,
     task stacks and actual underruns against the baseline. Use the existing
     published budgets; predeclare any additional regression limit before A/B.
     QEMU helps isolate decoder behavior but does not qualify full-radio memory,
     Wi-Fi, TLS or real-time output.
   - [ ] Save source/library/configuration hashes, allocation maps, failed and
     passing results, and successful test images under `firmware/development/`.
     Update manifests/changelog and preserve Wi-Fi, playlist and user settings.
   - Completion gate: full-rate HE/v2 works with the normal radio services and
     sustained load, all supported formats remain available, and the tests pass.
     A larger arena, isolated decode or a few saved KiB alone is not completion.

### Existing findings and detailed checklist

The [RAM/SBR investigation](ESP32C3_AAC_MEMORY_20260930.md) now maps the 55,128-byte
object, verifies existing PS reuse against the binary, and measures the full
radio. The 24 KiB Helix arena is not allocated in the current Espressif build.

- [x] Measure startup/AAC heap phases and task stack margins on physical C3.
- [x] Identify SBR channel/PS storage and already shared scratch using pinned
  primary source, a 32-bit layout probe and actual binary offsets.
- [ ] Prototype an Espressif-AAC adapter for the common codec arena, with
  free/realloc and complete cleanup across AAC configuration changes. Budget
  roughly 107 KiB for observed SDK state before margin, not the existing 24 KiB.
  First recover the measured total-RAM shortfall; reservation alone is no fix.
- [ ] Evaluate source-level separation of SBR persistent history and shared
  QMF scratch, including a distinct PS-safe lifetime map. Splitting an embedded
  array requires rebuilding its users; an allocator override cannot do it.

- [ ] Reduce peak AAC memory by reusing buffers whose lifetimes do not overlap,
  using the ESP8266 implementation as a reference. **Preserve the full AAC
  feature set; do not trade supported formats for lower RAM use.**

Reference: [ESP8266 bounded PCM output](ESP8266_AAC_PCM_BLOCKS.md),
[`AACDecodeBlocks`](../yoRadio/src/audioI2S/aac_decoder/aac_decoder.cpp), and the
[native ESP8266 bridge](../esp8266/rtos-sdk-native/components/helix_codecs/codec_bridge.cpp).
That implementation emits reusable PCM blocks and updates each overlap word
only after its last use for the current output. The selected 512-frame mono
profile saves 3,072 bytes, with about 6.1% more decoder time in its measured
workload. Stereo needs more PCM space. Neither the saving nor the CPU cost is
an estimate for C3.

The existing block API is guarded by `YORADIO_ESP8266_NATIVE` and excludes
`AAC_ENABLE_SBR`. C3 production uses Espressif `esp_audio_codec` 2.6.2, whose
decoder internals are supplied as a precompiled RISC-V library. Switching to
the current Helix AAC-LC-only path would lose HE-AAC functionality and is not
an acceptable implementation of this optimization.

### Investigation

- [ ] Map the peak live allocations of ADTS input, PCM, spectral/IMDCT scratch,
  overlap history, SBR and parametric stereo (PS). Share only temporary storage
  with disjoint lifetimes; preserve both channels and persistent decoder state.
  Do not reuse memory while output/DMA still owns it.
- [ ] Evaluate smaller reusable PCM blocks through the Espressif API before
  considering decoder-internal changes. The current
  [C3 adapter](../idf/esp32c3-oled-native/main/native_aac_decoder.c) requires an
  8,192-byte output to keep one SBR stereo frame atomic and reserves 8,191 bytes
  for a complete ADTS frame. Check bounded output and input sizing without
  truncating legal frames, losing pending PCM, or corrupting retry/progress
  accounting and format changes.
- [ ] Check whether supported allocator/workspace APIs permit shared scratch.
  If internals must change, establish source/API access or evaluate an equally
  capable decoder; do not assume ESP8266 source changes apply to the binary SDK.
- [ ] Measure peak live RAM **and the largest contiguous block**. A reusable
  arena can reduce fragmentation but cannot by itself remove a simultaneously
  needed 55,128-byte SBR allocation. Quantify the remaining shortfall after each
  change; a few KiB saved in PCM is not evidence that HE/v2 now fits.

### Required compatibility and acceptance

- [ ] Preserve every supported AAC variant: AAC-LC, HE-AAC v1 (SBR), HE-AAC v2
  (SBR + PS), mono/stereo, supported rates and bitrates, and supported input
  framing/container paths. Inventory the actual firmware paths separately
  from the SDK's capabilities; record missing variants as gaps to address,
  rather than claiming that all AAC profiles or containers already work.
- [ ] Require full decoded sample rate and channels, including 44.1/48 kHz
  HE/v2 stereo. No forced 22/24 kHz limit, forced mono, disabled SBR/PS, or silent
  AAC-core fallback is acceptable as a RAM optimization. The current full-radio
  SBR allocation failure above remains an open defect until this passes.
- [ ] Compare PCM and persistent overlap/state against the original path where
  exact comparison applies; exercise all window sequences, distinct L/R audio,
  malformed/truncated input, output backpressure/cancellation, reset and OOM.
- [ ] Verify source and PCM metadata, including in-stream changes, on OLED and
  WebUI. A changed output buffer size must not leave stale format information.
- [ ] Run A/B on physical C3 with Wi-Fi, HTTP/HTTPS, WebUI and PDM active. Record
  total CPU, decoder CPU, heap/stack margins and underruns. Recheck other codecs;
  an isolated decoder or QEMU pass alone is insufficient for acceptance.

## Implementation

- [ ] Keep the 16 KiB TLS receive buffer and 4 KiB transmit buffer allocated
  for the lifetime of one HTTPS connection instead of reallocating them for
  every TLS record.
- [ ] Allocate the ICY metadata workspace once and reuse it across stations.
- [x] Preserve the Espressif decoder PCM workspace for explicitly compatible
  station changes and only grow it as needed. The current audio service releases
  it for AUTO or custom-decoder targets; this existing reuse is separate from
  the planned within-frame scratch/PCM optimization above.
- [ ] Use 16 KiB (10 x 1600-byte blocks) as the compressed-audio default,
  while keeping the user-selectable 8-22.4 KiB range for jittery streams.
- [ ] Log free heap, largest free block, minimum free heap and task stack
  high-water marks after the TLS handshake and after the first decoded frame.

## Verification

- [ ] Add regression tests for buffer lifetime, the 16 KiB default, and the
  configurable upper limit.
- [ ] Run the complete host test suite.
- [ ] Build the normal ESP-IDF firmware with `-O3`.
- [ ] Test repeated HTTPS AAC playback on the physical ESP32-C3 OLED board.

