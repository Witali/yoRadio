# App PCM / DMA192 — 2026-09-17

Same accepted18 ASM stages and appdiag profile, but two192-word DMA buffers
instead of128 (+512B DRAM). OTA PASS, source55517ea9. Input2048,
scratch6144, reserve4096; CPU160/QIO40, I2S PDM32 GPIO3, LED OFF.

Kultur24 first window crossed startup. Stable window2:27.880s PCM in28.004s,
188 DMA underruns (117 attributed approximately to input wait,36 decode
wall interval,29 read,3 output; health/profile snapshots are not atomic).
Heap6788 to6152B, boot minimum3824B, queue error0. Service3 lifetime misses;
its unsigned maximum was invalid after a small SDK clock backward step.

NOT qualified and not selected as default. Divisibility of960 by192 did
not establish continuous playback. Preserve both windows and final state.
