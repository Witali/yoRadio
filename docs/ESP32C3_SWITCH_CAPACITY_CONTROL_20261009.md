# ESP32-C3 matched queue-capacity switching controls

The additional FLAC queue capacity remains **disabled by default**. Two
fresh-boot controls retained their largest free block through switching,
EOF and TLS record growth. Both expanded-queue runs lost contiguous capacity
across that sequence. One also had a WebUI connection timeout. This supports
further allocation-owner tracing before adoption; it does not identify the
allocation responsible or prove that the timeout has the same cause.

This follows the [FLAC input-growth experiment](ESP32C3_FLAC_INPUT_GROWTH_20261009.md).
Its earlier failed gates and nonzero FLAC DMA observations remain unchanged.

## Procedure and identity

The same saved binaries run on the physical C3 in extra-slot order **0 / 4 /
4 / 0**, each after app-only OTA and a fresh boot. Their only active SDK
configuration difference is `CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS`. Both
retain full compact AAC/SBR/PS, original sample rates, the 17,058-byte TLS RX
reserve, QIO 80 MHz and experimental nominal 48 kHz fractional PDM output.
Sources and linked codec audits are reused through a hash-pinned reference
to the preceding archive. No firmware implementation or default changed.

Each boot runs:

1. Three FLAC 48 kHz stereo -> HE-AAC 48 kHz stereo -> HE-AACv2 44.1 kHz
   stereo cycles, seven seconds per stream, Stop between streams and twelve
   seconds of settled idle after each cycle.
2. Four trusted HTTPS EOF cases: FLAC and HE-AACv2, each in AUTO and explicit
   codec mode.
3. A requested 75-second HE-AACv2 stream whose TLS plaintext records grow
   from 1 KiB to 16 KiB after playback starts, with twelve-second settled
   idle measurements before and after.

Both variants use the same fixtures, server settings and test sources.
CPU is informational, without a rejection threshold. App identities,
actual clock registers, actual QIO 80 MHz settings and four mapped-image
CRC reads per installation pass verification. These are two repetitions per
variant, not a statistical characterization; startup scheduling, Wi-Fi and
the binaries' different layouts remain potential influences.

## Memory across the complete sequence

Values below are medians of the settled idle samples, in **KiB**. The first
baseline follows the first complete switch cycle, not startup before any
playback. All checkpoints contain 17 tasks.

| Run | Extra slots | Switch cycle 1 | Cycle 2 | Cycle 3 | After EOF / before TLS test | After TLS test |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Control 1 | 0 | 108 | 108 | 108 | 108 | 108 |
| Expanded 1 | 4 | 100 | 100 | 100 | 92 | 92 |
| Expanded 2 | 4 | 108 | 96 | 92 | 96 | 96 |
| Control 2 | 0 | 104 | 104 | 104 | 104 | 104 |

Expanded 2 fails the original switching gate with a **16,384-byte** loss.
Expanded 1 passes the separate original stages, but loses **8,192 bytes**
between the switching series and the next settled baseline. Expanded 2
regains 4 KiB after EOF, leaving a **12,288-byte** loss against its first
baseline at the final checkpoint.

The supplementary `compare.py` therefore carries the first switch baseline
across both later checkpoints, applying the existing tolerances: at most
2,048 bytes of total-free loss, 4,096 bytes of largest-block loss, and no task
increase. Both controls pass; both expanded runs fail at both later
checkpoints. These paired endpoints are correlated observations, not four
independent failures. Original stage verdicts remain intact.

Total-free checkpoint medians stay between **132,998 and 133,128 bytes**.
This is a contiguous-capacity problem without a comparable total-free loss;
the logs alone do not identify a leaking or long-lived owner.

The [IDF heap documentation](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/system/heap_debug.html)
distinguishes total free memory from the size of a single available
allocation. In this pinned SDK, `multi_heap_get_info()` additionally applies
`tlsf_fit_size()` to the raw largest free span. The API value is rounded to
an allocation size class: an 8 KiB change is not evidence that exactly 8 KiB
of payload remains allocated. The inspected, unmodified SDK files are saved
in this archive under `sdk/`. This distinction does not waive the capacity
recovery gate.

## Playback, EOF and TLS results

All **36 switch playback observations** and **16 EOF cases** pass their
format/state checks. HE-AAC retains 48 kHz stereo and HE-AACv2 retains
44.1 kHz stereo. Expanded runs log exactly three queue expansions during
switching and two during FLAC EOF; no expansion is logged during the
subsequent HE-AACv2 record-growth test.

| HE-AACv2 TLS test | Original result | Weighted CPU | Minimum free heap | Minimum largest block | Observed DMA queue events / write errors |
| --- | --- | ---: | ---: | ---: | ---: |
| Control 1 | PASS | 58.75% | 26,184 B | 18,432 B | 0 / 0 |
| Expanded 1 | PASS | 59.40% | 26,120 B | 14,336 B | 0 / 0 |
| Expanded 2 | FAIL: connection timeout | 59.33%* | 26,208 B* | 16,384 B* | 0 / 0* |
| Control 2 | PASS | 58.82% | 26,028 B | 14,336 B | 0 / 0 |

CPU/heap figures use the unchanged steady-window analyzer. Both whole
observed and selected DMA event deltas are zero in these TLS tests. They
are queue-service counters, not an acoustic recording or proof of gap-free
output. These runs do not replace the preceding heavy-FLAC load comparison.

\* Expanded 2 aborts its requested 75-second observation at **67.015 seconds**,
including a **5.015-second connection timeout** on request 375. The trace
records that one failure at both `connect` and enclosing request levels.
Its last successful status requests are not a latency bound on the failed
request. The runner never freezes the final TLS record-acceptance snapshot;
replay explicitly keeps that check failed and telemetry incomplete. Partial
CPU, heap and DMA observations cannot turn it into a successful full run.
Median RSSI is -67 / -63 / -63 / -67 dBm in run order.

Overall **46/48 original report entries pass**. The two failures are Expanded
2's switching-memory gate and TLS test timeout. The supplementary cross-stage
gate also rejects Expanded 1. No decoder/allocation/TLS fault, panic,
watchdog or unexpected reset is recorded in the filtered serial journals.
The network timeout's cause is unresolved.

## Restoration, replay and next work

The controller restored `idf61-qio80-8c1f2d2d`, application SHA-256
`21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a`.
Image identity, unchanged Wi-Fi/playlist/settings and three playing AAC
44.1 kHz stereo observations pass. The restored production image uses the
previous integer clock. Listening is deferred because the user is currently
unavailable; fractional output remains experimental and default-off.

[Frozen reports and replay](../tests/results/esp32c3-switch-capacity-control-20261009/README.md)
include raw technical observations, original failures, cross-stage checks,
the physical controller and pinned shared-source evidence. Private settings
and TLS private keys are excluded. Run offline from the worktree:

```powershell
python tests/results/esp32c3-switch-capacity-control-20261009/replay.py --output .build/switch-capacity-replay-new
```

Next, use the existing heap-owner probe on this same sequence, retaining the
first baseline across every Stop/EOF boundary. Identify live allocations
that divide the free region before changing allocation policy. Investigate
the WebUI connection timeout separately. Full public-radio continuity, the
candidate's negative OTA suite and analog clock qualification remain open.

Follow-up: the [owner-trace and retention study](ESP32C3_INPUT_RETENTION_20261009.md)
reproduces displacement of baseline input buffers and tests a targeted
ordinary-shrink fix. The observations and failures above remain unchanged.
