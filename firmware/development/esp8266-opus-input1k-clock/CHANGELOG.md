# Opus input A/B control, 2026-09-10

Source5147be3, app885520B. Diagnostic radio with atomic wall-clock reads,
input1024B/scratch6144B, CPU160/QIO40, I2S PDM32 GPIO3,2x512-word DMA.
FIR/ICDF/word helpers ON; reciprocal, CELT specialization and rotation ASM OFF.
Production defaults unchanged. OTA succeeded; the image is under test,
not a proven continuous-radio release. All attempts, including HTTP timeouts,
are retained. Wi-Fi/SPIFFS/playlist untouched; no serial actions.

The paired input2k image has the same source/configuration except input size,
config hash, app hash and build time; application size is identical. A live
radio changes content between sequential runs: this is not a bit-identical
raw-codec speed comparison. Report continuity and RAM separately from CPU.
