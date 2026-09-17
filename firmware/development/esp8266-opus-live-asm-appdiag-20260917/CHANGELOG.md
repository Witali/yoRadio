# App-service attribution — 2026-09-17

Ordinary radio with all18 accepted ASM stages, app-task PCM2x960,
DMA128/input2048, CPU160/QIO40, I2S PDM32 GPIO3, LED OFF. Adds16 static
bytes of service counters; scratch6144 and reserve4096 unchanged. OTA PASS.

Kultur24 window1 crossed a reconnect and failed. Stable window2 produced
28.100s PCM in27.999s board time, but16 DMA underruns: NOT qualified.
Heap6672 to6556B in that window, later boot minimum3688B. Queue error0.
Service miss counter increased to4 across the whole session; it does not
explain all underruns. Service max4294966397us is invalid clock-wrap/backstep
evidence, not a multi-hour execution time or CPU measurement.

DLF64 subsequently stalled; final stage response timed out. Retain failed
trial too. No acoustic verification; this is not a successful final profile.
