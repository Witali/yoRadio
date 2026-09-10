# Flash-source Opus short-publication diagnostic, 2026-09-10

Source `391a85b`, app 912560 bytes. Same configuration as publication512
except a128-word producer loan. Physical DMA buffers remain two512-word
buffers. All five PCM fingerprints matched, all continuity cases failed.
No consistent benefit: keep default512; this option remains diagnostic-only.

`board-results.json`, `ota-results.json`, `return-live-ota.json` retain the
test and OTA evidence. No serial access, SPIFFS or saved playlist upload.
Returned to live `esp8266-opus-stage-wall-icdf` via OTA. The later real
HTTP Opus test failed; `live-followup.json` retains the timeout observation.
Playback explicitly stopped. This is not a production release.

[Method, comparison and limitations](../../../../docs/ESP8266_OPUS_FLASH_OUTPUT_BENCHMARK.md).
