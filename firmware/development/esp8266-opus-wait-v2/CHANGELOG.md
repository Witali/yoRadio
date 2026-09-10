# Split-wait diagnostic (pre-clock-fix), 2026-09-10

Source9c67eb6, app885424 bytes, CPU160/QIO40, I2S PDM32 GPIO3,
2x512-word DMA, Opus input1024/scratch6144. Accepted word/ICDF/FIR paths ON;
rejected reciprocal/decoder-only and unqualified rotation ASM OFF.
Application-only OTA succeeded. No SPIFFS/playlist/Wi-Fi changes or UART use.

Adds16B DRAM BSS (18504→18520); IRAM sections unchanged. Flash text+32B,
rodata+24B versus ff49a46. Scheduling/output/decoder are unchanged.

Ten sequential DLF24 HTTP windows were attempted; **0/10 qualified**.
Runs2/3 have missing HTTP observations, retained as failures. Available
windows have70..1598 added DMA misses. Post-decode pacing had zero attributed
misses in all eight observed windows; input waits, decode/output and transport
reconnect/unattributed work account for the interruptions. Do not equate
unattributed events with a proven network cause. Minimum sampled heap6028B;
this is not a worst-case free-block or memory-leak proof.

The SDK clock was observed going backwards: maximum read4294967115us.
`reanalysis.json` flags contaminated wall timing while retaining every raw
snapshot and DMA count. This is **not** a71-minute measured stall. The clock
read race is fixed subsequently in5147be3; this binary intentionally preserves
the original experiment and MUST NOT be promoted as a playback fix.

`pre-v2-startup.json` and `pre-v2-steady.json` are earlier ff49a46 observations,
not same-image comparison rows. Host lifecycle/diagnostic tests are retained
separately. See [wait investigation](../../../../docs/ESP8266_OPUS_WAIT_REASONS.md).
