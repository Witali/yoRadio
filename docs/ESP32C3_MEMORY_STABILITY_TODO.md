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

## Implementation

- [ ] Keep the 16 KiB TLS receive buffer and 4 KiB transmit buffer allocated
  for the lifetime of one HTTPS connection instead of reallocating them for
  every TLS record.
- [ ] Allocate the ICY metadata workspace once and reuse it across stations.
- [ ] Preserve the Espressif decoder PCM workspace across station changes and
  only grow it when a codec reports a larger required frame.
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

