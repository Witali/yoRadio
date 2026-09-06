# AAC block-size measurements

Filtered UART logs retain codec memory, timing, DMA and lifecycle metrics;
boot noise and network identifiers are omitted. `decode-*.log` has no audio
output; `output-*.log` includes PCM -> PDM -> physical DMA. `full` selects the
retained full-frame bridge. Numeric suffixes are PCM frames per callback.

Each case uses 8 warm-up and 200 measured retained AAC/MP3 frames from RAM,
with Wi-Fi disabled. See [analysis and configuration](../../ESP8266_AAC_PCM_BLOCKS.md).
`regression.log`: 341 tests passed, no skips/failures, 91.64 seconds.
