# RX16 with PCM queue — 2026-09-17

Experimental ordinary radio, all18 accepted ASM stages. RX16/continuous16,
TCP536/window2440/OOSEQ ON, PCM2x960 mono, worker1536B, DMA2x128 words,
I2S PDM32 GPIO3, CPU160/QIO40. Input1024/scratch6144/reserve4096 unchanged.
App890240B; exact SHA, configuration and loaded-byte proofs in this directory.

OTA succeeded. DLF24: **0/10 qualified**, six incomplete measurement windows.
Three complete windows had zero PCM progression; the fourth advanced833.5ms
in26977ms then stopped. Stage10 reserve refusals; boot minimum heap2984B.
Neutral DMA events while stopped are not active-audio dropout measurements.
No demonstrated playback or WebUI improvement, no acoustic qualification.
This experiment is NOT selected as the board default.
