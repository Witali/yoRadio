# CYD Vorbis over TLS: full-application resource controls

The unchanged public Espressif Vorbis decoder ran in the production CYD
application with OpenETH, initialized ST7789, PDM and the real WebUI.
Both diagnostic images retain the five-second task watchdog and 300 ms
interrupt watchdog. Their initial TCP window/mailbox are 11,520 bytes/10.

| Profile | Result | Last observed PCM progress |
| --- | --- | ---: |
| Normal static TLS buffers | NONPASS: WebUI health timed out after repeated OpenETH receive-allocation failures. | 40,640 frames |
| Dynamic TLS buffers | NONPASS: a 16,749-byte TLS allocation failed; playback ended after flushing 41,920 frames. | 40,640 frames before the flush |

The normal profile's nine OpenETH wait episodes include a largest-block
observation of 464 bytes against a 1,522-byte request. The dynamic profile
recovered its three OpenETH waits, then failed to allocate the next full
TLS RX buffer. The changed SDK configuration has one active policy delta,
`MBEDTLS_DYNAMIC_BUFFER`. Two dependent disabled options change presence;
their exact typed differences are recorded in [observed.json](observed.json).
Neither run completed the 703,584-byte response or reached successful EOF.
These results do not qualify full Vorbis playback or change production defaults.

The controller now accepts `--codec vorbis` and checks all 528,000 stereo
PCM16 frames and their complete SHA-256, including the final tail. Its
[direct public vendor reference](../cyd-espressif-reuse-20261030/NATIVE.md)
was revalidated offline, and both currently linked Espressif archives match
that checkpoint byte for byte. This is an integration identity, not an
independent numeric conformance oracle. The two failing runs do not meet it.
Twelve observer tests cover exact EOF and checksum acceptance/rejection.

[Reproduction and SHA probe](../../target/cyd_full_app_openeth_qemu/README.md#other-playback-fixtures)
uses the standard profile preparation with the task watchdog restored to
five seconds. Enable dynamic TLS buffers only for the second control;
retain the TCP and full 16,384/4,096-byte TLS record settings.
Local certificates, keys, flash images and full logs stay under ignored
`.build`. These are diagnostic QEMU images, not production hand-off firmware.

The next resource investigation is the simultaneous application-owned
CRC-verified page and vendor Ogg input buffering. The existing word-capable
page store on classic ESP32 is a candidate; no change to Vorbis synthesis,
CRC verification or input contents is justified by these two failures.
Physical Wi-Fi and audio still require the board.
