# CYD OpenETH receive allocation under TLS/Opus load

The [full-application diagnostic](../../target/cyd_full_app_openeth_qemu/README.md)
was rebuilt with its optional OpenETH RX overlay. The SDK configuration has
the same 1,259 typed values as the previous TLS load build. Both runs use the
same SPIFFS bytes, local TLS peer and pinned QEMU executable. The overlay
checks the next descriptor before allocating the original 1522-byte buffer.
On allocation failure, it keeps the descriptor and retries after one tick.
Three source drift controls were rejected. The original LF and CRLF inputs
generated identical overlay bytes.

The previous runner expected the status label `opus`. CYD reports `OGG` for
the Ogg container. The corrected runner checks the `OGG` label, active audio
and the known stereo fixture's 48 kHz PCM before sampling output progress.
The earlier UART allocation errors remain observable in the original reports.
[Original diagnostic results](../cyd-full-app-openeth-20261111/README.md).

The guest validated the local TLS certificate, configured PDM at 48 kHz and
reported one complete 1024-byte driver write. At that sample, the heap had
16,936 bytes free, a 10,704-byte minimum and a largest internal/DMA block of
13,312 bytes. Allocation, decoder, stream and output failure counters were
zero at that point.

This first driver write can be part of the 1408-byte PDM bias ramp counted
after DMA preload. The [TLS buffer comparison](../cyd-openeth-tls-dynamic-20261111/README.md)
observes writes well past that ramp in both profiles.

Later the OpenETH task logged four allocation pressure episodes and recovered
from three before the test ended. The lowest recorded free heap during these
episodes was 1796 bytes. The largest DMA block fell to 864 bytes. The HTTP
server logged a send error and closed the concurrent WebUI request without
returning the asset. The TLS peer had written 310,272 bytes to its socket when
the run ended. The strict playback/WebUI check therefore remains **NONPASS**.

[observed.json](observed.json) records the selected measurements and artifact
digests. The OpenETH profile uses the 30-second diagnostic watchdog. Production
Wi-Fi, the five-second watchdog and physical audio remain outside this run.
