# Frozen decoder-only quant_partition experiment

Changelog 2026-09-14: saved GCC ASM specialized for immutable ctx.encode=0,
in the original2382-byte range.1859 live bytes/523 unreachable padding.
All other ELF bytes, literal/call addresses, RAM and112-byte frame retained.
Parent: accepted PVQ row-loop,160MHz/QIO40/raw RAM packets/no output profiler.
Not production; C fallback unchanged.
Changelog 2026-09-14: all30 physical raw A/B/A attempts complete, exact PCM.
CPU192:87.31390 /90.18467 /87.34133%; both relative-speed gates FAIL.
Candidate REJECTED; active80% CPU target also not met. RAM/frames unchanged;
transient candidate run3 DRAM388 B retained, cause not established.
All JSON/logs, maximum calls, host24 checks and ordinary OTA restoration saved.
Final selected ASM regression suite:57 PASS,0 fail,0 skipped; regression-final.log.
See [experiment](../../../docs/ESP8266_OPUS_ASM_PARTITION_FROZEN.md).
