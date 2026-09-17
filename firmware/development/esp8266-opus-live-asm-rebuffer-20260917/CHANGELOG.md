# Opus read-ahead recovery — 2026-09-17

Source1c1d5757; all18 accepted ASM stages, CPU160/QIO40, I2S PDM32 GPIO3.
App PCM2x960, DMA2x128, input2048, scratch6144/reserve4096, LED OFF.
OTA PASS; application only, no UART or SPIFFS changes.

Not qualified as continuous playback. Kultur24 window1 retained a transport
timeout/reconnect:26.9042s PCM/32.732s board,3140 DMA misses. Window2:
28.089333s PCM/27.998s board,23 misses; stage snapshots attributed24 to
decode-wall and none to input wait/read/output. Snapshots are asynchronous;
decode-wall includes queue backpressure/preemption, not just CPU execution.
Free heap7304 to6656B, queue error0. Do not hide startup/reconnect failures.
No acoustic qualification. Default profile unchanged.
