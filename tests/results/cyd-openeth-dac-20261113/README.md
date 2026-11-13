# CYD continuous and legacy DAC under TLS/Opus in QEMU

Both ESP-IDF 6.0.2 builds use the full CYD application, dynamic TLS buffers,
ST7789, the OpenETH RX overlay, the same local CA, and the same SPIFFS bytes as
the [PDM follow-up](../cyd-openeth-tls-isolation-20261113/README.md). The typed
SDK configurations differ from PDM only in the backend selection. The test
probe counts 16-bit stereo frames only after the real output API accepts a
write. DAC priming and idle bytes are excluded. A complete run must flush
528,000 frames at ordered EOF.

With full 16-KiB TLS records, continuous DAC wrote at least 648 decoded frames
and served the exact 13,588-byte WebUI asset. The next HTTP observation timed
out. OpenETH had one unresolved 1522-byte allocation wait, with a largest
DMA block of 992 bytes at the recorded sample.

Legacy DAC configured its usual x16 output, 768 kHz for this source. The
OpenETH diagnostic runs the QEMU DAC model at 96 kHz, its configured ceiling.
The real output API accepted 40,008 frames before a flush following a stream
read error and an Ogg playback error. The guest recorded six RX pressure
episodes, all of which recovered, and 8500 failed allocations. The lowest
logged pressure sample had 232 bytes free. The exact WebUI overlap and full
stream checks failed.

The continuous DAC control with ordinary TLS records reached at least 19,848
frames and served the exact WebUI asset during playback. It then triggered
the IDLE1 watchdog without an OpenETH allocation wait or a recorded failed
allocation. Symbolication against the exact ELF resolved the output task
stack to `dac_continuous_write` at `dac_continuous.c:605`, near the SDK's busy
wait for the previous DMA chain to stop. The mechanism that left the SDK
waiting remains open.

The full-record continuous DAC control using the C3 TCP settings changed
only the receive window from 11,520 to 8640 bytes and the receive mailbox
from 10 to 8 entries. It served the exact WebUI asset with PCM progress from
648 to 15,048 frames. It then hit the same IDLE1 watchdog in
`dac_continuous_write`, with zero allocation failures or RX waits and a
reported minimum heap of 7260 bytes. This comparison leaves the smaller TCP
profile as a diagnostic configuration.

The probe's host tests reject truncated, failed or duplicate flushes and
ignore priming bytes as proof of progress. Four PCM observer tests and seven
TLS record tests passed. The [runner setup](../../target/cyd_full_app_openeth_qemu/README.md)
documents the diagnostic build flags. The model qualifies driver acceptance of
PCM and ordered output in the guest. Physical DAC timing remains open.

[observed.json](observed.json) records all four terminal runs and their image,
receipt and UART log digests.
