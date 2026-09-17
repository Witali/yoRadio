# Diagnostic full-MSS live trial — 2026-09-17

Ordinary radio, all18 accepted ASM stages, I2S PDM32 GPIO3, CPU160/QIO40,
DMA2x512, Opus input1024/scratch6144, SDK RX counters and immediate-refill
fix. TCP MSS1460/window2920/send2920 instead of536/2440/2440.

OTA succeeded. Ten DLF24 live starts: **0/10 qualified**, all ten lacked a
complete measurement window because diagnostic HTTP requests timed out.
This is NOT evidence that every attempt failed to decode; partial status
did report playing. Heap minimum reached3312B. All returned SDK allocation/
enqueue/driver-failure counters were zero. No acoustic assessment is claimed.

A further local saved DLF capture also lacked a complete window. It does
not qualify Internet-radio continuity. This profile is not promoted.
Default TCP settings remain unchanged. Full reports and OTA evidence are
under board/. App/preflight manifests identify exact accepted ASM bytes.
