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

- `app.bin` (672,480 bytes): `B55B7CACAE18F2C369053274F4B083C5BB8D9C35ED700B52D1B87972DC956157`
- `bootloader.bin` (7,808 bytes): `34A628DA55749D0C72ED3BC78EDA60B29DE6D341A8E54E70AE05CFF772219A85`
- `partition-table.bin` (3,072 bytes): `C3AEC2B0CC450D37286B5D832556268970CF0F63AA31250C94A21116D22A22DF`

Validation:

- The generated `sdkconfig` selects QIO 80 MHz, CPU 160 MHz, MP3 SSO and
  `CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8=y`; PDM16 is disabled.
- The deterministic MP3 fixture retained all frames and samples. MP3 SSO
  measured 48.50 dB SNR against exact Helix, with maximum error of 34 signed
  16-bit PCM levels.
- The SPI transfer ISR now notifies the producer only while it is blocked,
  preventing stale task notifications from accumulating.
- The production PDM path uses a direct 95-byte IRAM HSPI ISR instead of the
  generic SDK SPI dispatcher. Its common C prologue has a 16-byte frame and
  saves only `a0`; the rare producer wake/yield is a separate noinline path.
- Physical SDK-dispatcher versus direct-ISR A/B retained 96.8% realtime and
  reduced the average 512-bit inter-block gap from 7,423 to 7,393 CPU cycles
  (46.39 to 46.21 us). A high/low FIFO ping-pong experiment was rejected
  because it doubled the interrupt rate and reduced realtime to 93.7%.
- A generated-PCM physical run completed at 96.8% realtime with zero invalid
  queue events. Full 320-kbit/s profiles reached 95.2% realtime for MP3 and
  77.0% for AAC; see `docs/ESP8266_AUDIO_PROFILE.md` for stage timings.
- The profile and decode-only binaries were flashed and exercised on the
  Wemos D1 mini. This archived image is the rebuilt production profile without
  runtime statistics or decoder-stage logging.
- All 270 repository tests passed. The archived production image associated
  with Wi-Fi `DYACHENKO`, obtained `192.168.100.6`, initialized SPI-PDM8, and
  returned HTTP 200 for the WebUI root page.
