# Ordinary radio with accepted Opus ASM — 2026-09-17

- Applied all18 accepted frozen ASM stages through eBands-final, rebased
  into the ordinary radio layout. See manifest/preflight and linked proof.
- No benchmark or tone generator. CPU160/runtimeQIO40, I2S PDM32 GPIO3,
  two512-word DMA buffers; diagnostic health/stages endpoints enabled.
- App885792B, SHA256
  `6914f484fd86fd9bb2044ebe6925cfc4cc31dc9df0a23629753fc361ba276e70`.
- OTA confirmed slot0x10000.24 host cases exact PCM;11 regressions PASS.
- Ten live station attempts:0qualified continuous windows. Includes failed
  commands and seven incomplete measurement windows; not ten codec errors.
  HTTP/transport timeouts persist; heap minimum1440B. Not stable production.
- This ASM image remains on the board; station167/stopped restored.
  Playlist and volume/balance retained. No UART/reset/SPIFFS rewrite.
- `board/` preserves every attempt and final state; `host.json`, `tests.log`
  preserve correctness checks. Full explanation:
  [live report](../../../docs/ESP8266_OPUS_ACCEPTED_ASM_LIVE.md).
