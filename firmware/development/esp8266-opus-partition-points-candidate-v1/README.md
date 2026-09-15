# Pointwise quant_partition ASM candidate

2026-09-15. Diagnostic raw Opus benchmark, not production. CPU160/QIO40;
RAM input packets, no audio output or stage/function profiler.

Five frozen-address changes (16 bytes): two immutable-zero loads become
MOVI, three proven decoder-only branches become J. Same dynamic instruction
count, registers/ABI, stack112, static RAM and all other ELF bytes.
Host24 exact PCM cases and linked proofs retained; all30 physical A/B/A runs
are complete. CPU192:87.34119 /87.32800 /87.32333%; both speed gates FAIL.
Retained for combinations, not accepted alone; current80% goal not reached.
Raw DRAM minima8204 /1052 /8352 B, stack minimum1660 B. Candidate run10
timeout/CPU192100.58858% and A2 mono12 window excess743us are preserved.
All PCM exact;81 related tests PASS. Ordinary restored OTA; HTTP/WS checked.

App:903216 bytes, SHA256
`9b21df3103a45831d30827568384427e618f087182d2b0430639affcd120d76f`.

See [method, checks and result](../../../docs/ESP8266_OPUS_ASM_PARTITION_POINTS.md).
Use native application-only OTA; do not send UART commands on GPIO3.
