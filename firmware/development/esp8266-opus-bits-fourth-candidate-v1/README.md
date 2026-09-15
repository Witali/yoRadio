# Fourth-step PVQ shortcut: candidate

2026-09-15. Diagnostic raw Opus ASM; NOT production/default.
CPU160/QIO40, RAM packets, no audio output or stage/function profiler.
One fixed40-byte range in quant_partition:36 live bytes,4 unreachable padding.
Early path saves8/10 instructions, remaining paths add2. No RAM/frame/arena
or image growth. All outside instructions, addresses and tables unchanged.
Actual linked proof378304 cases;24 host PCM/state cases exact.
Pre-deployment98 related regressions PASS/0skip; preflight-tests.log retained.
Physical10 A/B/A still pending; do not infer CPU speed from instruction count.

App903216 B; SHA256
`101d87acdc93a8396ed5b8c234c81aeac291ea6c9646f5ac6345ada9845633c0`.

[Method and results](../../../docs/ESP8266_OPUS_ASM_BITS_FOURTH.md).
Native app OTA only; no UART commands on GPIO3.
