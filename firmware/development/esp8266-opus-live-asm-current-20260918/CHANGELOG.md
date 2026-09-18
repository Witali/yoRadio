# 2026-09-18: current ordinary radio with accepted Opus ASM

Source: `a82a4551bb4579e97ff0dd84ff7f1a06ab928db1`.
This is the ordinary native radio with WebUI and I2S PDM, not a raw-codec
benchmark or tone generator. Opus remains an experimental/diagnostic build
option; this artifact is not a claim of release qualification.

## Included

- Frozen LX106 Opus ASM and the full accepted eBands-final chain of 18
  post-link transformations. `preflight.json` lists every transformation,
  rebased address, hash and unchanged-function comparison.
- Existing word-access ASM, ICDF/FIR flash access and fixed-point decoder.
- Current reconnect/DRAM-reserve corrections and the detection-cancellation
  fix `0edf328d`, which was absent from the prior heapreserve binary.
- Helix MP3 SSO and AAC remain enabled; the C Opus fallback is unchanged.

Rejected quant-decode, quant-flags, quant-locals, allocation-decode and
eBands-SRC experiments are not added. "All optimizations" means all accepted
compatible changes, not every tested candidate.

## Unchanged hardware and memory profile

CPU 160 MHz, runtime QIO 40 MHz, mono I2S PDM32 on GPIO3/RX, nominal carrier
1.536 MHz. PCM queue uses two 960-sample slots; DMA uses two 128-word buffers.
Opus input is 2048 B, scratch 6144 B; the shared network input is 4096 B.
The existing app task consumes PCM; no additional PCM task stack is allocated.
PDM IRAM/batch output and physical-clock compensation remain enabled.

LED, SPIFFS logging/export, memory profiling, function/stage profiling,
FreeRTOS runtime statistics and all benchmarks are disabled. Existing
diagnostic stream/RX counters remain enabled as in the previous image.
The compatibility DIO image header is intentional; the existing SDK
bootloader enables the configured QIO runtime mode.

## Reproduce the build (PowerShell from this worktree)

Use fresh variant names if rebuilding changed sources; never overwrite
evidence from a different build. The base image is intermediate, not the
final accepted-ASM image to upload.

```powershell
& tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 `
  -SdkPath C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk `
  -RuntimeRoot C:/Work/yoRadio/.build `
  -Variant esp8266-opus-live-asm-current-base-20260918 `
  -Diagnostic -EnableOpus -OpusBackend bands-tell-inline-asm `
  -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -OpusInputBytes 2048 `
  -NoSpiffsCache -NoAudioLevelLed -Pdm32Iram -Pdm32Batch -Pdm32ClockCompensate `
  -OpusPcmQueue -OpusPcmAppTask -DmaBufferWords 128 `
  -SdkRxDiag -OpusStreamTest -StreamIdleTimeoutMs 3000
node tools/esp8266_opus_asm/live_variant_v2.cjs `
  esp8266-opus-live-asm-current-base-20260918 `
  esp8266-opus-live-asm-current-20260918
```

Deploy only `app.bin` through native `POST /update`. No bootloader,
partition table, NVS, Wi-Fi, playlist or SPIFFS image is part of this update.
No UART command or serial reset is used.

## Build and deployment result

Final app: **890336 bytes**, SHA256
`c63a757ccab9dd2f2ab02159cce88ac5a5500e65383d7ff46808165f7f3bfbd3`.
All 18 relocated transformations pass inherited semantic checks and exact
accepted function-graph comparisons. Static RAM and stack delta: zero.
Compared with the previous heapreserve image, flash text/app size shrank
16 bytes; IRAM code/BSS and DRAM data/BSS section sizes are unchanged.
Thirteen lifecycle/reconnect/literal-audit regressions pass without skips.

OTA returned HTTP200/OK and boot was independently confirmed in slot
0x110000 (previously 0x10000). HTTP status, WebSocket getindex and playlist
requests succeeded. Playlist wire hash is unchanged. These boot/deployment
checks passed; they do not assert continuous playback.

The playback smoke test is a **known failure**, preserved without retries
of Play or excluded observations:

- Sent `play=513` for the existing station named Nightwave Plaza 128 kbps.
  The following status request timed out. The station name is not a verified
  fixed bitrate; later status reported OPUS/64 kbps.
- After 65 seconds without requests from the runner, a complete autonomous
  25007-ms window contained 1113088 PCM frames at 48 kHz (23189.33 ms,
  ratio 0.927314), with 1419 DMA underruns. Continuity failed.
- The first Stop WebSocket timed out. The next snapshot showed stopped with
  CONNECTION ERROR, combined free heap 26568 B and boot minimum 452 B.
  No Opus init failure was latched (`stage=0`). A later memory snapshot
  reported current byte-addressable DRAM 29104 B, largest block 27036 B.
  These sequential observations do not identify the cause or prove no leak.
- An idempotent Stop cleanup succeeded. Final HTTP/WS/playlist snapshot:
  stopped, no error, RSSI -58 dBm, combined free heap 28832 B, slot 0x110000.
  Original station/volume are retained. The new app remains installed.

No acoustic recording was made. CPU75%, uninterrupted playback and full-radio
fragmentation qualification remain open. The cancellation fix is now in a
booted physical image, but its exact race/cancellation path has only host
regression coverage, not a targeted on-board fault-injection proof.

All attempts are saved here (`play.json`, `quiet.json`, `stop.json`,
`final.json`, `memory-after-play.json`, cleanup snapshots), together with
build proof, SDK configuration, logs and OTA evidence. Deployment regression
tests check image/hash/graphs/profile/OTA and retain the playback failure.
