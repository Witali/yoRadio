# ESP32-C3 minimum input prefill experiment — 2026-10-09

## Hypothesis and implementation

The [staged queue diagnosis](ESP32C3_STAGED_FLOW_20261009.md) reproduced
completion-queue events while playing HE-AACv2 with bursty TLS records. The
decoder sometimes waited for encoded data while output waited for PCM.
With the maximum prefill set to 500 ms, a full queue could still start
decoding after approximately 9 ms. A minimum startup wait may preserve
delivery margin without allocating another buffer.

Commit `f2d94570` adds `CONFIG_YORADIO_INPUT_PREFILL_MIN_MS`, default zero.
For this experiment it is 250 ms; the existing maximum is 500 ms. Time is
measured from entry into prefill after leasing the first input packet.
Decoding starts when the queue is full and the minimum has elapsed, or when
the maximum expires. The queue need not remain full for 250 continuous ms.
The deadline is a scheduling deadline, not a hard real-time upper bound:
polling and preemption can delay the observation of its expiry.

The decoder retains its first packet lease. Only the producer adds queued
packets during the wait. Stop and a changed stream generation cancel the
wait. Queue capacity, TLS reserve, task priorities, decoder arithmetic,
receive timeouts and output data are unchanged. The option does not wait
for more data each time the running decoder exhausts its input.

## Build and host validation

The [saved candidate](../firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250/)
is `idf61-prefill-min250`, 1,622,096 bytes, SHA-256
`89d320f663bda6439456c95b6f47d09cd5cac2d434ff9fe85df568fa07fbae9c`.
Its application ELF identity is
`5a17d251e0a7b308dd011e850b1b1016afba0b46bc7dee6263b82f8c624a4ff3`.
The only effective configuration difference from `idf61-staged-flow` is
the 250 ms minimum. Both use full compact AAC/SBR/PS, the RX-only TLS reserve,
adaptive input, QIO 80 MHz, nominal fractional 48 kHz and queue profiling.
These are laboratory images with an extra test CA.

IRAM text remains 47,690 B, DRAM data 12,856 B and BSS 45,664 B. The linked
full AAC and HTTP reader audits pass. The unrelated CLZ block is inactive.
The 20-byte reduction in flash text is not a claimed speed optimization.

The host harness compiles the actual prefill function with deterministic
queue and clock stubs. All 88 cases pass under ASan/UBSan: ring and adaptive
queues, minimum values 0/1/250/500 ms, early and late producers, short input,
maximum deadline, cancellation, stale generation, clock wrap, coarse ticks,
reduced queues and zero capacity. These checks do not replace full decoder
integration or physical playback measurements.

## Physical comparison

The candidate plays the same HE-AACv2 44.1 kHz stereo fixture over TLS 1.2
AES-GCM at explicitly 1.0x delivery. Short cases use 1 KiB, 16 KiB, growing
and alternating records for 75 s each. A separate alternating-record case
runs for 600 s. The control observations come from the immediately preceding
staged-flow experiment. There is no matched short control for growing and
alternating records; those comparisons remain absent.

CPU, heap and selected queue counters exclude the first 10 s. Whole observed
counter intervals are also retained to avoid hiding startup events.
Sequential runs cannot isolate RF and compiler-layout effects. Original
playback/runtime/memory verdicts and additional DMA evidence are separate:
PASS in the former does not establish gap-free sound.

| Candidate record pattern, 75 s | Mean CPU busy | Minimum CPU-log free heap | Minimum largest block | Selected / whole observed DMA events | Input wait in selected flow windows |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 KiB | 59.355% | 26,076 B | 14,336 B | 0 / 0 | 0 ms |
| 16 KiB | 58.420% | 26,096 B | 14,336 B | 0 / 0 | 0 ms |
| Growing | 58.731% | 25,676 B | 14,336 B | 0 / 0 | 0 ms |
| Alternating | 58.528% | 26,120 B | 14,336 B | 0 / 0 | 0 ms |

The short phase passes all eight original entries with complete CPU, DMA and
queue-flow telemetry. All driver-write error deltas are zero. For 16 KiB
records, the matched control has four selected DMA events (six across the
whole observed interval) and 454.618 ms of encoded-input waiting; the candidate
has zero for both. Empty-PCM waiting falls from 807.996 to 372.505 ms in the
selected flow windows, and its timeouts from 92 to eight. Individual PCM wait
timeouts can occur while buffered DMA continues playing, so those eight
timeouts do not establish eight sound gaps.

Actual prefill logs are 500 ms for small records, 259 ms for large records,
510 ms for growing records, and 259 ms for alternating records. These match
the intended minimum/deadline behavior with polling and scheduling delay.

## Ten-minute result

Both images completed their separate 600 s alternating-record observations.

| Measurement | Minimum 0 ms (control) | Minimum 250 ms (candidate) |
| --- | ---: | ---: |
| Selected DMA completion-queue events | 5 | 0 |
| Whole observed counter-interval events | 6 | 0 |
| Driver-write errors | 0 | 0 |
| Encoded-input waiting in complete selected flow windows | 1,619.286 ms | 0 ms |
| Encoded-input timeouts | 39 | 0 |
| Output waiting for PCM in complete selected flow windows | 4,693.634 ms | 3,270.936 ms |
| Empty-PCM timeouts | 285 | 45 |
| Decoder waiting for PCM space, share of wall time | 55.507% | 55.832% |
| Mean CPU busy | 58.656% | 58.468% |
| Minimum CPU-log free heap | 26,260 B | 25,668 B |
| Minimum largest block | 18,432 B | 14,336 B |
| Median / minimum RSSI | -64 / -70 dBm | -63 / -70 dBm |

The candidate passes all 13 original entries across the short and long
phases. Both phases retain complete telemetry, zero recorded allocation,
decoder, panic, watchdog and client transport faults, and zero driver-write
errors. No DMA completion-queue events were recorded anywhere between the
captured counters in any candidate case. Task-stack minimum free space is
1,116 B for output, 2,672 B for decoding and 2,608 B for streaming.

This is evidence that the startup margin helps this controlled bursty TLS
fixture. It is not a guarantee against longer network outages, all radio
stations, or analog artifacts. The slightly lower CPU value is not claimed
as a speed optimization; the smaller measured largest free block is retained
rather than described as a RAM saving. Flow percentages belong to separate
tasks and must not be added together as CPU utilization.

Neither minimum prefill nor fractional clocking is promoted to production
by this experiment. Listening is deferred at the user's request; no analog
capture is available.

The controller verified the fresh nominal 48 kHz clock registers and four
mapped QIO 80 MHz application CRC reads. It then restored
`idf61-qio80-8c1f2d2d` by application-only OTA, checked unchanged Wi-Fi,
playlist and settings, and recorded three successful AAC 44.1 kHz stereo
playback observations. The newer TLS numeric-error filter was integrated
only after this run and restoration; this archive uses its original frozen
capture code.

## Remaining acceptance work

The later [full regression](ESP32C3_MIN_PREFILL_REGRESSION_20261009.md) passes
the codec matrix, PCM-tail and switching checks, but retains one WebUI connect
timeout during exact HE-AAC EOF observation and 84 heavy-FLAC DMA queue overruns.
The controlled HE-AACv2 improvement above does not qualify all-codec continuity.

Before changing defaults, resolve the heavy-FLAC continuity finding and the
interrupted EOF observation, then verify TLS closures, certificate rejection,
OTA during full HE-AACv2 playback and the final quiet memory configuration.
Repeat the relevant regression when firmware changes. Existing results for a
different image remain useful controls but do not qualify this image automatically.

## Evidence and replay

The [frozen archive](../tests/results/esp32c3-min-prefill-20261009/) retains
the original verdicts, per-request transport timing, build audits, 88 host
cases, 83 source snapshots and the explicit comparison with the preceding
control archive. The measured firmware implementation is `f2d94570`; exact
source overlays are recorded in the artifact manifest. Public test
certificates are included, but private keys and saved settings are not.

```powershell
python tests/results/esp32c3-min-prefill-20261009/replay.py --output .build/replay-min-prefill
```

Use a new output directory. The replay verifies hashes and reproduces the
summary, identity checks and comparison, including missing short control
cases. It does not reinterpret original verdicts or claim acoustic validation.
