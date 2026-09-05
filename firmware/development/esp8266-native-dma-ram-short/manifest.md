# Diagnostic: RAM decode with committed-prefix and short-neutral recovery

2026-09-05 development snapshot based on `7f10ef6`; tested code subsequently
committed as `aab3600`. RAM benchmark/real output ON, prefix and short retry
ON, Wi-Fi/profile/trace OFF. CPU160/QIO40, mono Helix SSO/AAC, GPIO3 PDM32,
2 x 512-word capacity. Test volume128 and normalization off exist in RAM only.

App: 282880 bytes. SHA-256:
`128471F88F51ECCC421E8D1588542FA76ED74099425BC5EFE7165B44215CDB3C`.

MP3: 4.800/4.785525 s audio/wall, zero underruns. AAC: 4.266666/4.259223 s,
four short 64-word neutral retries. FIFO-empty=0. IRAM arena16384, task stack
headroom1496, lifecycle heap restored. This proves approximate realtime for
these isolated frames, not uninterrupted RF streaming or acoustic quality.
Ordinary firmware restored. [Results](../../../docs/ESP8266_DMA_STARVATION_RECOVERY.md).
