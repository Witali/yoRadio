# ESP32-C3 copied RX packet sizing, 2026-10-07

## Result

A bounded startup packet pool is worth testing to isolate network allocations
from the codec heap. This measurement supports that experiment, but does not
implement a pool or establish a safe production capacity. A pool must replace
the observed dynamic allocations. It cannot remove the memory occupied by a
growing receive queue.

The physical 600-second HE-AACv2 44.1 kHz stereo run with WebUI requests recorded
**16 simultaneously live copies** and **17,664 B peak allocation capacity**.
There were **23,941 successful allocations and 23,941 final releases** by the
last post-Stop snapshot; zero live buffers remained. Allocation failures,
input rejections and lost tracking entries were all zero. These cumulative
counters include activity since boot, including setup and idle traffic.

The original progressive-heap-loss gate remains **FAIL**. Runtime, idle and
Stop recovery checks passed. This is not acoustic/sample-continuity qualification.

## What was measured

The off-by-default `CONFIG_YORADIO_RX_COPY_PROFILE` wraps the pinned IDF 6.0.2
native-copy handoff. Copies still use `pbuf_alloc(PBUF_RAW, ..., PBUF_RAM)`.
The driver buffer is released after copying; an owner is removed only at the
actual final `mem_free()`, including reference-counted and chained pbufs.
The final ELF contains the correct STA/AP callbacks and free hook.

The target adds 888 B static RAM: 768 B for 64 tracked owners, 112 B counters,
8 B report timestamp. A per-free search and five-second log records affect
timing. This build is for memory sizing, not a production CPU comparison.

Allocation capacity includes the 16-byte target pbuf and allocation alignment,
but excludes allocator block headers. It does not count the original transient
Wi-Fi RX allocation, TLS, TX buffers, sockets, TCP control blocks or codec RAM.
The profiler accounts for lifetimes; it does not measure a distribution of
retention time in milliseconds.

## Packet sizes and simultaneous ownership

| Received frame length, B | Cumulative allocations | Independent live peak | Live after Stop |
| --- | ---: | ---: | ---: |
| 0–128 | 17,926 | 5 | 0 |
| 129–512 | 3,506 | 5 | 0 |
| 513–1152 | 1,445 | 11 | 0 |
| 1153–1600 | 1,064 | 11 | 0 |
| 1601–65535 | 0 | 0 | 0 |
| **Total** | **23,941** | **16 simultaneous** | **0** |

The largest observed frame was 1,494 B. Class peaks occur at different times:
their sum, 32 slots, is not the simultaneous peak of 16. Conversely, 16 total
slots would leave no count headroom over this single observation.

During the load window, 117 intact CRC snapshots covered all 600 seconds;
the largest host receive-time gap was 5.406 seconds. The allocation/free delta
between its first and last snapshots covered 593.047 seconds, not the full
600 seconds: 22,883 arrivals and 22,871 releases. Do not label those deltas as
exact whole-window totals.

| Sampled ownership | First steady minute | Last minute |
| --- | ---: | ---: |
| Median live copied packets | 0 | 11 |
| Median allocation capacity | 0 B | 13,400 B |
| Maximum sampled allocation capacity | 208 B | 14,412 B |
| Median aggregate uncredited TCP payload | 0 B | 9,472 B |

The first steady minute excludes the initial ten seconds. TCP credit and RX
allocation snapshots are asynchronous; logical TCP payload is already inside
the packet data and must not be added again. These values support receive-queue
retention as a contributor to heap pressure, not an exact subtraction explaining
every heap byte. Event-updated peaks also capture bursts between log samples;
the maximum sampled live count was only 14 while the true tracked peak was 16.

## Playback and recovery

| Measurement | Result |
| --- | ---: |
| Observed load | 600.000 s |
| WebUI status samples | 3,244 |
| Maximum status request time | 234 ms |
| Minimum sampled RSSI | −69 dBm |
| CPU records / decoder windows, after warmup | 116 / 118 |
| Diagnostic mean / peak busy CPU | 68.89% / 70.2% |
| Diagnostic decode time / audio duration | 49.27% |
| Decoded audio duration / wall time | 1.00159 |
| Minimum sampled free heap | 27,712 B |
| Minimum sampled largest block | 11,776 B |
| First / last three-sample median heap | 43,556 / 31,700 B |
| First / last three-sample median largest block | 32,768 / 16,384 B |
| Idle heap median before / after | 146,816 / 146,864 B |
| Idle largest block before / after | 114,688 / 114,688 B |
| Idle task count before / after | 17 / 17 |
| Runtime / Stop recovery | PASS / PASS |
| Progressive heap gate | **FAIL, retained** |

CPU is informational. The instrumentation changes code placement and timing,
and RF/host scheduling differ between runs; the lower decode time here is not
evidence that preallocation accelerated decoding. No fixed pool was installed.
The earlier uninstrumented [matched comparison](ESP32C3_RX_MATCHED_20261007.md)
remains the relevant ordinary/native-copy CPU observation.

## Implications for a pool

- Preallocation can make packet storage predictable and keep these repeatedly
  allocated buffers out of the general heap used by AAC.
- It reserves RAM even when idle. Reserving 16 × 1,600 B already consumes
  25,600 B before metadata, versus 17,664 B observed peak allocation capacity.
  Those 16 slots also lack count headroom. Preallocation is not automatically
  a reduction in total RAM.
- Separate size classes need shared spare capacity or another way to handle
  changing packet-size mixtures. Reserving each independent class peak would
  require 33,472 B of payload capacity before metadata, wasting much of the
  potential saving.
- Retain a path for control traffic and WebUI. Test bounded exhaustion rather
  than blocking Wi-Fi/lwIP or silently using an unlimited heap fallback.
- Select production capacity only after full-rate AAC/other codecs, verified
  HTTPS, reconnect and OTA trials. This is one HTTP fixture with WebUI load,
  not a complete network workload envelope.

See the [startup pool plan](ESP32C3_NETWORK_PACKET_POOL_PLAN.md) for ownership,
exhaustion and acceptance requirements. The profiler remains disabled by default.

## Retained evidence and reproduction

- `tests/results/esp32c3-rx-copy-profile-20261007/`: original study/OTA reports,
  telemetry, status samples, host tests, exact sources, configuration, linked
  call evidence, replay summary and integrity manifest.
- `firmware/development/esp32c3-rx-copy-profile/`: diagnostic application and
  exact configuration; ELF SHA-256
  `e38cff51e1e7d552b675ee4e94a9951a0ae9d11b48908aa147e1fe3927b31f68`.
- Host ASan/UBSan exercised actual SDK pbuf/mem code, including refcount, chains,
  trim, failure, overflow and concurrent release. Parser negative tests reject
  corrupted, incomplete and inconsistent records.
- Ordinary `esp32c3-station-timeout` was restored by OTA after measurement;
  both OTA transitions passed HTTP identity/settings checks. The first
  transition passed independent serial health. The restoration capture ended
  with `serial capture interrupted: incomplete final line`; its independent
  serial-health **FAIL** is retained. This does not invalidate the already
  completed study capture, but restoration is not a fully qualified serial
  trace. A subsequent HTTP check confirmed the ordinary image, saved-station
  playback, timeout 10 seconds and RSSI −62 dBm; `board-final.json` retains it.

```text
python tests/test-rx-copy-profile.py
python tests/test-rx-copy-profile-evidence.py
python tools/esp32c3_tests/rx_copy_profile.py tests/results/esp32c3-rx-copy-profile-20261007/study/performance.json --status tests/results/esp32c3-rx-copy-profile-20261007/study/status.json --output <new-summary.json>
```
