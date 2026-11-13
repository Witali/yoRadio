# Static TLS RX, PDM and WebUI after EOF in QEMU

The [previous run](../cyd-openeth-static-rx-opus-20261113/README.md) with the
smaller initial Opus PCM buffer and TCP window 8640/8 decoded its first
packet. The first 1,024-byte PDM write then accepted zero bytes and timed
out after about one second. The allocation failure count stayed at zero.

ESP-IDF 6.0.2 arms the I2S DMA link before setting TX_START. The QEMU I2S
model armed its virtual timer on the first write. If the timer fired before
the second write, the callback discarded the pending DMA descriptor. The
first PDM write could then wait for a DMA completion until the driver's
timeout expired. [ESP-IDF source](https://github.com/espressif/esp-idf/blob/v6.0.2/components/esp_driver_i2s/i2s_common.c#L118).

The [patch and QTest regression](qemu-i2s-dma-start.patch) keep the descriptor
pending and start the virtual timer once both conditions are met. Explicit
link stop, DMA reset and TX reset clear the pending descriptor. Advancing the
virtual clock between the two MMIO writes reproduced the missing completion
on the original model. The fixed model passed all six checks.

The earlier WebUI timeout occurred in a separate request for the JavaScript
asset after clean EOF. The newer integrated QEMU control includes Windows
SLIRP host-forwarding fixes. That control and both runs with the I2S patch
served the asset within the existing HTTP deadline. The exact cause of the
older HTTP timeout remains open. [Port reservation](https://github.com/Witali/QEMU-ESP32/commit/b068387b7a),
[merge](https://github.com/Witali/QEMU-ESP32/commit/dfb47bdcea).

| QEMU build | Full TLS/Opus and WebUI after EOF | Minimum free heap | PDM completion-queue drops |
| --- | --- | ---: | ---: |
| Integrated control cb9deafd83 | Pass | 7,612 B | 29 |
| I2S fix, run 1 | Pass | 10,164 B | 14 |
| I2S fix, run 2 | Pass | 10,168 B | 13 |

All three runs used the same application, flash image, SDK configuration and
unmodified runner. Each received 706,319 Ogg bytes over TLS 1.2, including
43 full 16,384-byte plaintext records and the 1,807-byte tail. The guest
matched the HTTP body CRC and the CRC of all 551 Opus packets. It reached
normal EOF in the playback generation. Across 1,034 writes the PDM driver
accepted exactly 1,058,176 bytes with zero errors, timeouts or short writes.
WebUI served the exact 13,588-byte gzip asset during playback and after EOF.
There were zero allocation failures and OpenETH allocation waits. The UART
still recorded OpenETH RX frame drops. See [observations](observed.json)
for digests and counters.

## Reproduce

Apply the patch to QEMU at `9135fc89ce3eba7bbb1c2dbed103cd2854436940` with
`git apply --unidiff-zero <patch>`. Its local QEMU commit is
`82c3e11c1ce258adf0076ae92f1eb2404e480371`. Build the classic ESP32 target
and run `python tests/esp32_i2s_dma_test.py --qemu <executable> --bios <pc-bios>`
from that QEMU checkout. For the measured Windows executable, the I2S
model object was recompiled and relinked with the existing integrated
cb9deafd83 build objects. The original I2S model source is identical at
those two base commits.

Use the [OpenETH full application fixture](../../target/cyd_full_app_openeth_qemu/README.md)
and the [packet and body trace hook](../cyd-openeth-static-rx-opus-20261113/README.md).
Select PDM at 48 kHz, OpenETH RX backoff, the Ogg timeline, the 30-second
diagnostic watchdog, the static TLS RX reserve and static Mbed TLS buffers
with 16,384/4,096-byte record limits. Use a TCP receive window of 8,640 bytes,
an eight-entry TCP receive mailbox and the 3,840-byte initial Opus PCM buffer.
Run the full application fixture against the patched QEMU with
`--tls-material`, `--through-eof` and `--full-tls-records`. Use a fresh
output directory each time. Physical Wi-Fi and PDM remain unverified.
