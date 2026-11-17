# CYD packet-level Opus on both DAC outputs

Continuous DAC and legacy DAC ran the production CYD application on both
ESP32 cores in QEMU OpenETH with ESP-IDF 6.0.2 and a five-second task
watchdog. The generated configurations differ only in DAC selection.
Both enable packet-level Opus, static TLS RX, early MPI and idle input
reclaim. They use fresh local TLS material and the same WebUI assets.

| Ogg layout | Largest page | Response bytes | Continuous DAC | Legacy DAC |
| --- | ---: | ---: | --- | --- |
| Original stereo fixture | 54,597 B | 706,319 | PASS | PASS |
| Padded packet across pages | 65,306 B | 769,173 | PASS | PASS |
| Continued OpusTags | 65,307 B | 771,564 | PASS | PASS |

All six runs reached ordered EOF with 528,000 decoded PCM frames and
MD5 `2cdf381e8a227d6bc0a8c63dd7fc77fe`, matching the PDM control.
The local peer sent each complete response with full 16,384-byte TLS
records and its final tail. Every requested driver write completed,
with zero errors, short writes, timeouts or guest faults.

The radio retained its static RX while the WebUI used a separate heap RX.
Each run induced one failed 1,536-byte Mbed TLS allocation and recovered
after releasing one idle input slot. The resident count changed from
eight to seven, above the four-slot minimum. Exactly that allocation
failure appeared in health. The same certificate-verified HTTPS
connection served APIs during playback and the exact 13,588-byte script
after EOF. Both RX buffers returned before the controller exited.

The PCM probe counts samples accepted by the real output API. The raw
DAC driver byte counters also include idle writes. The minimum free
heap measurements include the deliberately injected allocation pressure.
Continuous DAC uses QEMU's 48 kHz model, and legacy DAC uses its 96 kHz
ceiling and the existing longer EOF deadline. Physical Wi-Fi and analog
output still require the board.

[Measurements and image digests](observed.json) · [Reproduction](../../target/cyd_full_app_openeth_qemu/README.md#radio-tls-and-https-webui-under-pressure)
