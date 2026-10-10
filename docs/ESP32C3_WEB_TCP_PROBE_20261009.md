# ESP32-C3 WebUI TCP diagnostic: timeout not reproduced

The [input-retention follow-up](ESP32C3_INPUT_RETENTION_20261009.md) recorded
two failed WebUI connections during HE-AACv2 TLS playback. This repeat adds
default-off TCP handshake instrumentation to locate a future failure.
**The previous timeout remains unresolved.** The repeat passes its 16
application checks, but the USB TCP trace is incomplete and must not be
treated as a fully qualified transport capture.

## Instrumentation and controls

`CONFIG_YORADIO_WEB_TCP_PROBE` wraps the actual lwIP input and IPv4 output
paths. It copies metadata before lwIP can modify/free a packet and forwards
the original arguments and return value. The existing WebSocket status task
drains a 64-event RTC ring and schedules network snapshots every second.
Consequently, snapshots continue without successful HTTP status requests.
No additional task, packet allocation, retry or longer timeout is introduced.

An optional host trace records each socket's local port before Python closes
a failed connection. This lets future failures be matched by port and time.
Addresses, payloads, request headers, credentials and exception messages are
not retained. Host tests cover destructive packet ownership, pass-through
behavior, handshake states, filtering, ring overflow/index wrap and both
backlog configurations under ASan/UBSan. Five host transport tests pass.

The linked ELF proves the real input/output routes reach the wrappers and
that only the WebSocket task calls the independent sampler. Compared with
the retained-queue owner image, only this Kconfig option changes:

| Linked section / artifact | Delta |
| --- | ---: |
| RTC data | +1,024 B |
| Ordinary DRAM BSS | +16 B |
| IRAM | 0 B |
| Flash code | +1,186 B |
| Flash constants | +248 B |
| Application binary | +2,464 B |
| AAC/FLAC code and constant sections | 128 identical sections in 18 objects |

Other controls remain ESP-IDF 6.1 revision
`9a97f6c54ec638111ce55cd36581b3c192f15207`, QIO 80 MHz, full compact AAC/SBR/PS,
17,058-byte TLS RX reserve, four optional extra FLAC input slots, input
prefill 500/250 ms, and experimental fractional 48 kHz PDM. This diagnostic
configuration is not a production-default recommendation. The inactive CLZ
worktree change was not compiled. No PCM arithmetic changed.

## Physical repeat

The same bounded scenario performs three FLAC 48 kHz -> HE-AAC 48 kHz ->
HE-AACv2 44.1 kHz cycles, four HTTPS EOF cases (FLAC/HEv2, AUTO/explicit),
75 seconds of HEv2 with TLS plaintext records growing from 1 KiB to 16 KiB,
and a stopped minute without HTTP polling.

| Observation | Result |
| --- | --- |
| Application report, including post-close runtime | 16/16 PASS |
| Host-traced TCP connects | 918 successful, zero failures |
| Maximum observed connect duration | 266 ms |
| HEv2 TLS status samples | 388; full 44.1 kHz stereo |
| CPU samples during record test | Mean 59.35%, peak 63.9%; no CPU acceptance limit |
| Minimum free heap / largest block in record test | 20,968 / 14,848 B |
| Settled watched region, initial -> final raw free span | 106,604 -> 106,604 B; zero remaining owners |
| Complete-capture runtime fault gate | PASS |
| Complete TCP/listener telemetry gate | FAIL |

The independent DMA replay contains 13 complete samples over **60.094 s**
inside the sustained TLS window: 5,634 writes / 11,538,432 bytes, zero
increments in descriptor-reuse overruns or write errors. This is a counter
observation, not an analog continuity or sound-quality measurement.

The actual SDK enables `TCP_LISTEN_BACKLOG=1`, overriding upstream lwIP's
default. Valid snapshots report backlog 5 and no sampled pending accepts
or SYN_RCVD connections. Handshake event records do show transient pending
accepts between snapshots. Sampling an empty queue does not prove it was
always empty, particularly with damaged telemetry.

## Why the TCP capture is rejected

Initial USB capture hand-off loses part of the startup output. Additional
lines also lose individual characters or merge during playback: examples
include `dropped0`, `por=60964` and two complete/partial events on one line.
The strict replay records **13 issues** (malformed lines and sequence gaps),
including issues inside the TLS window. It never repairs or guesses missing
characters. No nonzero ring-drop counter is observed in intact records, but
this does not make the USB trace complete.

The pinned SDK's default USB Serial/JTAG VFS transmitter waits up to 50 ms
for a writable FIFO, then drops bytes until it becomes writable. This is
a plausible loss mechanism, not proof of the exact host/USB cause in this
run. The diagnostic format currently also lacks an end-to-end checksum;
sequence checks cannot detect every possible digit loss.

Before using the probe to exclude a TCP failure path, reduce the verbose
log volume and add explicit frame integrity checking, then repeat with a
continuous capture. Keep the present failed telemetry gate and the original
WebUI failures. A pass here does not establish that the timeout is fixed.

## Saved image, restoration and replay

The diagnostic application is saved at
`firmware/development/esp32c3-idf-6.1-r9a97-web-tcp-probe/app.bin`:

- Application SHA-256: `2a4a2505141e2e85421112bb3cc4d10db1e64b65800e11bd2b47e38c0b1e8762`.
- Embedded ELF SHA-256: `197034196e6b1a5523fcabc1135a5326411238280747473301fa5847c31b658c`.

After the trial, app-only OTA restored `idf61-qio80-8c1f2d2d` in app1.
Wi-Fi, playlist and settings compare unchanged. Three subsequent status
observations confirm AAC 44.1 kHz stereo playback. The restored image uses
the prior integer PDM clock; listening qualification remains deferred.

[Frozen evidence](../tests/results/esp32c3-web-tcp-probe-20261009/README.md)
includes the source snapshot, wrapper tests, linked audits, filtered serial
data, host connection timings, original reports and strict replay. Private
settings and TLS keys are excluded. No production-default change is made.
