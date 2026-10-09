# Integer-clock cross-codec qualification, 2026-10-09

## Decision

The HTTPS format matrix and mixed-codec switching pass, but **the complete
campaign does not pass**. A ten-minute HE-AACv2 run retains an initial-idle
WebUI TCP timeout and 11 delayed-DMA notification events near its end.
Do not promote this configuration as uninterrupted production playback.

The unchanged diagnostic `idf61-flac-int4` application has SHA-256
`28d24c6f7e1dd59ff2908f9e53d658f30eaf012a8af94ee34e3174cb5d75bc00`.
It uses ESP-IDF `9a97f6c54ec6`, verified QIO 80 MHz, full compact AAC/SBR/PS,
RX-only TLS reserve 17,058 B, adaptive input, 250/500 ms prefill, and four
extra FLAC input slots. Its integer PDM divider gives a nominal rate of
48,076.923 frames/s. The [separate quiet candidate](ESP32C3_QUIET_INT4_BUILD_20261009.md)
has not been qualified by these observations.

## Coverage and results

| Phase | Original gates | Additional review |
| --- | ---: | --- |
| 11 HTTPS fixtures, automatic and explicit decoder selection | 23/23 PASS, including final Stop | 22/22 saved playback/EOF observations pass |
| AAC transitions, WebSocket/generation checks, three mixed-codec cycles | 6/6 PASS | Two transitions and 33 switches pass; settled heap recovery passes |
| 600 s HE-AACv2 44.1 kHz stereo, TLS records grow from 1 KiB to 16 KiB | 3/5 PASS | Full format/record evidence passes; 11 DMA events, zero write errors; recovery baseline invalid |

No runtime fault is recorded in any completed capture. WebSocket and generation
checks retain the original runner's assertions; the independent replay covers
the saved REST observations. The matrix verifies stopped EOF observations,
not every exact persistent EOF status string. These runs do not replace the
final HTTP matrix, certificate-error tests, repeated OTA, public-radio tests
or listening/analog measurements.

The long test uses real-time pacing 1.0 and frequent WebUI requests. Its
post-warmup observation lasts 590.084 s; selected DMA samples cover about
585.9 s. CPU and task waits use their own complete interval coverage.

| Long-test measurement | Value |
| --- | ---: |
| Mean CPU busy | 61.32% |
| Decoder CPU | 42.40% |
| Decoder waiting for input, wall time | 0.112% |
| Decoder waiting for PCM space, wall time | 52.06% |
| Output waiting for PCM, wall time | 1.303% |
| Minimum free heap | 25,876 B |
| First / last median free heap | 26,308 / 26,232 B |
| Minimum and last largest free block | 14,336 B |
| Median / minimum RSSI | -66 / -78 dBm |
| Measured / whole observed DMA events | 11 / 11 |
| DMA write errors | 0 |

Wait times overlap and include scheduling; they are not CPU utilization.
CPU has no pass ceiling. The modest heap change during this playback is
not evidence that all previous heap-trend failures are resolved.

## Retained failures and next experiment

One of 5,106 traced TCP connections fails: request 28 in the long phase times
out after 5,014.85 ms during the initial stopped-board observation, before AAC
starts. Subsequent connections succeed. The same failure appears in two trace
layers; it is one outage. The original initial-idle gate fails, and the recovery
gate consequently fails with `Missing baseline`. Raw idle CPU samples remain
available but do not repair that missing qualified baseline. No OOM cause has
been established. Stopped-state Wi-Fi modem sleep is a hypothesis for a later
controlled comparison, not a demonstrated cause or an implemented fix.

All 11 DMA events occur in seven observation brackets between 537.084 and
592.194 seconds after playback observation starts. Overlapping decoder windows
show input waits and output windows show empty-PCM waits. Those are roughly
five-second brackets, not exact event times. The counters track discarded DMA
completion notifications, not an exact count of audible gaps.

The ordinary output clock consumes 1/624 extra audio seconds per wall second
relative to the resampler's 48,000-frame target: about 0.962 s in ten minutes.
The late onset is consistent with buffer depletion from this mismatch, but
does not alone prove causality or exclude source/network jitter. Next compare
a resampler targeting the actual nominal integer-clock rate, preserving the
integer PDM divider. Check sample counts, PCM interpolation error, CPU, memory,
long real-time delivery and the unchanged control. Keep this separate from
the fractional-clock option's unresolved analog-noise qualification.

## Timing, reproducibility and restoration

The current helpers use one `time.perf_counter()` epoch (Windows QPC,
reported resolution 100 ns); the host-clock change passes 48 tests. Original
sandbox socket/temp failures and successful authorized reruns remain in the
archive. The whole-DMA replay now accepts strictly increasing timestamps.
Historical low-resolution evidence is unchanged. A quiet build overlapped
the early matrix but finished before the sustained run; these are not matched
performance comparisons against historical runs.

The controller restores `idf61-qio80-8c1f2d2d`, verifies unchanged Wi-Fi,
playlist/settings, and observes three subsequent AAC-playing states. No
production default changes. The [frozen evidence and offline replay](../tests/results/esp32c3-integer-qualification-20261009/README.md)
contain original failures, complete filtered captures, source/image identities,
event brackets and restoration. Replay passes 145 byte-exact indexed files;
that confirms reproducibility of the failures as well as the successes.
