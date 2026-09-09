# ESP8266 I2S PDM32 — WebUI pause off

2026-09-09; source `4a275875b7ed807a4076a8095627bc6c4f4f4fd5`.

- Control build: `-WebAudioPause off`, HTTP/audio priorities remain 5/5.
- CPU160, QIO40, Helix MP3 SSO + AAC, mono, I2S PDM32 DMA GPIO3/RX.
- Input 6144 bytes; prefill 1000 ms; two 512-word output DMA buffers.
- App 760800 bytes; SHA-256 in manifest.json. Fits the existing OTA slot.
- Host regression tests and LX106 build checked; not flashed or qualified
  for continuous audio on a physical board in this change.
- App-only candidate: do not overwrite NVS, partition table or SPIFFS.

See [mode documentation](../../../docs/ESP8266_WEB_AUDIO_PAUSE.md).
