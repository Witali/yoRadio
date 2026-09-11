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

Completed ten DLF24 windows:0/10 continuity passes, health missing in1/6/7.
Seven observable intervals had515..1591 new DMA misses, sampled minimum
heap6436B. All observed stage clocks were plausible after the atomic-read fix.
The paired [comparison](../esp8266-opus-input2k-clock/comparison.json) retains
every attempt. Neither image qualifies as continuous Opus radio.

2026-09-11: restored by OTA after the2KiB experiment. Local own SILK12 over
HTTP also had TCP reconnects. One steady26991ms interval delivered27060ms
PCM and26 DMA misses, with no input-wait calls. Output had15 attributed
misses; sampling endpoints are not atomic. See local-silk12-steady.json and
the TCP log; server accepted bytes are not proof of delivery.
