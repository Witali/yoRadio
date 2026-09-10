# FIR ON physical-output diagnostic — 2026-09-10

Source3f72f25, app912496B, CPU160/QIO40. Same exact FIR-word candidate;
own raw packets from flash → decoder → normalization → PDM32 → real I2S DMA.
One1200-packet/24-second-PCM run per mode. All five PCM hashes match.
**All five continuity gates failed.** DMA misses56/556/1221/6582/16623;
minimum free DRAM320B, HTTP observation timeouts/reset retained inrun1.json.
Not qualified for normal use. OTA app-only; subsequently replaced by live
diagnostic without benchmark fixtures/task/runtime stats. No SPIFFS changes.

See [complete results](../../../docs/ESP8266_OPUS_FIR_WORD_BENCHMARK.md).
