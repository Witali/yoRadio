# ESP8266 native — I2S RCPDM32 development artifact

- Built: 2026-09-05
- Source revision: `591b4bd`
- Target: ESP8266EX / Wemos D1 mini, 4 MiB flash
- SDK: ESP8266 RTOS SDK v3.4, Xtensa GCC 8.4.0
- Profile: `esp8266/rtos-sdk-native/sdkconfig.i2s-rcpdm.defaults`
- CPU/flash: 160 MHz / QIO 40 MHz (SDK-compatible DIO boot header)
- Audio: Helix MP3 SSO + AAC; mono I2S RCPDM on GPIO3
- Modulation: 32 bits per nominal 48-kHz output PCM sample, alpha=1/16
- Carrier: nominal 1.536 MHz, divider 8 x 13 gives 1.5384615 MHz
- DMA: existing 2 x 512-word SLC ring
- Build: main `-O3`, diagnostic logging enabled; no tone test or profiler
- App offset: `0x10000` with the existing native partition layout
- File: `app.bin`, 670000 bytes
- SHA-256: `A8625F64050EC4E05BA7EE00CBF857BA56D0DF6D352C063A68B7B40C9DCF42FA`

## Changes

- Added a separate compile-time I2S RCPDM output without replacing the normal
  I2S PDM default, the MP3/AAC decoders, WebUI, sample pacing or DMA driver.
- Predictive RC uses one uint32_t state and 32 decisions per word. The constant
  charge/discharge distance is bit-exact with the supplied two-candidate model.
- No extra PCM/PDM buffers, allocation or ISR work. Static RAM is unchanged:
  DRAM data 1640 + bss 18600 bytes; IRAM text 23096 + bss 4040 bytes.
- Existing gain, normalization, balance, stereo-to-mono and resampling remain.
- Matched starting filter: 1 kohm + 10 nF, followed by AC coupling into a
  high-impedance amplifier input; see the [design notes](../../../docs/ESP8266_I2S_RCPDM.md).

## Validation and limitations

- 304 repository regression tests passed. New C tests compare 493216 words
  with an independent reference, plus silence, rails and reset checks.
- GCC ASan/UBSan passed. Xtensa packer has no division, 64-bit arithmetic,
  calls or extra stack frame; conversion remains in the audio task.
- Both the RCPDM firmware and ordinary-PDM output/application objects compile.
- This experimental variant has NOT been flashed or acoustically tested.
  Real-time CPU load, underruns and analog SNR/THD still need physical testing.
- The build identity contains `-dirty` because unrelated Arduino WebRadio
  changes were present in the repository; they are not inputs to this target.
- SPIFFS/NVS and the previous default firmware artifact are untouched.
