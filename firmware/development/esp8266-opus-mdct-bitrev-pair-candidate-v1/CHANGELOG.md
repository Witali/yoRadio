# 2026-09-14: MDCT bitrev pair experiment, not accepted

Saved GCC ASM + accepted MDCT-half parent. One24-byte instruction replacement
caches a bitrev word in a0 across two iterations, without extra RAM or stack.
CPU160/QIO40 raw RAM benchmark; PDM/function/stage profiling disabled.
App903216 B, SHA2563095072ae7bed52ce2fb83b815122487e20403f5adbacd14116d91e363bf0274.

30 A/B/A exact PCM,24 related regressions pass. CPU19288.02013%, but repeated
128 gain0.01595% is below mono12 slowdown0.02031%; standalone candidate OFF.
Max192 call22.621ms is not improved. Accepted best remains MDCT-half.
All attempts, peaks, min RAM and restore checks archived alongside this file.

Normal live512-idle3s radio restored through OTA after measurements. This image
is a diagnostic benchmark, not normal listening firmware. Goal70% not achieved.
[Details](../../../docs/ESP8266_OPUS_ASM_MDCT_BITREV_PAIR.md).
