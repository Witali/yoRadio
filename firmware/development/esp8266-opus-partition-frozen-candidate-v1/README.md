# Frozen decoder-only quant_partition experiment

Changelog 2026-09-14: saved GCC ASM specialized for immutable ctx.encode=0,
in the original2382-byte range.1859 live bytes/523 unreachable padding.
All other ELF bytes, literal/call addresses, RAM and112-byte frame retained.
Parent: accepted PVQ row-loop,160MHz/QIO40/raw RAM packets/no output profiler.
Not production; speed gate and30 A/B/A still pending. C fallback unchanged.
See [experiment](../../../docs/ESP8266_OPUS_ASM_PARTITION_FROZEN.md).
