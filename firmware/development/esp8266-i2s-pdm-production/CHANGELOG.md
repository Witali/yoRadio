# ESP8266 production: I2S PDM32

## 2026-09-08

- User stopped the latency investigation and requested ordinary production
  radio with I2S PDM instead of the temporary SPI debug output.
- Source `fd34463`, app758432 bytes, SHA-256
  `8F3DC79EF7D8C11945F64BAB9CAB5D9A2EA237CD7691CB8F6C814F651DA39B01`.
- Flashed app0 at0x10000 on COM8, hardware flash hash verified. NVS, Wi-Fi,
  full playlist, SPIFFS, bootloader and partition table were not overwritten.
- Standard delta-sigma PDM32 on GPIO3/RX, nominal1.536 MHz
  (integer divider1.538461 MHz), mono48 kHz PCM, two512-word SLC-DMA buffers.
  CPU160 MHz, QIO40, Helix MP3 SSO and Helix AAC. No SPI/RCPDM/PCM transport.
- Tone, codec/output benchmark, audio/memory/WebUI tracing are disabled.
  Application log level ERROR; normal error reporting remains enabled.
- Includes latest shared WebUI initial-snapshot and compact-volume fixes.
  No renewed latency optimization or extended benchmark was requested.
- Build: `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1`.
  Connect the filtered amplifier input to RX/GPIO3, not D7/GPIO13.
  UART was used only for ROM flashing/reset and passive TX log capture.
- Short boot check: firmware runs, but the SDK reports repeated Wi-Fi
  association/disconnection attempts. Two HTTP status attempts timed out;
  network readiness and audible radio were not confirmed. No further Wi-Fi
  debugging or settings changes were performed, per the user's stop request.
  Precompiled SDK Wi-Fi code can still emit its own state messages despite
  the application ERROR log threshold.
