# ESP8266 SPI radio: raw playlist comparison

## 2026-09-08

- Source `b74e21b`, compiled only; **not flashed**.
- `CONFIG_YORADIO_PLAYLIST_WEB_GZIP` OFF; no gzip encoder/cache symbols.
  Other sdkconfig entries match the normal gzip-enabled comparison image.
- Ordinary radio, SPI-PDM GPIO13/D7, CPU160/QIO40, no tone or WebProfile.
- 761328 bytes, SHA-256
  `00904E8B91C0A54DB8244C968086A9C4C4E19C99DB2A9A5D4DBD3183EBDC3ECA`.
- Build with `tools/esp8266_audio_profile/build_spi_pdm_debug.ps1 -NoPlaylistGzip`.
  Existing compressed cache files are ignored, not deleted. CSV/index and
  compressed WebUI HTML/JS/CSS are unchanged by this playlist-only option.
