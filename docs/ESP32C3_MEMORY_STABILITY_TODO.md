# ESP32-C3 memory stability TODO

Goal: keep HTTPS radio playback reliable on the ESP32-C3 OLED board by
avoiding repeated allocation and release of large heap blocks.

## Implementation

- [ ] Keep the 16 KiB TLS receive buffer and 4 KiB transmit buffer allocated
  for the lifetime of one HTTPS connection instead of reallocating them for
  every TLS record.
- [ ] Allocate the ICY metadata workspace once and reuse it across stations.
- [ ] Preserve the Espressif decoder PCM workspace across station changes and
  only grow it when a codec reports a larger required frame.
- [ ] Limit the compressed audio ring to 16 KiB (10 x 1600-byte blocks),
  including migration of an older larger saved value.
- [ ] Log free heap, largest free block, minimum free heap and task stack
  high-water marks after the TLS handshake and after the first decoded frame.

## Verification

- [ ] Add regression tests for buffer lifetime and the 16 KiB limit.
- [ ] Run the complete host test suite.
- [ ] Build the normal ESP-IDF firmware with `-O3`.
- [ ] Test repeated HTTPS AAC playback on the physical ESP32-C3 OLED board.

