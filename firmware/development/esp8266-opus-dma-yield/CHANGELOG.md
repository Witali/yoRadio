# ESP8266 Opus DMA-aware yield A/B — 2026-09-10

Diagnostic candidate only, **not recommended for production**. Source `bd95aca`.
Its source change was subsequently removed because no reliable continuity gain
was demonstrated. See [full results](../../../docs/ESP8266_OPUS_DMA_YIELD_EXPERIMENT.md).

Build: `tools/esp8266_audio_profile/build_i2s_pdm_production.ps1
-Variant esp8266-opus-dma-yield -EnableOpus -OpusWordAsm -Diagnostic
-OpusStreamTest -WebAudioPause off -NoSpiffsCache -Pdm32Iram -SdkRxDiag
-Pdm32Batch -OpusDmaYield` at source revision `bd95aca` (one command).
The removed switch is available by checking out that historical revision.

Application 884016 bytes; manifest holds SHA-256 and source/settings hashes.
OTA HTTP 200 OK; app slot changed 0x110000 -> 0x10000. No filesystem image,
credentials, serial commands or computer Wi-Fi changes.

Same PCM48k mono, I2S PDM32 GPIO3, 2 x 512-word DMA, CPU160/QIO40,
1024-byte Opus input, 6144-byte scratch. 387-byte ISR unchanged; IRAM unchanged;
DRAM BSS +16 bytes, application +256 bytes relative to batch-resume.

SILK12: 24/19 underruns over two 27-second windows; baseline steady window 22.
About 1337 redundant sleeps omitted per window, but all continuity gates still
failed. CELT64 produced only 17.53 seconds of PCM during 26.97 seconds and had
RX timeout/reconnect. All failed windows are preserved in `results/`.
No analog sound-quality measurement and no claim of improved decode CPU.
