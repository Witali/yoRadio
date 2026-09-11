# Diagnostic Opus PCM queue, DMA256, consumer stack1536

2026-09-11, source0fb3e1b, app889872B. Not production-qualified.

- Two960-sample PCM16 mono slots and two256-word DMA buffers, GPIO3/RX.
- Consumer stack1536B (512B less than previous experiment); main audio5120B.
- Unchanged Opus scratch6144B, input1024B and post-init reserve4096B.
- CPU160, QIO40, standard PDM32; receive inactivity3000ms.
- First init-failure diagnostic records total and largest free DRAM before
  cleanup. Current heap snapshot available on diagnostic Opus endpoint only.
- Host ownership/error tests pass for both consumer stack variants; heap walk
  passes ASan/UBSan. No Opus/PDM math or PCM values changed by this build.
- Target individual stack frames saved in target-stack.json. These are not
  complete call-chain or interrupt-stack bounds; board watermarks required.

Build:

```powershell
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 -Variant esp8266-opus-pcm-queue256-stack1536 -Diagnostic -EnableOpus -OpusStreamTest -NoSpiffsCache -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -Pdm32Iram -Pdm32Batch -SdkRxDiag -DmaBufferWords 256 -StreamIdleTimeoutMs 3000 -OpusPcmQueue -PcmStackBytes 1536
```

The baseline DMA512 traces describe a previous image, not this candidate.
TCP_INFO bytes accepted by the sender are not board-received bytes. Wall-time
profile percentages are not task CPU usage. Board results follow separately.

## Board outcome: failed, previous image restored

All10 LAN starts accepted;0 qualified. Nine attempts failed the4096B reserve
guard after init (free CAP81456..3288B; largest964..2140B). Attempt10 spanned
a WDT reboot (SDK reason7), precise cause unknown. Do not call these idle DMA
counters audio performance or infer a speed-up. Consumer stack watermark1160B,
main1496B, observed only after short exploratory output. Boot heap low1280B.

`qualification.json`, `local-series/`, `local-first.json` and TCP source trace
retain failures. Exact b77b61c DMA512 restored by app-only OTA to0x10000;
`restore-dma512-ota.json` and `final-status.json` confirm HTTP access and Stop.
Production defaults remain unchanged; do not deploy this candidate as a fix.
