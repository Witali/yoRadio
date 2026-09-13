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
