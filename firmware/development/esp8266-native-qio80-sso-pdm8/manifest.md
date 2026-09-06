# ESP8266 native QIO80 MP3 SSO + I2S-PDM8 development artifact

- Built: 2026-09-01
- Target: Wemos D1 mini / ESP8266EX
- CPU: 160 MHz
- Flash: 4 MiB, QIO at 80 MHz
- SDK: ESP8266 RTOS SDK v3.4, GCC 8.4, release optimization
- Source: `esp8266/rtos-sdk-native`
- Profile: board default `sdkconfig.defaults`
- Decoder: Helix MP3/AAC with `CONFIG_YORADIO_HELIX_MP3_SSO=y`
- Audio: mono I2S-PDM DATA on GPIO3/RX, PDM8
- I2S carrier: 1,538,461 Hz (48,076.9 32-bit words/s)
- Effective PDM transition rate: 384,615 Hz

This production-profile build makes continuous I2S/SLC-DMA PDM the default
audio backend. Its local output-only backend follows the architecture used by
ESP8266Audio/ESP8266 Arduino core: four static circular buffers of 128 32-bit
words, a companion SLC link, DMA mode 1, BBPLL audio clock and EOF task
notification. Buffers are primed with neutral `0xAAAAAAAA`; initialization
fails if DMA does not return its first descriptor within 100 ms. GPIO15/BCLK
and GPIO2/LRCLK are routed to make the hardware clocks run; only GPIO3/DATA is
connected to the RC audio filter.

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

- `app.bin` (668,992 bytes): `78B2E1FCCE4490345E185F2C81EEE0952258F013F8D06D12FB850C2B6DBA4E31`
- `bootloader.bin` (7,808 bytes): `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85`
- `partition-table.bin` (3,072 bytes): `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF`

Validation:

- The generated `sdkconfig` selects QIO 80 MHz, CPU 160 MHz,
  `CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y` and
  `CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8=y`; legacy SPI-PDM is disabled.
- The release build completed successfully with no GPIO16 control.
- The focused I2S-DMA tests passed: 5/5.
- All repository tests passed: 275/275.
- This exact image was flashed and hash-verified on Wemos D1 mini
  `48:3f:da:18:f0:35`. The 100-ms hardware DMA self-test passed, Wi-Fi obtained
  `192.168.100.6`, HTTP status and WebSocket responded, station 502 returned
  HTTP 200/ICY metadata and initialized the Helix MP3 workspace. No I2S DMA
  write timeout or reset loop occurred during the short test.
- Long-duration listening and the complete MP3/AAC bitrate matrix remain open.
