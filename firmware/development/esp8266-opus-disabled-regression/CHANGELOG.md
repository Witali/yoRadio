# 2026-09-09 — Opus-disabled regression build

Source `6a9f8eaffd8075fd9da7280346804e8ccd41c0d7`, app 763936 bytes.
SHA-256 `42391e2c0d644551aef89f47b4ce535c0321e18f139d4d3038551f8613afb93b`.

Same native I2S PDM32/GPIO3 production configuration with Opus OFF.
MP3/AAC input 4096 B and audio stack 4096 B retained. The ELF contains no
`opus_decode`, `native_opus`, `yoradio_opus` or `ogg_opus` symbols.
Full shared/ESP8266 host suite 334/334 PASS. Not flashed in this change.
Use the matching script.js.gz from the experimental/volume100 artifact if
updating a board that still has the old volume0..254 WebUI.
