# ESP32-C3 matched delivery pauses, 2026-10-09

## Decision

The expanded FLAC input queue reduces delayed-DMA-service events in this
controlled pause experiment: **16**, versus **25 and 23** with the ordinary
queue. It does not eliminate the events around approximately 200 ms source
pauses. Keep extra FLAC slots **disabled by default** pending final buffering
and production qualification. This is a bounded capacity comparison, not an
acoustic measurement or proof that every network interruption is avoidable.

Full-rate HE-AACv2 plays after expanded FLAC, with zero measured DMA event/error
increments and settled memory recovery. The full AAC observation has a separate
timestamp-integrity failure; the accepted post-warmup interval is stated below.

## Controls and procedure

The unchanged images from the [integer-clock comparison](ESP32C3_FLAC_INTEGER_20261009.md)
use pinned ESP-IDF `9a97f6c54ec6`, QIO 80 MHz, the ordinary PDM divider
(nominal 48,076.923 Hz), full compact AAC/SBR/PS, the TLS RX reserve and input
prefill. The only configuration difference between the images is
`CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS=0/4`: 4/8 total input slots. Encoded
payload capacity is 8,192/16,384 B; packet storage is 8,240/16,480 B, excluding
allocator overhead. No firmware is rebuilt for this experiment.

The controller installs the images through native app-only OTA in
control/expanded/control order. Each boot checks image identity, PDM registers,
actual QIO 80 MHz and four full-image CRC reads. Each phase plays 180 seconds
of the same HTTPS FLAC fixture with 100 ms WebUI polling plus request duration,
then checks settled Stop memory. The expanded phase also plays HE-AACv2 at
44.1 kHz stereo for 180 seconds and checks recovery again. CPU has no ceiling.

The FLAC fixture is `stress-flac-48000-2ch-16bit-610s`, SHA-256
`3971068e09afad15702e257d54d6ad5600e847511e4bd9fac6c3e47917f739b3`.
The shared server pauses at identical encoded-byte positions, then resumes
unpaced finite-file delivery. Continuous AAC retains pacing ratio 1.0; it
does not reach the first pause position in this run. All phases request and
read back `SO_SNDBUF=4096`. The older unpaused experiment used the OS-default
send buffer and is therefore not a matched pause/no-pause control.

The new server implementation in `bb764e80` passes six dedicated host tests,
including exact payloads over HTTP and verifying HTTPS, pause boundaries,
catch-up, repetition and cancellation. Existing pacing (4), delivery-statistics
(2) and recovery (2) tests also pass. Saved test observations distinguish the
new test's recorded result from the raw regression logs.

## Measured results

Complete post-warmup DMA windows span about 165.17 seconds for FLAC and
165.235 seconds for AAC. Wait percentages include waiting and preemption;
they are not CPU utilization. All four measured telemetry windows pass.

| Measurement | FLAC control before | FLAC expanded | FLAC control after | HEv2 after expanded FLAC |
| --- | ---: | ---: | ---: | ---: |
| Mean CPU busy | 79.52% | 80.30% | 79.97% | 62.11% |
| Decoder input-wait wall time | 24.69% | 0.239% | 25.17% | 0.00% |
| Output empty-PCM wait wall time | 11.49% | 0.161% | 11.88% | 1.29% |
| Measured DMA queue events | 25 | 16 | 23 | 0 |
| Whole observed DMA queue events | 25 | 16 | 23 | Rejected timestamps |
| Measured DMA write errors | 0 | 0 | 0 | 0 |
| Minimum free heap, CPU samples | 57,596 B | 48,976 B | 57,340 B | 25,600 B |
| Minimum largest block | 38,912 B | 36,864 B | 38,912 B | 14,336 B |
| Median RSSI | -63 dBm | -62 dBm | -63 dBm | -66 dBm |
| Settled Stop heap recovery | PASS | PASS | PASS | PASS |

The original controller gates pass **24/24** (7/7, 10/10, 7/7). They do not
require zero DMA queue events. The separate stricter measured criterion fails
all three FLAC runs and passes AAC. No runtime fault is recorded by the
post-capture checks. All **4,172 traced TCP connections succeed**; this does
not establish a repair for the earlier intermittent WebUI timeout.

After expanded FLAC, free heap is 133,112 B; after AAC it is 133,112–133,116 B,
versus 133,076–133,088 B initially. All phases retain a settled largest block
of 102,400 B and 17 tasks. These observations support reuse/release in this
bounded sequence, not an explanation for every earlier heap-trend failure.

## Actual pauses and surrounding DMA intervals

Each counter interval starts with the last observed DMA sample before the
host pause and ends with the first sample at least one second after it.
These are several-second brackets, including any unrelated events within
them. Socket writes are not acknowledgements or board-arrival timestamps;
TCP/TLS and receiver buffering can mask a host pause.

| Encoded offset | Requested pause | Actual ms: before / expanded / after | DMA events before | Expanded | After |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3,000,000 B | 50 ms | 60.2 / 58.5 / 53.5 | 0 | 0 | 0 |
| 6,000,000 B | 100 ms | 106.2 / 101.8 / 113.6 | 0 | 0 | 0 |
| 9,000,000 B | 200 ms | 202.6 / 214.3 / 213.9 | 12 | 10 | 12 |
| 12,000,000 B | 50 ms | 60.7 / 57.7 / 63.5 | 0 | 0 | 0 |
| 15,000,000 B | 100 ms | 108.9 / 100.3 / 103.7 | 3 | 0 | 1 |
| 18,000,000 B | 200 ms | 202.6 / 211.5 / 211.7 | 10 | 6 | 10 |

All 18 pauses complete at their intended byte positions; captured delivery
statistics finish without dropped windows. Mean completed host body-write
rates are 160,342 / 160,436 / 160,338 B/s over the respective responses.
These averages include backpressure and pauses and do not prove timely
arrival at the board. The event increases fall within the pause brackets;
this supports delivery/buffering sensitivity but does not isolate each cause.

## AAC timing limitation

The post-warmup AAC interval records 15,516 DMA writes and 31,776,768 bytes,
with zero event/error increments. Full-rate stereo status and memory checks
pass. The separate whole-observation replay rejects two early DMA samples
with the same host timestamp `256451.875`; their device log timestamps are
224,393 and 224,397 ms. Both original rows remain in the archive.

The host uses Python 3.12 `time.monotonic()` backed by `GetTickCount64()` at
15.625 ms resolution. Pause durations use `perf_counter()` independently;
they do not mix clock epochs with event timestamps. Before further
whole-interval comparisons, use one common high-resolution timestamp source
across controller, server and captures. Changing only the USB capture clock
would make its timestamps incomparable. Do not repair historical evidence or
weaken the duplicate-timestamp rejection.

## Remaining work and restoration

The [current qualification checklist](ESP32C3_MEMORY_STABILITY_TODO.md#remaining-qualification-work-2026-10-09)
separates implemented AAC compression from unresolved FLAC delivery, TLS and
memory policy, intermittent WebUI connections and final all-format/OTA
qualification. Define and verify the buffering/rebuffering response to longer
interruptions; queue growth alone does not establish continuous output. Keep
the exact-clock option separate until listening or analog noise testing.

The controller restores `idf61-qio80-8c1f2d2d`, verifies unchanged Wi-Fi,
playlist and settings, and checks three subsequent playing observations.
The restored application SHA-256 is
`21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a`.
No production defaults change. No listening or analog recording was performed.

[Frozen evidence and offline replay](../tests/results/esp32c3-delivery-pauses-20261009/README.md)
include the original passing and failing gates, exact source/image provenance,
actual pause timing, raw filtered observations and restoration. Private keys
and user settings are excluded. A successful offline replay means those
verdicts are reproduced, not that all hardware acceptance criteria passed.
