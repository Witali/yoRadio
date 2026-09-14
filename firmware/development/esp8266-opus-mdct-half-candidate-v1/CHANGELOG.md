# 2026-09-14: frozen-layout MDCT halfword experiment

Full saved GCC ASM with tell-inline parent, five exact17-byte selector patches.
CPU160/QIO40; raw RAM benchmark, no audio output or function/stage profiling.
App903216 B. C fallback, production defaults, RAM and96-byte MDCT stack unchanged.
SHA256 f74fb6f9b2dfd2bd4fd51ac63b772503dbe93b2917c2b012f5e4c15d223c3d97.

30 physical A/B/A and18 related regression tests pass. Median CPU19288.06342%,
versus88.11908/88.10215 controls: only0.044–0.063% relative time improvement.
Both high-bitrate selection checks pass; retain experimental recipe, not default.
Maximum call23.009ms is not improved. Goal70%/continuous I2S not achieved.
All raw attempts, maximums, min RAM and restore checks are beside this file.

Normal live512-idle3s radio was restored via OTA after measurements; this image
is NOT normal listening firmware. [Details](../../../docs/ESP8266_OPUS_ASM_MDCT_HALF.md).
