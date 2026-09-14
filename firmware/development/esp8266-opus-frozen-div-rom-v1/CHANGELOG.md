# Frozen-layout ROM diagnostic control — 2026-09-14

One aligned L32R literal target redirected from exact ASM helper to original
ROM __udivsi3. Same complete ELF bytes except this word; no instruction,
address, RAM, stack or codec configuration changes. App903872B, SDK v3 packing,
QIO40 build configuration/DIO image header unchanged; checksum/SHA256 valid.
Not production, no UART. Ten-before/ten-after physical measurements complete:
CPU192 medians91.2016/91.1890%, paired ASM103.6197%; ASM rejected.
All PCM exact, static RAM unchanged. Full thirty-run archive is in ASM folder.
Method and ASM-pair artifacts: ../esp8266-opus-frozen-div-asm-v1/ and
docs/ESP8266_OPUS_ASM_FROZEN_DIV.md. Original C fallback remains unchanged.
