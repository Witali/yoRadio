# App PCM consumer with 2 KiB compressed input — 2026-09-17

Only input capacity changes from apppcm:1024 to2048 bytes. No new PCM task,
DMA2x128, leased PCM2x960 mono, LED OFF. All18 accepted ASM stages,
CPU160/QIO40, I2S PDM32 GPIO3, RX14, TCP536/window2440/OOSEQ ON.
Scratch6144 and reserve4096 remain unchanged. OTA passed.

Kultur24: initial observation crosses startup. Steady windows produced
28.000s PCM/28.004s with94 underruns, then27.9893s/27.996s with97 underruns.
Neither qualifies as zero-gap playback. Free heap samples6584..7336B;
boot minimum4212B. App/output stack1632B, audio1432B, queue error0.
After sample:TX1408 completions, zero failed completions, RSSI-43dBm.
These conditions differ from earlier trials; no isolated CPU/LED claim.
All observations in board/. Build is experimental, not the default.
