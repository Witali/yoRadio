# Full-size TLS records with the CYD radio application

The three CYD profiles used the same ST7789, PDM, OpenETH RX overlay, fixture,
local CA and 30-second diagnostic task watchdog. The static control and
dynamic image came from `d471868f1`. The reserved RX image came from `abadf24e6`,
which changed test and documentation files. The firmware source trees match.
The reserve changes one effective configuration value against the static
control. Its ELF contains a 16,717-byte RX symbol and adds 16,768 bytes of DRAM
BSS. All three retain TLS RX/TX limits of 16384/4096 bytes.

The local HTTPS server wrote the Opus fixture in 16,384-byte chunks with a
1807-byte tail. The OpenSSL message callback captured the outgoing TLS record
header lengths. For the negotiated TLS 1.2 AES-256-GCM suite, a full application
record has 16,408 bytes after the five-byte TLS header. The receiver gate
requires ordered EOF, the exact 1,058,176 PDM driver bytes, and WebUI assets
during playback and after EOF. [TLS 1.2 fragmentation](https://www.rfc-editor.org/rfc/rfc5246.html#section-6.2.1), [AES-GCM overhead](https://www.rfc-editor.org/rfc/rfc5288.html#section-3).

| Profile | Complete TLS body at peer | Exact WebUI during playback | Observed failure |
| --- | --- | --- | --- |
| Dynamic, two runs | No | No | Both timed out during the PDM bias ramp. Heap allocation failures and OpenETH RX waits stayed at zero. |
| Static RX reserve | Yes, 706,319 bytes | Yes | Playback ended as `decode failed` after 730,496 driver bytes. OpenETH recovered from nine RX pressure episodes. |
| Static control | No | No | WebUI closed after a 1024-byte partial response during playback. |

The reserved run recorded 43 full outgoing TLS records and the final short
record, with a complete sender body. The guest reported a 560-byte minimum
heap and 18,880 failed allocations. The decoder reported failure with an
1807-byte input block. The cause of the decoder failure remains open.

Both dynamic runs completed 17 full socket writes and captured 18 outgoing
full record headers. The capture includes a header as soon as OpenSSL creates
it. The successful socket writes totalled 278,528 bytes in each run. The
minimum heap was 13,156 and 13,208 bytes, respectively. The static control
captured 14 full record headers and reached a minimum heap of 348 bytes.

An initial MemoryBIO server passed a verified host HTTP roundtrip and timed
out before the handshake in QEMU, with zero body bytes. The measured QEMU runs
use the established HTTPS socket server. The host tests verify exact file
bytes, the full record headers and the short tail, and reject the 1024-byte
record control. Seven record tests and four existing pacing tests passed.

[observed.json](observed.json) records the four terminal QEMU runs and their
image, configuration, receipt and log digests. The full application gate is
**NONPASS** in this diagnostic PDM profile. Separating TLS receive behavior
from PDM startup and tracing the reserve profile's decode failure are the next
software checks.

The follow-up reproduced a startup state bug in the host driver seam. A PDM
bias write timeout left the channel enabled and the next configure call
could treat it as ready. The CYD driver now releases that channel on startup
failure, retains its handle if release fails, and retries cleanup before
another startup. The output ownership suite passed under ASan/UBSan with 17
PDM, 17 continuous DAC and 10 legacy DAC cases. A control that restored the
old readiness check failed at the expected retry assertion.
