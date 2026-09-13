# Diagnostic Opus ASM inner4 experiment

Not an ordinary radio release. This app runs the raw Opus benchmark, with
physical audio output off during measurement. Board defaults are unchanged.
Rejected: 30 A/B/A runs gave CPU192 88.103 / 94.984 / 88.120%. Exact PCM,
same RAM/stack, but 7.81% longer decoding time than the first control.

- Parent: `esp8266-opus-bands-tell-inline-v1`, best measured ASM control.
- Candidate: `bands-inner4-asm`; energy inner product in `renormalise_vector`
  expands by four for N>=8. No new buffer, table, static RAM or stack.
- `app.bin`: 903280 bytes, SHA256
  `f5f698a8bbe33a7d3aba466f5764d2396e5c44b93b49a4a4802bef081b39d658`.
- Build source HEAD `f81ab121` with the overlay then committed as `b6217542`.
  Exact source/recipe/parent hashes are in the build and overlay manifests.
- CPU160, QIO40, O3, same fixtures/config as control; no function/stage profiler.
- 56 Node tests, 6162 actual-instruction cases and host ASan/UBSan exact PCM,
  including 320/510 kbit/s and PLC/reset/OOM. See `correctness.json` and logs.
- `census.json` records dynamic vector lengths on the host, with explicit
  audio duration. It is not target timing and adds no counters to firmware.
- `preflight.json` verifies linked loop, unchanged other hot graphs, profile
  parity and static sections. Image +64 bytes versus control.

Physical A/B/A results and final restore are recorded in
[the experiment report](../../../docs/ESP8266_OPUS_ASM_INNER4.md).
`controls/before`, `runs`, `controls/after` retain all 30 numbered attempts.
`comparison.json` applies the existing relative high-bitrate acceptance rule.
`ota-restore.json` and `restored-snapshot.json` confirm ordinary I2S PDM
radio restored in slot0x110000, with the initial stopped state retained.
Root HTTP200, playlist and six WebSocket index messages verified; no live
playback qualification for this rejected candidate.

Rebuild from the worktree root (paths below refer to the existing local SDK):

```powershell
tools/esp8266_audio_profile/build_i2s_pdm_production.ps1 `
  -SdkPath C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk `
  -RuntimeRoot C:/Work/yoRadio/.build -Variant esp8266-opus-bands-inner4-v1 `
  -Diagnostic -EnableOpus -OpusBackend bands-inner4-asm `
  -OpusWordAsm -OpusIcdfFlashWord -OpusFirFlashWord -NoSpiffsCache `
  -Pdm32Iram -Pdm32Batch -OpusBenchmark `
  -OpusBenchmarkFixtures firmware/development/esp8266-opus-asm-library/fixtures
```

Only use the native application OTA endpoint. No UART/USB reset, bootloader,
partition-table or SPIFFS flashing is part of this experiment.
