# Early Opus decoder creation with the original large Ogg pages

The control uses the original 706,319-byte stereo Opus fixture, with pages
up to 54,597 bytes. The radio borrows the static TLS RX and the HTTPS WebUI
holds its heap RX buffer. PDM runs in dual-core ESP32 QEMU OpenETH with the
five-second watchdog and ESP-IDF 6.0.2.

The control reproduced the 26,504-byte failed allocation and produced zero
PCM. The guest logged an allocation failure during the vendor Opus decoder
open. In the linked vendor library, the stereo state size is 26,504 bytes
including the SILK state, CELT state and decoder header. The failure occurs
with the first full audio page already resident.

With `CONFIG_YORADIO_OGG_OPUS_RAW=y`, the same public Opus decoder opens
after the CRC-verified OpusTags and before the first audio page allocation.
The shared packet reader preserves the original page CRC, lacing and
packet bytes. The adapter checks output geometry and applies pre-skip,
final trimming and header gain with ordered link cleanup.

Both QEMU replays matched 528,000 PCM frames to the established Espressif
MD5, received all 43 full TLS body records and the 1,807-byte tail, and
recorded 1,058,176 bytes accepted by PDM including fill and padding. With
both RX buffers live, each test induced one failed 1,536-byte Mbed TLS
allocation and observed a successful retry after one idle input slot
was released. The WebUI served the exact 13,588-byte script after EOF
over the same verified TLS connection. Both RX buffers returned.

Under ASan and UBSan, the shared adapter passed 38 playback schedules
and 27 contract controls. Four new mono and stereo Family 0 cases compare
PCM with libopus and require one decoder open at OpusTags, before decoding
audio. They include 120 ms packets, split packets and multi-page comments.
The existing simple wrapper passed 116 host cases.

[Measurements](observed.json) · [Reproduction](../../target/cyd_full_app_openeth_qemu/README.md#radio-tls-and-https-webui-under-pressure) · [Ogg Opus timing](https://www.rfc-editor.org/rfc/rfc7845.html#section-4)
