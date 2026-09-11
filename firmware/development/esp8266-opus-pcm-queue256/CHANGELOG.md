# Diagnostic Opus PCM queue / DMA256

2026-09-11, source27f0818. App889408B. Experimental, not production-qualified.

- Two960-sample PCM16 mono slots (3840B) replace the single1920B workspace.
- Separate priority6 output consumer with2048B stack, no PCM ring copy.
- Two256-word I2S PDM32 DMA buffers (2048B total), GPIO3/RX.
- CPU160MHz, QIO40MHz; input1024B, scratch6144B, unchanged4096B reserve.
- Receive inactivity timeout3000ms; diagnostic Opus endpoint and SDK RX stats.
- Lease/trim/OOM/stop ownership tests pass;12/12 pristine PCM comparisons exact.
- DMA256/512/768 writer tests are bit-exact; actual queue passes ASan/UBSan.
- New health counters are output progress, not enqueue progress. Output timing
  is wall time, not CPU utilization. Production defaults remain unchanged.

Build command:

```powershell
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-opus-pcm-queue256 -Diagnostic -EnableOpus -OpusStreamTest -NoSpiffsCache -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -Pdm32Iram -Pdm32Batch -SdkRxDiag -DmaBufferWords 256 -StreamIdleTimeoutMs 3000 -OpusPcmQueue
```

Board evidence will be retained beside this file. No UART recovery is authorized.

## Hardware qualification: failed

OTA to0x110000 succeeded. Remote Plaza10/10 commands accepted,0 qualified
continuous windows. LAN CELT64 likewise10 accepted,0 qualified;9 start-status
replies report decoder-init error. All attempts, including missing samples,
are retained. Queue output counters advanced only briefly. No CPU-speed or
audio-quality improvement is claimed.

Consumer stack minimum1672B free, main audio1496B free; local boot-lifetime
heap minimum4004B. Scratch allocation6144B failed with8304B total DRAM free
(stage8), suggesting fragmentation; largest block was not measured.
Total RAM is not reduced:1968B static savings are outweighed by1920B extra
PCM,2048B task stack and TCB. Production defaults remain unchanged.

See `docs/ESP8266_OPUS_PCM_QUEUE.md` for reset/timing caveats and next gates.
The exact pre-test DMA512 image is restored via app-only OTA; its result and
final status are saved here. This candidate must not replace production.
