# ESP32 C3 heap use during continuous HE AAC playback

The ten-minute DIO and QIO runs from 8 October show receive-queue growth
alongside falling free heap. They do not yet identify every live allocation.
Both original **FAIL** results remain unchanged. This analysis on 9 October
adds a controlled delivery-rate option for the next physical comparison.

Follow-up: the [9 October physical pacing comparison](ESP32C3_HEAP_PACING_20261009.md)
is now complete. At 1.00x, heap remained stable but DMA queue overruns occurred;
at 1.02x, receive queues filled and the original heap-trend gate failed again.
Both recovered settled idle memory after Stop. The follow-up preserves every
original verdict and records a separate PDM clock hypothesis.

## Observed memory and receive credit

`NET_HEAP` and `NET_RX` come from the same TCPIP callback. Pairing uses their
sequence number and equal snapshot age, with host receive time minus age for
window selection. It excludes ten seconds of warmup and preserves malformed,
missing, duplicate, stale and delayed records as unavailable evidence.

| Measurement | DIO | QIO |
| --- | ---: | ---: |
| Valid paired snapshots | 117 | 116 |
| Heap versus outstanding receive credit, Pearson r | -0.9923 | -0.9881 |
| Active connections throughout selected samples | 2 | 2 |
| TIME_WAIT connections | 0 | 0 |
| Maximum outstanding receive credit | 8,640 B | 8,640 B |
| Minimum snapshot free heap | 14,856 B | 14,524 B |
| Minimum largest free block | 4,608 B | 4,608 B |

The correlation is descriptive; successive samples are not independent trials.
Receive credit counts logical TCP payload, not allocator capacity. Refused data
overlaps the credit count and must not be added to it. Host socket buffers, TLS,
Wi-Fi and application input buffers have separate lifetimes.

| Seconds after playback start | DIO median heap / outstanding credit | QIO median heap / outstanding credit |
| --- | ---: | ---: |
| 10–70 | 26,404 / 0 B | 26,160 / 0 B |
| 130–190 | 22,928 / 3,159 B | 21,536 / 4,212 B |
| 250–310 | 17,104 / 7,448 B | 17,104 / 7,587 B |
| 430–490 | 17,514 / 7,587 B | 17,512 / 6,534.5 B |
| 550–600 | 16,940 / 7,974.5 B | 17,496 / 7,309 B |

Half-byte values are medians of two integer observations. This pattern is
consistent with initial queue filling followed by bounded fluctuations. It
does not prove the absence of a smaller leak. Settled idle recovery already
passed in the [original comparison](ESP32C3_QIO80_RECHECK_20261008.md).

## Why the server can fill the receive queue

The verified `hev2-44100-stereo` fixture contains 47,379 bytes for
11.842176870748299 seconds: **4,000.869140625 encoded bytes per audio second**.
The archived server events specify `pacing_ratio=1.02`, so the intended rate is
4,080.8865234375 bytes/s. Relative to exactly real-time consumption, the excess
is **80.0173828125 bytes/s**, approximately **48,010 bytes over 600 seconds**.

This is a nominal rate calculation, not a measurement of bytes retained on the
board. Each server recorded 2,448,073 completed socket-write bytes over about
599.89 seconds. Successful socket writes do not mean the board received those
bytes. Socket buffering and backpressure can keep some surplus on the host.
The board's measured audio rate also differs slightly from nominal time.

The shared fixture server and C3 runner now accept `--pacing-ratio 1.0` for a
control with no deliberate surplus. The default remains **1.02**; historical
stress conditions and acceptance thresholds are preserved. HTTP and built-in
HTTPS servers record the selected ratio. External HTTPS origins require their
own configuration; the specialized TLS-record server is unaffected.

## Minimum free memory means different things

The current `check_cpu` diagnostic thresholds are **8,192 bytes of free heap**
and **4,096 bytes in the largest free block**. Falling below either fails the
test. The independent first/last trend limits are 2,048 bytes for total free
heap and 4,096 bytes for the largest block. These policy thresholds are not a
proof that every format transition or reconnect can succeed with that reserve.

The observed QIO low point of 14,524 / 4,608 bytes belongs to the laboratory
build, with a reserved TLS RX slot and reduced input queue. No allocation
failure was captured in that run. It is not a measured safe floor for the
[installed production image](ESP32C3_PRODUCTION_QIO80_20261008.md), whose memory
configuration differs.

In that production configuration, dynamic TLS buffers are disabled. TLS
allocates its full receive buffer during connection setup and keeps it until
connection cleanup; the 16 KiB content capacity need not be allocated again for
every incoming record. A new TLS connection still needs buffers and handshake
memory. The experimental dynamic-RX reserve's **17,058-byte** request must not
be treated as the production image's universal free-heap threshold.

The AAC adapter grows its input frame allocation up to **8,191 bytes** and
retains that capacity until destruction. A larger later frame can therefore
need a new contiguous allocation while the previous buffer is still live,
unless realloc can extend it in place. A 4 KiB free block does not guarantee
that operation. Initial SBR/PS setup, format changes and WebUI uploads have
additional requirements. Check these phases separately from steady playback.

## Validation and next physical comparison

The new server tests exercise real loopback HTTP routes with an isolated
deterministic pacing clock: default rate, slower/faster rates, segments with
different durations, unpaced files, continuous AAC, exact bytes and invalid
ratios. They do not claim physical network timing. Four new pairing tests
include corrupted/missing telemetry and replay of both saved hardware runs.
Together with existing network, load-window and recovery tests, **26 tests pass**.
The first loopback invocation was prevented by sandbox socket restrictions;
the authorized loopback rerun passed. No new firmware was flashed for this work.

Next, compare the same diagnostic image, fixture, TLS policy and WebUI load
for 600 seconds at 1.00x and 1.02x. Keep the original acceptance result and
compare settled windows and Stop recovery separately. If the lower-rate run
still shows loss, trace actual allocation owners; even a disappearance of the
trend at 1.00x does not qualify operation with an overfeeding real station.
The firmware must tolerate ordinary backpressure without allocation failures.

Reproduce the analysis without contacting a board:

```powershell
python tests/test-heap-receive-correlation.py
python tests/test-audio-server-pacing.py
python tools/esp32c3_tests/heap_receive_correlation.py --input tests/results/esp32c3-qio80-recheck-20261008/physical/qio/hev2-ten-minutes --output .build/qio-heap-receive.json
```

[Saved derived results](../tests/results/esp32c3-heap-receive-20261009/) retain
source/input hashes, original verdicts, every paired sample and validation logs.
