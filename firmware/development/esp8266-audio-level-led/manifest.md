# ESP8266 native radio — hardware audio-level LED

- Built: 2026-09-09, source `a98116e5d130712de279b14ce2476b0454166f4b`.
- Application: `app.bin`, 764272 bytes.
- SHA-256: `562e1986f72097f33210fa85ce1e4a7350ef056522d24b051a43694915001517`.
- Profile: CPU160, QIO40, Helix MP3 SSO + AAC, mono, input 4096 bytes,
  I2S PDM32 SLC-DMA on GPIO3/RX, 2 x 512-word DMA buffers, short WebUI pause.
- Error logs and bounded local SPIFFS logging enabled; test tone, profiling
  and debug traces disabled. Wi-Fi, playlist and partition layout unchanged.
- LED: active-low GPIO2/D4, hardware GPIO sigma-delta, maximum divider 255,
  20-Hz brightness refresh, at most 64 frames sampled per refresh. No PWM ISR,
  new task, heap allocation or additional audio buffer.
- Layout: two 960-KiB app slots and SPIFFS 256 KiB. Use the native WebUI OTA
  application endpoint; OTA selects the inactive slot. Initial app0 address
  is `0x10000`, not an instruction to serial-flash the running board.
- Compared with `../esp8266-spiffs-log/`: +944 image bytes, +16 static DRAM
  bytes; IRAM unchanged. These are linker/build measurements, not runtime
  free-heap or CPU-time measurements.
- Targeted LED and audio-path tests: 13/13 passed (four host hardware mocks
  plus eight bit-exact I2S output combinations and one configuration check).
- Final complete ESP8266 host regression: 257/257 passed, no skips, 113.16 s.
- Not flashed in this task. Physical brightness and CPU overhead still need
  on-board verification. Deployment must follow the repository OTA/RX rules.

Build command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-audio-level-led -WebAudioPause short -SpiffsLog
```

Select `-LedUpdateHz 10` or `-NoAudioLevelLed` with a fresh variant for a
different LED configuration. See [implementation and tests](../../../docs/ESP8266_AUDIO_LEVEL_LED.md).
