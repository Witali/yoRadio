# Autonomous Opus measurement — 2026-09-17

Source59554c1d, all18 accepted ASM stages, CPU160/QIO40, I2S PDM32 GPIO3.
App PCM2x960, DMA2x128, input2048, scratch6144/reserve4096, LED OFF.
Adds48 static diagnostic bytes; no extra task, allocation or flash logging.
OTA PASS; no UART or SPIFFS changes.24 offline image-identity tests PASS.

Kultur24, no requests inside the runner's65s waits:

| Window | PCM | Board time | DMA underruns |
| --- | ---: | ---: | ---: |
| 1 | 25.100s | 25.003s | 8 |
| 2 | 25.100s | 25.002s | 9 |

Both FAIL the zero-underrun requirement. HTTP sampling is not the sole
cause. These are closed25s board-side windows, not CPU measurements.
No acoustic qualification or promotion to the default profile.
