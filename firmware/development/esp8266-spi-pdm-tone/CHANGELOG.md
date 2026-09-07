# ESP8266 SPI-PDM 1 kHz tone test

## 2026-09-07

- Temporary Wemos D1 mini test: existing sine generator -> production audio
  output -> asynchronous HSPI PDM8 -> **D7/GPIO13**. I2S is disabled; RX/GPIO3
  is not the audio output. D5/GPIO14 is the SPI clock, not analogue audio.
- 48 kHz PCM, 48 samples per sine period, full-scale 1 kHz sine, 500 ms on /
  500 ms neutral silence. The actual SPI carrier is 384615 Hz. Block gaps can
  affect analogue timing; this test does not certify an oscilloscope frequency.
- Wi-Fi, WebUI and radio decoders are intentionally not started. This image
  is for listening to the output, not for diagnosing WebUI while it runs.
- Normalization off, volume 254, balance zero **in RAM only**. No stored audio
  settings are changed by the generator. Start with low amplifier gain.
- Keep the RC filter and AC coupling into a high-impedance amplifier input;
  do not connect a low-impedance speaker directly to a GPIO.
- CPU 160 MHz, QIO 40 MHz, app.bin 128064 bytes; SHA-256:
  `87507D2FC34B5C32EAF336002D2FE4598512DD8138FC6E1E2F8E7CE4952C70FC`.
- Source revision/config identity: see `manifest.json` and `sdkconfig`.
  Build flags enable both AUDIO_OUTPUT_BENCHMARK and AUDIO_OUTPUT_TONE_TEST;
  OUTPUT_COMPARE is off. Ordinary I2S board defaults are unchanged.

Rebuild from repository root (does not flash):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/esp8266_audio_profile/build_spi_pdm_debug.ps1 -ToneTest
```

## Installation and verification

- Full 4 MiB flash backup taken privately before installation. Partition table
  and OTA CRC checked: active app0, entries seq 2 and 3 valid.
- Wrote only app0 at 0x10000; esptool verified the written hash. Bootloader,
  OTA selection, NVS, PHY and SPIFFS were not written. Do not use a generic
  whole-project flash command that writes initial OTA data.
- UART boot confirms `SPI-PDM: mono GPIO13/D7, 384615 Hz, 8 bits/sample` and
  `tone test: 1000 Hz ... 500 ms on / 500 ms silence`. No PCM output failure
  was observed during the 25-second capture. The user reports a thin squeal
  and a loud interrupted tone. This confirms an audible output path on D7,
  **not clean audio**: the extra squeal remains unexplained. Possible sources
  include PDM8 noise/filtering or SPI inter-block gaps; no oscilloscope or
  spectrum measurement was performed to distinguish them.
- 18 generator/SPI regression tests pass. Another 3 HTTP tests passed for
  the prepared normal SPI radio build; those are not active in this tone image.
- Logs and credential-bearing backup stay under ignored
  `.build/webui-diagnostic-20260907/`; never publish that backup.

The ordinary SPI radio is separately saved at
`../esp8266-spi-pdm-debug/app.bin`. Do not restore it automatically before the
user has finished listening to this tone test.
