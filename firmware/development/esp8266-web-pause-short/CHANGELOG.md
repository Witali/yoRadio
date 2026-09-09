# ESP8266 I2S PDM32 — short WebUI audio pause

2026-09-09; source `4a275875b7ed807a4076a8095627bc6c4f4f4fd5`.

- Build with `-WebAudioPause short`: HTTP priority 6, audio priority 5.
- HTTP preempts audio only while runnable; decoder and stream remain open.
- No fixed pause-duration guarantee; audible DMA starvation remains possible.
- CPU160, QIO40, Helix MP3 SSO + AAC, mono, I2S PDM32 DMA GPIO3/RX.
- Input 6144 bytes; prefill 1000 ms; two 512-word output DMA buffers.
- App 760800 bytes; static DRAM unchanged from off; SHA-256 in manifest.json.
- Host regression tests and LX106 build checked. Not flashed; WebUI latency
  and audio continuity still need physical A/B testing.
- App-only development candidate; leave NVS/SPIFFS/partition table intact.

See [mode documentation](../../../docs/ESP8266_WEB_AUDIO_PAUSE.md).
