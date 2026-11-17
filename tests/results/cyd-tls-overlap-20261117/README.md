# CYD radio TLS and HTTPS WebUI under heap pressure

One dual-core PDM image with ESP-IDF 6.0.2 ran the production radio and
WebUI over QEMU OpenETH. The radio borrowed the static TLS RX buffer.
One certificate-verified TLS 1.2 connection to the HTTPS WebUI used a
heap RX buffer. Both buffers stayed live through a failed 1,536-byte
Mbed TLS allocation and a successful retry after the production input
pool released one idle slot.

The passing Opus fixture carries eight original packets per page, with
pages up to 10,275 bytes. The radio consumed all 707,831 encoded bytes
through EOF. The 528,000 decoded PCM frames matched the single-TLS
control MD5. PDM accepted 1,058,176 bytes including fill and padding.
The same WebUI connection served an API response during playback and
the exact JavaScript asset after EOF. The test observed the static
reserve and the heap RX returned.

The original fixture on the same image has pages up to 54,597 bytes.
With HTTPS live, decoding failed before any audio output. Health
recorded one failed 26,504-byte allocation and associated its sequence
with the Ogg decoder's result `-7`. The radio returned its static RX loan.
The [follow-up with early Opus initialization](../cyd-ogg-large-pages-20261117/README.md)
identified that allocation and played the original page layout through EOF.

FFmpeg with libopus produced the same PCM MD5 for both Ogg layouts.
The re-page profile changes transport framing only. Both runs
preserved their QEMU flash snapshots and recorded no guest fault.

[Measurements](observed.json) · [Reproduction](../../target/cyd_full_app_openeth_qemu/README.md#radio-tls-and-https-webui-under-pressure)
