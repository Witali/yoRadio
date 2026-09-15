# Last PVQ probe shortcut: candidate

2026-09-15. Diagnostic raw Opus ASM benchmark; NOT production.
CPU160/QIO40, RAM packets, no audio output or stage/function profiler.
Two ranges20+28 B; reused encoder-only storage proven unreachable for
private encode=0. Fast path saves2/4 instructions, rare path adds3/4.
No RAM/frame/arena/image growth. All other linked addresses/bytes preserved.
Host24 PCM/state cases exact; physical A/B/A pending.

App903216 B, SHA256
`46c27cfba72216c75f143299545c996a5358f639ee8dcf25d0f0b9cd04d6fe79`.

[Method and results](../../../docs/ESP8266_OPUS_ASM_BITS_FIFTH.md).
Only native application OTA. No UART application commands on GPIO3.
