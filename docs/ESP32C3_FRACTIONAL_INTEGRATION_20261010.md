# Integrated nominal 48 kHz candidate, 2026-10-10

The combined configuration improves the observed audio timing, but **is not
production-qualified**. Ten-minute HE-AACv2 playback passes with no measured
DMA counter increments, while its post-Stop contiguous-memory check fails.
The requested ten-minute FLAC test is interrupted by a WebUI TCP connection
timeout. Both failures remain recorded; repository defaults are unchanged.

## Configuration and saved images

Both candidates use pinned ESP-IDF `9a97f6c54ec6`, QIO 80 MHz, full compact
AAC/SBR/PS at native rates, the 17,058-byte TLS RX reserve, adaptive input,
250/500 ms input prefill, and four optional extra FLAC input slots. Hardware
fractional PDM clocking targets nominal 48,000 frames/s. Software integer-rate
compensation, FIR and direct-DMA PCM are disabled. Output priority is 8;
decoder priority is 7. Both remain awake.

| Image | App bytes | Hardware testing |
| --- | ---: | --- |
| `idf61-frac4`, profiling and laboratory CA | 1,623,232 | Results below; not accepted |
| `idf61-quiet-frac4`, normal roots and no console/logging | 1,454,704 | Built and audited; not installed |

Artifacts: [diagnostic](../firmware/development/esp32c3-idf-6.1-r9a97-frac4/manifest.json)
and [quiet](../firmware/development/esp32c3-idf-6.1-r9a97-quiet-frac4/manifest.json).
Their app SHA-256 values are respectively
`6ef20f1ae25429027165b6cd7549cc053bc1fdf5741176287a34105d2fa6ad02` and
`eb28c93028323388a8c01a96050d0fde10d9d39b160b2021605a906c86b86a5f`.

Against each saved integer-clock control, the only active configuration
change is `CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK=y`. All 18 AAC/FLAC objects'
nonempty code/constant sections remain byte-identical: 128 sections in the
diagnostic comparison and 119 in the quiet comparison. Full AAC, HTTP and
TLS/input allocation link checks pass. The quiet trust bundle matches the
normal production roots; no private board settings are embedded.

Quiet IRAM text, initialized DRAM and BSS remain 46,184 / 11,524 / 44,848 B.
Inactive unrelated CLZ work is explicitly excluded. The frozen source
snapshot was prepared at `81155050`; the documentation-only FIR report
commit occurred between the two build captures. Source hashes stayed equal.

The physical diagnostic installation verifies the app ELF identity, actual
QIO/80 MHz setup, four mapped-image CRC passes, and PDM register divider
`625/312`, giving nominal 48,000 Hz. This is register/configuration evidence,
not an external frequency measurement.

## HE-AACv2: ten-minute playback passes, memory recovery fails

One TLS connection plays full 44.1 kHz stereo HE-AACv2 at 1.0x fixture pacing.
Plaintext record sizes grow from 1 KiB to the full 16 KiB; the captured wire
records include 118 of 1,048 B and 140 of 16,408 B. The observation lasts
600.03 seconds and retains 3,286 status samples. Original results are **4/5**:
playback, initial idle, runtime and settings restoration pass; idle recovery
fails its unchanged largest-block threshold.

| Post-warmup measurement | HE-AACv2 |
| --- | ---: |
| Mean CPU / output task | 61.23% / 7.20% |
| Decoded audio / elapsed time | 0.99997 |
| Minimum free heap / largest block | 26,004 / 15,360 B |
| First / last steady-state median free heap | 26,408 / 26,456 B |
| Decoder waiting for compressed input | 0% |
| Decoder waiting for PCM space | 52.26% |
| Output waiting for PCM | 1.21%; longest call 5.97 ms |
| DMA notification increments / write errors | 0 / 0 |

CPU, decoder, queue-flow and DMA telemetry pass completeness checks. The
whole observed DMA counter bracket spans 596.02 seconds, with zero increments
and 55,882 successful writes. Counter observations do not measure analog
continuity or cover unobserved edges. Wait times include preemption and must
not be added across tasks or interpreted as CPU utilization. A full PCM
queue causing decoder waits is expected backpressure, not an overflow.

After Stop, median total free heap is 133,138 B versus 133,486 B initially:
only 348 B less. However, the largest allocatable block falls from
**114,688 to 102,400 B**, a **12,288 B** loss, with the same 17 tasks. This is
consistent with fragmentation without a comparable total-free loss; no
allocation owner is identified. The SDK rounds largest-block capacity to
allocator size classes, so the change is not a 12 KiB payload-leak measurement.
Do not waive the failed recovery gate or assume TLS initialization caused it.

## FLAC: incomplete because new TCP connections time out

The heavy 48 kHz stereo 16-bit FLAC run requests 600 seconds. Observation
stops after **77.34 seconds**; the entire playback case, including cleanup,
lasts 83.38 seconds. Original results are **5/6**: playback fails with
`URLError` caused by `TimeoutError`; idle, recovery, Stop and complete-capture
runtime checks pass. No allocation, decoder, TLS, watchdog or reset fault is
recorded, but this is not a successful ten-minute test.

Host trace requests 419 and 420 fail specifically during TCP **connect**,
after 5,004 and 5,006 ms, with local ports 54994 and 54996. The second attempt
occurs while cleaning up the first failure. No HTTP response was reached.
The evidence distinguishes connection establishment from slow WebUI handler
execution; it does not identify where the handshake was lost.

The partial post-warmup data show CPU 80.84%, output task 5.76%, minimum free
heap 49,188 B and largest block 38,912 B. Decoder waits are 78.34% for PCM
space and 0.043% for input; the observed decode/audio pace is approximately
real time. CPU has no acceptance ceiling. Complete qualification of the
interrupted telemetry interval fails and these values are descriptive only.
The saved whole DMA counter bracket covers 70.05 seconds with zero increments
and write errors; it does not prove continuity through the failed connections.

Settled largest-block capacity recovers to its own 102,400 B baseline after
FLAC. That baseline already includes the preceding AAC loss, so this result
does not establish recovery to fresh boot. Median RSSI is -74 dBm during AAC
and -71 dBm during FLAC, with minima -85 / -83 dBm. No causal attribution to
signal strength is made.

## Restoration and next action

Application-only OTA restores the user's listened fractional-clock image
`idf61-listen48-8c1f2d`, ELF SHA
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`.
Wi-Fi, playlist and settings compare unchanged in memory. Three observations
confirm the original stopped state. No NVS, filesystem or bootloader write
is performed.

Next, trace the retained allocation owners after first AAC/TLS use and the
TCP SYN/SYN-ACK path during heavy FLAC. The existing `web-tcp-v2` diagnostic
image has exactly three additional active settings: heap hooks, heap-owner
probe and TCP probe. Its extra instrumentation changes timing and heap layout;
use it for attribution, then verify any repair on uninstrumented candidates.
Final quiet-image format, network and OTA qualification remains open.

[Frozen evidence and offline replay](../tests/results/esp32c3-frac4-20261010/README.md)
retain both builds, original verdicts, incomplete observations, transport
failures, queue timing, sources and restoration checks.
