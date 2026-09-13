# 2026-09-13 — Opus ASM inline + intensity, rejected combination

Source 5a4bc210, bands-tell-intensity-asm, CPU160/QIO40, app 903248 B (+256).
Four inline sites plus the exact intensity shortcut; one shared 32-B table.
Exact PCM and unchanged static RAM/scratch/stack. CPU192 92.898 -> 92.315%,
only 0.63% less time, while mono12 slows 3.19%. Repeated control confirms
rejection by the user's high-bitrate-first criterion. Best remains separate
tell-inline at 88.136%; target <=70% not reached. Default C unchanged.

10 initial controls +10 fused +10 this candidate +10 final controls, shared
controls counted once. All numbered attempts and final-control timeout/
heap/CPU outlier retained in comparison.json, without replacement.
Ordinary radio restored by OTA, app0x10000, stopped. Shared restoration:
../esp8266-opus-bands-control-v1/restore-after-fused-tell-intensity.json.
[Details](../../../docs/ESP8266_OPUS_ASM_TELL_INTENSITY_RESULTS.md).
