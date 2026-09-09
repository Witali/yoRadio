# ESP8266 native — HTTP socket ownership fix

## 2026-09-09

- Source: `609bbdc88a2d756a8b6e53c36905744d01b67092`.
- Application: 760672 bytes, SHA-256
  `4DC65634E36AE98166A27118C43DF399E81C6CF04B82CA70A8327D220D434596`.
- Publish the stream socket only after validating the initial HTTP body.
  A malformed chunk no longer leaves a closed fd in caller-owned state;
  failed retries/cancellation cannot close an unrelated reused descriptor.
- No new RAM buffers, tasks or allocation. Existing profile retained:
  CPU160, QIO40, mono Helix MP3 SSO + AAC, 6144-byte input, 1000-ms prefill,
  standard I2S PDM32 on GPIO3/RX, two 512-word DMA buffers; ERROR logs.
- Host verification: 237/237 ESP8266 tests pass, no skips. The new actual-C
  ownership regression fails on old code and passes with this change.
- Installed by app-only OTA: HTTP 200/OK, active slot changed from 0x110000
  to 0x10000; upload took 17.46 s. No SPIFFS/NVS/partition image uploaded.
  Wi-Fi client reconnected; served playlist representation remained identical.
- Two-tab WebUI while stopped: 377/266 ms initial load, ten volume actions
  acknowledged in both tabs in 23–47 ms. After the audio test: 401/272 ms,
  ten actions in 22–53 ms. Volume restored to 128 each time.
- MP3 128 starts and produces PCM, but the 30-second continuity test FAILS:
  four incomplete/timed-out health polls, DMA underruns. Sampled minimum free
  heap 7168 bytes; SDK minimum 5044 during the run, later 4140. First Stop
  was not confirmed under load; a subsequent Stop while idle was confirmed.
- Therefore this image fixes the scoped HTTP ownership defect, but is NOT
  stability-qualified for continuous audio or responsive WebUI during playback.
  The 6-KiB input profile remains unqualified. Board left stopped on Retro FM.
- Speaker was disconnected; audio assessment used PCM/DMA counters, not
  listening or analog capture. No board-side malformed-response injection;
  deterministic fd-reuse injection was executed on the host with real C code.

[Fix and references](../../../../docs/ESP8266_HTTP_STREAM_OWNERSHIP_FIX.md).
[Saved test reports](../../../../docs/benchmarks/esp8266-http-ownership-2026-09-09/).

Build: `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-i2s-pdm-http-owner-fix`.
