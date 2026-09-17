# TX completion diagnostics — 2026-09-17

Ordinary radio, all 18 accepted Opus ASM stages, I2S PDM32 GPIO3,
CPU160/QIO40, synchronous DMA2x512, input1024/scratch6144/reserve4096.
LED enabled with existing brightness cap32. Diagnostic RX/TX counters48B.
Exact image SHA, configuration and relocation proofs are beside this file.

OTA succeeded. Deutschlandfunk Kultur24 produced29.1093s PCM in30.006s,
with766 DMA underruns: NOT qualified. TX completion snapshots showed16
failed completions out of465 between samples. These are SDK completion
events, not a TCP packet-loss percentage. RSSI after the interval was-53dBm.
Timing stages include waits/preemption and are not CPU utilization.
All captured results are retained under board/. No acoustic qualification.
