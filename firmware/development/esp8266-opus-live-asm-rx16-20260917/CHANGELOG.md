# RX16 with synchronous PCM — 2026-09-17

Control without the extra PCM worker: all18 accepted ASM stages, ordinary
radio, RX16/continuous16, TCP536/window2440/OOSEQ ON, DMA2x512 words,
I2S PDM32 GPIO3, CPU160/QIO40. Input1024/scratch6144/reserve4096 unchanged.
App886256B; exact SHA, configuration and loaded-byte proofs in this directory.

OTA succeeded. DLF24: **0/10 qualified**, six incomplete measurement windows.
Four complete windows had zero PCM progression after init errors. Returned
diagnostics show stage10 reserve refusals; boot minimum heap3456B.
The first status did show playing at24kbps, but its continuity window was
incomplete. Do not present that status as continuous playback proof.
Neutral DMA events after failure are not active-audio dropout measurements.
RX16 is NOT selected as the board default. No acoustic qualification.
