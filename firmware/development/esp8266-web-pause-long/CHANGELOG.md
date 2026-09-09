# ESP8266 I2S PDM32 — long WebUI audio pause

2026-09-09; source `4a275875b7ed807a4076a8095627bc6c4f4f4fd5`.

- Build with `-WebAudioPause long`: static-page loads cooperatively release
  the decoder and close the radio stream before sending the response.
- Owner acknowledgement deadline 1000 ms; timeout returns HTTP 503.
- Hold for 250 ms after the last completed static request; then reconnect.
- New Stop/Play/Next supersedes the old stream resume. No persistent Stop.
- Periodic status/WebSocket traffic does not request long pauses.
- CPU160, QIO40, Helix MP3 SSO + AAC, mono, I2S PDM32 DMA GPIO3/RX.
- Input 6144 bytes; two 512-word DMA buffers; app 762624 bytes.
- Static DRAM +8 bytes versus off; no new task/audio buffer. SHA-256 in manifest.
- Host regression tests and LX106 build checked. Not flashed; intentional
  audible interruptions and physical WebUI performance are not yet measured.
- App-only development candidate; leave NVS/SPIFFS/partition table intact.

See [mode documentation](../../../docs/ESP8266_WEB_AUDIO_PAUSE.md).
