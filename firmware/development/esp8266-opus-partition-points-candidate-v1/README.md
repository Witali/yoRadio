# Pointwise quant_partition ASM candidate

2026-09-15. Diagnostic raw Opus benchmark, not production. CPU160/QIO40;
RAM input packets, no audio output or stage/function profiler.

Five frozen-address changes (16 bytes): two immutable-zero loads become
MOVI, three proven decoder-only branches become J. Same dynamic instruction
count, registers/ABI, stack112, static RAM and all other ELF bytes.
Host24 exact PCM cases and linked proofs retained; physical speed pending.

App:903216 bytes, SHA256
`9b21df3103a45831d30827568384427e618f087182d2b0430639affcd120d76f`.

See [method, checks and result](../../../docs/ESP8266_OPUS_ASM_PARTITION_POINTS.md).
Use native application-only OTA; do not send UART commands on GPIO3.
