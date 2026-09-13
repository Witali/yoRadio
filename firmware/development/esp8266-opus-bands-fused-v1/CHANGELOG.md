# 2026-09-13 — Opus ASM loop fusion, rejected experiment

Source df497491, bands-fused-asm, CPU160/QIO40, app 903120 B (+128).
Exact PCM and unchanged static RAM/scratch/stack; CPU192 92.898 -> 97.088%,
4.51% slower, repeated control 92.853%. Do not promote to production.
10 initial controls +10 fused +10 tell-intensity +10 final controls; shared
controls are counted once. All attempts/timeout/outliers retained.

comparison.json includes raw reports, host correctness, hashes, full build
profile and RAM/selection checks. host-shapes.json shows B=1 in 82.52% of
192k calls and only 18.22% of coefficients eligible for the fused path.
This is not live playback qualification or a proof of flash/cache causality.

Ordinary radio restored by OTA, app0x10000, stopped. Shared restoration:
../esp8266-opus-bands-control-v1/restore-after-fused-tell-intensity.json.
[Details](../../../docs/ESP8266_OPUS_ASM_NORMALIZATION_FUSION.md).
