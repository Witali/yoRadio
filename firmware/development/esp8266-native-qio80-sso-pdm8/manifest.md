# ESP8266 native QIO80 MP3 SSO + SPI-PDM8 development artifact

- Built: 2026-09-01
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: 4 MiB, QIO at 80 MHz
- SDK: ESP8266 RTOS SDK v3.4, GCC 8.4, release optimization
- Source: `esp8266/rtos-sdk-native`
- Profile: `sdkconfig.helix-sso-qio80-pdm8.defaults`
- Decoder: Helix MP3/AAC with `CONFIG_YORADIO_HELIX_MP3_SSO=y`
- Audio: mono SPI-PDM on GPIO13/D7, 8 bits/sample
- PDM bit clock: 384,615 Hz (48,076.9 PCM samples/s)

This experimental complete radio/WebUI build halves the SPI-PDM oversampling
ratio from 16 to 8 without changing the normal profile. The 80 MHz APB clock
uses an HSPI pre-divider of 26 and an 8-cycle bit divider:
`80,000,000 / (26 * 8) = 384,615.38 Hz`. This keeps the same +0.16% PCM
sample-rate error as the 769.231-kHz PDM16 profile.

PDM8 approximately halves sigma-delta conversion work and SPI transfer
interrupt frequency. Each 512-bit queued block grows from about 0.67 ms to
1.33 ms, so the 12-block output queue covers about 16 ms. The lower
oversampling ratio also raises one-bit quantization noise and may require
checking the analogue RC filter and amplifier on the physical board.

Flash all three images without erasing NVS or SPIFFS:

- `bootloader.bin` at `0x0000`;
- `partition-table.bin` at `0x8000`;
- `app.bin` at `0x10000`.

SHA-256:

- `app.bin` (673,312 bytes): `62024F4CEC6DE4CE12BF7496CD36DA63F4D439C380FF89AC029AA7CB036C8BB9`
- `bootloader.bin` (7,808 bytes): `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85`
- `partition-table.bin` (3,072 bytes): `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF`

Validation:

- The generated `sdkconfig` selects QIO 80 MHz, CPU 160 MHz, MP3 SSO and
  `CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8=y`; PDM16 is disabled.
- The deterministic MP3 fixture retained all frames and samples. MP3 SSO
  measured 48.50 dB SNR against exact Helix, with maximum error of 34 signed
  16-bit PCM levels.
- All 267 repository tests passed.
- This artifact was compiled and archived but was not flashed during this
  build. Its physical audio noise and end-to-end CPU load remain to be
  measured before promoting PDM8 to a normal profile.
