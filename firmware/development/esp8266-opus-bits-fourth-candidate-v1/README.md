# Fourth-step PVQ shortcut: candidate

2026-09-15. Diagnostic raw Opus ASM; NOT production/default.
CPU160/QIO40, RAM packets, no audio output or stage/function profiler.
One fixed40-byte range in quant_partition:36 live bytes,4 unreachable padding.
Early path saves8/10 instructions, remaining paths add2. No RAM/frame/arena
or image growth. All outside instructions, addresses and tables unchanged.
Actual linked proof378304 cases;24 host PCM/state cases exact.
Pre-deployment98 related regressions PASS/0skip; preflight-tests.log retained.
All30 physical A/B/A complete: CPU19286.77929 /86.51781 /86.79698%; both
high-bitrate gates PASS. New experimental raw baseline, default unchanged.
Static RAM/frame/arena unchanged; minimum free DRAM8172 /1184 /8160 B,
free stack1660 B. B/run4 HTTP timeout and all outliers retained.
Ordinary radio restored OTA; HTTP/WS/station/playlist checked. The80% CPU
target and continuous live I2S PDM remain unqualified.

App903216 B; SHA256
`101d87acdc93a8396ed5b8c234c81aeac291ea6c9646f5ac6345ada9845633c0`.

[Method and results](../../../docs/ESP8266_OPUS_ASM_BITS_FOURTH.md).
Native app OTA only; no UART commands on GPIO3.
