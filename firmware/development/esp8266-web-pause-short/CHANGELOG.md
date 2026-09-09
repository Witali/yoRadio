# ESP8266 I2S PDM32 — short WebUI audio pause

2026-09-09; rebuilt from `527953a8b52c9b237a7d2967898ae9debed4d181` and
installed on the physical Wemos D1 mini via native OTA.

- Build with `-WebAudioPause short`: HTTP priority 6, audio priority 5.
- HTTP preempts audio only while runnable; decoder and stream remain open.
- No fixed pause-duration guarantee; audible DMA starvation remains possible.
- CPU160, QIO40, Helix MP3 SSO + AAC, mono, I2S PDM32 DMA GPIO3/RX.
- Input 6144 bytes; prefill 1000 ms; two 512-word output DMA buffers.
- App 760800 bytes; static DRAM unchanged from off; SHA-256 in manifest.json.
- SHA-256: `8F22523F459ADB94368CE31BFBF96F13C92A253102178E2491312294F965267E`.
- OTA returned HTTP 200/OK in 17.89 s; new running slot confirmed:
  `0x10000` -> `0x110000`. Served playlist hash unchanged; no NVS/SPIFFS upload.
- Idle WebUI, two tabs: ready in 403/291 ms, ten volume clicks acknowledged
  by both tabs in 20-55 ms. Two WebSockets remained connected.
- Retro FM MP3 128 kbps started, but the 30-second continuity test FAILED:
  DMA underruns increased and 5/7 health polls timed out. Two complete samples
  gave minimum free heap 7236 bytes; SDK low-water later reached 4548 bytes.
- Stop succeeded. The subsequent two-tab WebUI test passed: 256/241 ms to
  ready, 22-53 ms volume ACK. Left stopped on station 510, volume restored to 128.
- No audible quality claim: verification used PCM/DMA counters, not a recording.
- Fixed updater compatibility with PowerShell UTF-8 BOM before any upload;
  seven targeted manifest/pause tests passed. Full 243-test result is retained
  in the original pause-mode documentation.
- App-only development candidate; leave NVS/SPIFFS/partition table intact.

See [mode documentation](../../../docs/ESP8266_WEB_AUDIO_PAUSE.md).
Physical reports: [deployment test](../../../docs/ESP8266_WEB_PAUSE_SHORT_DEPLOY_2026-09-09.md).
