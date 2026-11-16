# CYD static TLS RX on all three audio outputs

The full application ran from `bb0e931bb` on dual-core ESP32 QEMU with
ESP-IDF 6.0.2, the ST7789 status display and diagnostic OpenETH. The
generated SDK configurations differed only in audio-output selection.
Each enabled static TLS RX reservation and the default two-channel limit.
Each used TCP window/mailbox 8640/8, the five-second task watchdog and
the 300 ms interrupt watchdog. Idle input reclaim and early MPI mutex
initialization were disabled for this comparison.

| Audio output | Output at EOF | Minimum free heap | Lowest sampled value of the largest free DMA block during playback |
| --- | ---: | ---: | ---: |
| PDM | 1,058,176 driver bytes | 13,196 B | 17,408 B |
| Continuous DAC | 528,000 decoded PCM frames | 13,864 B | 18,432 B |
| Legacy DAC | 528,000 decoded PCM frames | 9,908 B | 17,408 B |

All three received the complete 706,319-byte stereo Ogg stream over
verified TLS 1.2 with 43 full 16,384-byte body records and a 1,807-byte
tail. WebUI served the same 13,588-byte gzip asset before playback, during
PCM progress and after EOF. The driver accepted every requested byte.
There were zero allocation failures, OpenETH RX waits, output errors,
short writes, timeouts or watchdog events. The PDM check uses the driver
byte count and the two DAC checks count decoded PCM frames accepted by
the audio output. [Measurements and image digests](observed.json)

Use the [OpenETH fixture](../../target/cyd_full_app_openeth_qemu/README.md)
with the [classic ESP32 QEMU I2S DMA start fix](../cyd-pdm-static-rx-20261113/README.md).
Enable `CONFIG_YORADIO_TLS_STATIC_RX_RESERVE` with static Mbed TLS buffers
and 16,384/4,096-byte RX/TX limits. Set `CONFIG_ESP_TASK_WDT_TIMEOUT_S=5`
and enable OpenETH RX backoff and the PCM probe in the diagnostic build.
Reuse the local CA and TLS fixture for all three profiles. Run with
`--through-eof --full-tls-records`. The legacy DAC test uses QEMU's
96 kHz DAC model ceiling.

The remaining tests include reconnect and OTA during playback, combined
memory options in the full application, and physical Wi-Fi and DAC/PDM
timing. Static RX reservation remains opt-in.
