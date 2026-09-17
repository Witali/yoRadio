# App PCM / DMA512 / input1KiB — 2026-09-17

All18 accepted ASM stages, CPU160/QIO40, I2S PDM32 GPIO3, app PCM2x960,
DMA2x512, compressed input1024, scratch6144/reserve4096, LED OFF.
Clock compensation OFF. Source24243cc0. OTA PASS.

**Rejected.** Kultur24 briefly decoded, then transport timed out and the
reconnect hit stage10(reserve). SnapshotfreeDRAM4000B, required4096B;
the details field sampled4060B, largest2664B. Do not lower the guard.
First health response timed out; final PCM age23600ms, queue error0,
WebUI DECODER INIT ERROR. Retain the missing/failed window as a failure.
Boot minimum3824B, stopped free27200B. Larger DMA was not a fix.

Application/settings/playlist partitions were not erased. No UART used.
Not promoted to default. No acoustic qualification.
