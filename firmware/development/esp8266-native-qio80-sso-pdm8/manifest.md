# ESP8266 native QIO80 MP3 SSO + I2S-PDM8 development artifact

- Built: 2026-09-01
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: 4 MiB, QIO at 80 MHz
- SDK: ESP8266 RTOS SDK v3.4, GCC 8.4, release optimization
- Source: `esp8266/rtos-sdk-native`
- Profile: `sdkconfig.helix-sso-qio80-pdm8.defaults`
- Decoder: Helix MP3/AAC with `CONFIG_YORADIO_HELIX_MP3_SSO=y`
- Audio: mono I2S-PDM DATA on GPIO3/RX, 8 bits/sample
- PDM bit clock: 384,615 Hz (48,076.9 PCM samples/s)

This production-profile build makes continuous I2S/SLC-DMA PDM the default
audio backend. Four circular buffers of 128 32-bit words are primed with the
neutral `0xAAAAAAAA` bit pattern. An incomplete 32-bit PDM word is retained
across decoder callbacks, so PCM block boundaries do not add padding gaps.
Only the DATA signal is routed: GPIO15/BCLK and GPIO2/LRCLK remain GPIOs.

GPIO3 is also UART0 RX. Firmware does not read UART input in this mode and does
not control GPIO16. The installed 470-ohm series resistor is the only current
limiter between the USB-UART bridge and GPIO3; the host must not transmit UART
data while audio is active. UART0 TX logging on GPIO1 remains available.

Legacy HSPI-PDM on GPIO13/D7 and standard PCM I2S for an external DAC remain
selectable at build time. PDM8 approximately halves sigma-delta work relative
to the earlier PDM16 profile, at the cost of greater one-bit quantization noise.

Flash all three images without erasing NVS or SPIFFS:

- `bootloader.bin` at `0x0000`;
- `partition-table.bin` at `0x8000`;
- `app.bin` at `0x10000`.

SHA-256:

- `app.bin` (673,616 bytes): `0C67351D5446EBCB8A2C89B7811200D8D94370B7B0033F4D57CBDCB3BD5CD8D4`
- `bootloader.bin` (7,808 bytes): `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85`
- `partition-table.bin` (3,072 bytes): `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF`

Validation:

- The generated `sdkconfig` selects QIO 80 MHz, CPU 160 MHz,
  `CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y` and
  `CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8=y`; legacy SPI-PDM is disabled.
- The release build completed successfully after removing all GPIO16 control.
- The focused I2S/SPI-PDM tests passed: 19/19.
- All 274 repository tests passed.
- This exact I2S-PDM image has not yet been flashed or audio-tested on the
  physical Wemos D1 mini.
