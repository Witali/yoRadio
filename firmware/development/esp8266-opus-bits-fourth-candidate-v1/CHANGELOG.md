# 2026-09-15 — exact fourth-step PVQ shortcut

- Source experiment f1a96cd9; preceding host frequency census3996d408.
- One fixed40-byte range replaces only register arithmetic/branches/table
  reads. Same outside instructions, image903216 B, static RAM, frame and arenas.
- Actual linked proof378304 cases;24 host PCM/state cases through510kbps,
  including mode transitions, PLC/reset/OOM and compound packets. C fallback
  and the protected GCC snapshot remain unchanged.
- Ten controls, ten candidates, ten repeated controls: CPU192 medians
  86.77929 /86.51781 /86.79698%; both high-bitrate gates PASS. Accepted only
  as an experimental raw baseline, not a production default.
- All raw JSON/log/SHA and statistics retained, including B/run4 observation
  timeout, DRAM minimum1184 B and192kbps maximum call28.717ms. Cause unknown.
- Ordinary live512-idle3s restored OTA in0x10000; HTTP200/WebSocket/stopped
  station167/playlist verified. No UART, SPIFFS, partition or bootloader write.
- Still not achieved:80% raw CPU target and continuous live I2S PDM/WebUI.
- Final100 related regressions PASS/0skip in71.69s, including independent
  physical-report recomputation; final-tests.log retained. Not the full repo suite.

[Full method and results](../../../docs/ESP8266_OPUS_ASM_BITS_FOURTH.md).
