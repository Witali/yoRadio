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

