# Diagnostic low-RAM Opus with PCM queue — NOT qualified

2026-09-13, source c470f55, 891936-byte application, CPU160/QIO40.
I2S PDM32 GPIO3/RX, DMA2x256, PCM2x960 mono, consumer stack1536.
SILK lending, compact autocorrelation, word-safe PLC IRAM; scratch4352.
Opus reserve4096 and protected main stacks are unchanged. No partition,
SPIFFS, Wi-Fi or UART writes were performed; application-only OTA was used.

Host PCM/guards/leases/ASan checks pass. Physical LAN CELT64: **0/10**
continuous windows qualified. Some starts output PCM, but OOM/fragmentation,
receive stalls and HTTP observation timeouts remain. This is not a production
default and is not evidence of uninterrupted Opus playback.

See [analysis](../../../../docs/ESP8266_OPUS_PLC_IRAM.md).
Results: `live-results/`, `ota.json`, `stop.json`, `fixture-trace.zip`.
