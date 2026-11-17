# CYD Vorbis over TLS: repaired page storage

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
These original results do not qualify full Vorbis playback.

## Repaired storage on all three outputs

The application now reuses the classic ESP32 word-capable Ogg page store
with the public simple decoder. It retains the full CRC check and supplies
the unchanged encoding through a 2,048-byte buffer. Vorbis synthesis and
the Espressif archives are unchanged.

| Output | Complete PCM frames | Complete vendor PCM SHA-256 | Minimum free heap |
| --- | ---: | --- | ---: |
| PDM | 528,000 | `e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910` | 38,640 B |
| Continuous DAC | 528,000 | Same exact hash | 40,132 B |
| Legacy DAC | 528,000 | Same exact hash | 36,728 B |

All three runs completed the 703,584-byte response, 42 full 16,384-byte
TLS body records and its 15,456-byte tail. Audio advanced during a WebUI
asset read, and the exact 13,588-byte asset was served again after ordered
EOF. There were zero allocation failures, OpenETH allocation waits, driver
write errors, timeouts or short writes. The distinct backend byte totals
and telemetry counters remain in the JSON.

The repaired PDM SDK configuration is byte-for-byte identical to the
original static-buffer control. The DAC configurations change only the
audio-output choice. TCP, TLS record sizes, static buffer policy, clocks,
watchdogs, task cores, priorities and stack sizes are retained. The observed
decode-task stack minimum is 10,844 unused bytes in each run. QEMU uses its
48 kHz continuous-DAC model and 96 kHz legacy model ceiling. These are
emulator resource checks, not physical timing or listening measurements.

Host ASan/UBSan checks pass 156 lifecycle cases, including 40 new fragment
cases, plus 276 page, 204 trim and 144 gain cases. The new cases preserve
every encoded byte through incomplete consumption, zero/partial/full
consumption on resize, cancellation, allocation refusal and CRC rejection.
They cover the maximum 65,307-byte page and a continued packet.

The 528,000-frame bound follows the fixture's EOS granule. The
[Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
defines that position in samples per channel. The fixture has 15 pages;
its largest encoded page is 58,231 bytes.

## Stack-frame regression and complete task lifecycle

An initial version passed the three full PCM runs but placed the staging
array in the common decoder frame. ELF disassembly measured 3,728 bytes,
against the original 1,744. The final separate non-inlined helper uses
2,144 bytes, while `decoder_task` uses 1,760. Raw Opus never calls that
staging helper. [The ELF check](../../check-cyd-ogg-stack.py) passes all
three final images and rejects the earlier oversized frame. This checks
static compiler frames, not total runtime stack depth.

The updated SDK/QEMU task fixture also passes nine Opus20/Opus120/Vorbis
lifecycle cases and one three-codec chain in a single HTTP session and
generation. It checks exact complete PCM, EOF, Stop/reopen, maintenance,
six real resize/retry pairs, source/PCM metadata and the original task
bindings. All 18 public decoder handles and 16 HTTP clients close.
The output seam validates stereo legacy layout, zero header gain and both
metadata calls before every PCM packet. Its diagnostic watchdog settings
remain 20 seconds/1,000 ms. This fixture's extra probes leave
a measured 772-byte decode stack minimum; it has synthetic transport and
output boundaries. The three full-application measurements above include
real TLS, TFT and backend writes.

The first SDK attempt exposed two missing APIs in the old output seam.
A later attempt stopped on an assembler `No space left on device` error.
Both remain nonpassing. The successful fresh campaign retains exact
compiler dependencies and verifies every source, runtime and image binding.

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

The original profile exhausted RAM while the application-owned CRC-verified
page and vendor decoder were live. Moving the application payload
to word-capable storage makes the three unchanged static-buffer profiles
complete this workload. Allocation refusal still has the original byte
fallback. See [storage and lifetime rules](../../../docs/CYD_MEMORY_TRANSFER_DESIGN.md#verified-ogg-pages-in-word-capable-ram).
Physical Wi-Fi and audio still require the board.

## Family 1 regression and the old ownership expectation

The complete creator-backed dispatch regression initially failed its
open-refusal control. The same assertion fails on source `51b4f03b8`, before
the word-page change. Its original expectation kept the Tags page ready;
the earlier early-open implementation already acknowledges it before opening
the public decoders. The isolated old-source control observed two opens,
one created/destroyed handle, zero live handles/output and zero page size,
ready or pending state.

The test now requires that acknowledged state, the blocked Tags phase and
no remaining decoder handles. Byte and word variants pass the unchanged
43 positive schedules, 12 controls and 12,983,296 exact creator PCM samples.
The 23 extra word-storage controls and two-channel policy variant also pass.
The original failure is retained; no numeric oracle or tolerance changed.
