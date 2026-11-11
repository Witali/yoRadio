# Dynamic Mbed TLS buffers with the full CYD radio application

The C3 radio profile uses Mbed TLS's on-demand buffers. We compared that SDK
option with the static-buffer CYD control. Both images were built with
ESP-IDF 6.0.2 from `d471868f1`, with the same OpenETH RX overlay, 30-second
diagnostic task watchdog, local CA, station, WebUI assets, ST7789 and PDM.
The TLS record limits remained 16384 bytes RX and 4096 bytes TX. Enabling
dynamic buffers exposes the default-off configuration cleanup flag and hides
the default-off static RX reserve. All other effective settings match.
[Espressif Mbed TLS configuration](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/kconfig-reference.html#config-mbedtls-dynamic-buffer).

| Run | Result | Minimum heap | Largest DMA block after WebUI | Allocation failures | RX waits | PDM driver bytes after WebUI |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Static 1 | NONPASS | 348 B | 5376 B | 8 | 2 | 81,280 |
| Dynamic 1 | PASS | 18,416 B | 18,432 B | 0 | 0 | 73,088 |
| Static 2 | NONPASS | 304 B | 10,240 B | 56 | 2 | 81,280 |
| Dynamic 2 | PASS | 18,540 B | 21,504 B | 0 | 0 | 77,184 |

All four guests received the verified TLS stream and served the exact
13,588-byte WebUI JavaScript asset during PDM output. The static controls
recovered their OpenETH descriptors and recorded failed 1522-byte allocations.
The dynamic application image was 2976 bytes larger. The ELF section sizes
for IRAM text, DRAM data and DRAM BSS matched.

The first full-file dynamic run reached its 50-second host deadline after
892,288 bytes of PDM driver writes. The peer finished writing all 706,319
encoded bytes and the guest still had zero allocation failures. The PDM driver
averaged 58 ms per write in QEMU. The static full-file control closed the
WebUI connection after five RX pressure episodes.

The expected output is 528,000 samples from the fixture's Opus pre-skip 312
and final granule 528,312. The PDM byte counter includes 1408 bias ramp bytes
after DMA preload and pads the last block to 512 samples. The total is
1,058,176 bytes at the driver boundary.

The retry with a 90-second host deadline passed. The health sample at guest
uptime 81.635 seconds followed `stream ended` for generation 1. The driver
accepted exactly 1,058,176 bytes in 1034 writes, with zero errors, timeouts, short writes or
completion queue drops. The guest served the exact WebUI asset during playback
and after EOF. Its heap minimum was 16,164 bytes, and after EOF it reported
142,648 bytes free with a largest DMA block of 110,592 bytes. The reported stack
margins were 1604 bytes for stream, 2700 for decode, 2868 for output and 1228
for HTTP. OpenETH logged zero RX waits and the health API reported zero
allocation, decoder, stream or output failures.

[observed.json](observed.json) records the exact image, runner and receipt
digests. The [reproduction](../../target/cyd_full_app_openeth_qemu/README.md)
uses the installed SDK and local TLS peer. This qualifies the diagnostic PDM
run with verified TLS over OpenETH. Production Wi-Fi, larger TLS records under
load, the two DAC variants and physical audio still need their own checks.
