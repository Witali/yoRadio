# ESP32-C3 matched prefill and AAC EOF follow-up — 2026-10-09

## Result

The matched 0 → 250 → 0 ms comparison does **not reproduce the earlier 84
FLAC DMA queue events**. All three 180-second runs have zero events in the
selected steady playback interval. The 250 ms run records one event during
the first ten seconds; it remains an adverse observation, not a discarded
warmup result. No production default is changed.

All eight targeted HE-AAC/HE-AACv2 exact EOF checks pass across HTTP and
HTTPS. The previous WebUI connection timeout remains an unresolved original
failure in the [broader regression](ESP32C3_MIN_PREFILL_REGRESSION_20261009.md).
These new results do not retrospectively turn it into a pass.

## Matched images and method

Both diagnostic images use the same firmware implementation and profiling.
Their only effective SDK configuration difference is
`CONFIG_YORADIO_INPUT_PREFILL_MIN_MS`: 0 versus 250. Both retain the 500 ms
maximum prefill timeout, QIO 80 MHz, full compact AAC/SBR/PS, fractional nominal
48 kHz, the 17,058-byte RX TLS reserve and the same adaptive input allowance.
Output/decoder/stream task priorities remain 8/7/5; the scheduler tick is 1 ms.

| Image | Version | Application SHA-256 |
| --- | --- | --- |
| New matched control | `idf61-prefill-min0` | `1b5ba21bde04a27d7a95998afc53f187d4b1acee8d57ab8dd58d480b177d41f0` |
| Existing candidate | `idf61-prefill-min250` | `89d320f663bda6439456c95b6f47d09cd5cac2d434ff9fe85df568fa07fbae9c` |

The control is built from `2a180938` with the recorded local source overlay.
It is saved under `firmware/development/esp32c3-idf-6.1-r9a97-prefill-min0/`.
Its 1,622,112-byte application has 47,690 B IRAM text, 12,856 B DRAM data and
45,664 B BSS, matching the candidate's RAM section sizes. Full AAC/HTTP linked
code audits and the PCM flush/discard audit pass. The existing 88 host prefill
cases cover identical implementation hashes. The unrelated inactive CLZ
CMake block is preserved as provenance but is not compiled.

The archived Kconfig files differ in help wording; verification compares
their non-help content as well as effective configuration. Build version and
binary layout differ, so this is not a byte-identical timing comparison.

Each FLAC run starts after a fresh app-only OTA boot and uses the same
610-second, 48 kHz stereo 16-bit fixture, observed for 180 seconds over
certificate-verified HTTPS. Files are delivered with normal TCP backpressure,
without artificial pacing, alongside frequent WebUI requests. The encoded
rate is approximately 1,283.224 kbit/s. There are no test retries, extended
connection timeouts or CPU-budget rejection gates. Settled idle memory is
checked before and after every run.

## Heavy FLAC comparison

CPU, heap, decoder and selected DMA measurements exclude the first ten
seconds. RSSI and maximum WebUI response use the full playback observation.
The whole-observation DMA row includes the early interval. Counts span
recorded counter boundaries, without extrapolation between missing endpoints.

| Measurement | 0 ms before | 250 ms | 0 ms after |
| --- | ---: | ---: | ---: |
| Mean CPU busy | 79.394% | 80.003% | 79.095% |
| Peak sampled CPU busy | 80.1% | 80.8% | 80.0% |
| Selected DMA queue events | 0 | 0 | 0 |
| Whole-observation DMA queue events | 0 | 1 | 0 |
| Selected driver-write errors | 0 | 0 | 0 |
| Minimum sampled free heap | 57,612 B | 57,284 B | 57,316 B |
| Minimum sampled largest block | 32,768 B | 36,864 B | 32,768 B |
| Median / minimum RSSI | -67 / -68 dBm | -63 / -68 dBm | -67 / -70 dBm |
| Maximum WebUI response | 141 ms | 1,110 ms | 125 ms |
| Decoder input wait, selected intervals | 40.666 s | 40.860 s | 40.712 s |
| Decoder input timeouts | 0 | 0 | 1 |
| Output wait for PCM, selected intervals | 18.632 s | 18.944 s | 18.319 s |
| Output PCM polling timeouts | 2,977 | 3,046 | 3,030 |
| Settled free heap after stop, both samples | 133,024 B | 133,128 B | 133,124 B |

All required telemetry coverage checks pass. The settled largest free block
is 106,496 B with 17 tasks in all three runs, and independent heap recovery
checks pass. Queue waits include normal pipeline scheduling; a PCM polling
timeout does not mean the hardware ran out of playable DMA data. The final
control has one input timeout without a recorded DMA event.

In the 250 ms run, the sole event is between the cumulative samples at
238905.296 and 238910.312 on the controller's monotonic clock. The selected
steady interval starts at 238914.609. The overlapping server delivery windows
contain a maximum socket write of 219 ms. WebUI request 60 also spends 1,031 ms
establishing a TCP connection and succeeds. These observations do not isolate
Wi-Fi, TCP, host scheduling or startup behavior as the cause. A DMA
completion-queue event is not a measured acoustic gap.

This sequential A/B/A result removes the earlier profiling mismatch but
does not establish statistical equivalence or universal continuity. CPU load,
RSSI and free-block layout vary between runs. The previous 84-event run and
the earlier successful ten-minute HE-AACv2 result remain valid observations.
Minimum startup delay alone cannot prevent later network stalls: four
2,060-byte input slots contain at most about 51 ms of this high-rate FLAC.

## Exact AAC EOF checks

| Transport | HE-AAC 48 kHz stereo | HE-AACv2 44.1 kHz stereo |
| --- | --- | --- |
| HTTP | AUTO and explicit AAC: PASS | AUTO and explicit AAC: PASS |
| HTTPS | AUTO and explicit AAC: PASS | AUTO and explicit AAC: PASS |

The runner checks decoded playback before EOF, at least two stopped REST
observations, cleared PCM fields, retained decoded format, durable
`stream ended` state and stopped WebSocket state. Independent replay confirms
the saved REST EOF and format observations. WebSocket verdicts are retained
from the original runner. No failed client requests are recorded.

Across all five phases, **22/22 original report entries pass**, including
setup, heap recovery and stop entries. This is not 22 distinct formats.
The extended log scan records no allocation, decoder, TLS, panic, watchdog,
unexpected-reset or serial-capture fault. These targeted EOF cases supplement
the earlier full codec matrix; exact HTTPS EOF for every other fixture is
still outside this run's coverage.

## Restoration and remaining qualification

Four fresh test boots verify nominal 48 kHz registers, actual QIO 80 MHz and
four matching mapped application CRC reads each (16 total). Clock readback
confirms a nominal divider ratio, not absolute crystal accuracy or analog
noise performance.

The controller restores the saved quiet `idf61-qio80-8c1f2d2d` application,
verifies unchanged Wi-Fi, playlist and settings, and records three successful
playing states. Laboratory images are not left running. The
[quiet fractional candidate](ESP32C3_QUIET_MIN_PREFILL_BUILD_20261009.md) is
still not qualified for production.

Listening is deferred because the user is unavailable. Fractional clock
mode remains experimental and disabled by default until the sound-quality
comparison can be completed. No analog capture was performed.

Remaining work includes diagnosing intermittent input/transport stalls,
qualifying TLS closure/framing and certificate rejection on the selected
image, resolving the previously unclassified OTA TLS errors, and testing
the quiet build with public radio and OTA. Keep original failures alongside
new observations rather than replacing them with a successful rerun.

## Reproducible evidence

The [archive](../tests/results/esp32c3-prefill-matched-20261009/) contains 170
indexed files (5,329,722 bytes): original observations, request timing, server delivery windows, build audits,
81 frozen support sources, 14 firmware source snapshots, both image manifests
and configurations, public test certificates and restoration verification.
Private settings and TLS keys are excluded. The byte-exact index and offline
replay preserve original gates separately from continuity findings.

```powershell
python tests/results/esp32c3-prefill-matched-20261009/replay.py --output .build/replay-prefill-matched
```

Use a new output directory. The physical controller is a record of the
procedure; a new hardware run requires fresh paths and a valid trusted test
certificate. Offline replay does not contact the board or network.
