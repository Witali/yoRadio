# Live Opus DMA512, 2026-09-13

Diagnostic ordinary-radio image, not a raw benchmark. Source fb46cf5.
CPU160/QIO40, I2S-PDM32 on GPIO3, two512-word DMA buffers, C fixed-point
Opus with WordASM/ICDF-word/FIR-word, IRAM/batched PDM, SPIFFS cache disabled.
Opus packet buffer1024B and scratch6144B; no PCM consumer task/queue.
Audio/WebUI stack minimum and decoder reserve unchanged.

Uses3000ms input inactivity timeout instead of1000ms, without extending
individual nonblocking reads. This only tests receive/reconnect behaviour;
it is not an asserted fix for decode/output underruns. Full parameters and
image SHA256 are in manifest.json. Build does not change board defaults.
No physical qualification at build time; later evidence must be recorded
separately. No Wi-Fi, playlist, SPIFFS or partition changes are included.

## Restoration after ASM experiments, 2026-09-13

Application-only OTA succeeded: slot0x110000 ->0x10000, HTTP200/OK,
885552B,19.18s upload, then the expected running slot was observed.
See `restore-after-asm-tests.json` for exact hash and complete OTA evidence.
HTTP status confirms Wi-Fi connected, RSSI-55dBm, no error, stopped, and
the previous selected station unchanged. Free heap27628B, lifetime minimum
24748B, web stack free2288B in a follow-up status sample. These are idle
figures, not decode/RAM or live audio qualification. No new Opus radio
continuity claim is made. The raw benchmark is no longer the active image.
