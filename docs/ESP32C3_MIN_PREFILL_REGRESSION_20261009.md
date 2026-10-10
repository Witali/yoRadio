# ESP32-C3 minimum-prefill regression — 2026-10-09

## Result

The minimum-prefill candidate passes the full codec matrix and memory gates,
but one exact EOF check is interrupted by a WebUI connection timeout.
**Heavy FLAC also requires continuity investigation**: the three-minute
HTTPS run records 84 DMA completion-queue overruns in three groups. Original
PASS verdicts are retained separately from this finding. They do not establish
uninterrupted sound.

The [matched follow-up](ESP32C3_PREFILL_MATCHED_20261009.md) passes all eight
targeted HTTP/HTTPS AAC EOF checks and does not reproduce the 84-event FLAC
finding in a 0 → 250 → 0 ms comparison. It retains one early DMA event in
the 250 ms run. Both this report's original failures and the new observations
remain recorded; the follow-up does not establish their cause.

The candidate is `idf61-prefill-min250`, application SHA-256
`89d320f663bda6439456c95b6f47d09cd5cac2d434ff9fe85df568fa07fbae9c`, ELF identity
`5a17d251e0a7b308dd011e850b1b1016afba0b46bc7dee6263b82f8c624a4ff3`.
It uses QIO 80 MHz, full compact AAC/SBR/PS, a 17,058-byte RX-only TLS reserve,
adaptive input, 250/500 ms minimum/maximum prefill and fractional nominal
48 kHz. The frozen runner includes the numeric TLS error filter from `92f4d042`.

## Physical coverage

**146/147 original report entries pass**. This count includes setup,
recovery and stop entries; it is not 147 distinct audio formats. The failed
EOF case remains failed in the independent replay.

| Phase | Original entries passed |
| --- | ---: |
| 60 tiny FLAC tails, warmup and stop | 62/62 |
| 22 HTTP codec/selection cases and stop | 23/23 |
| 22 HTTPS codec/selection cases and stop | 23/23 |
| Heavy FLAC, idle recovery and stop | 4/4 |
| AAC transitions, network faults and WebSocket | 10/10 |
| 33 station changes across three cycles and stop | 2/2 |
| 22 exact HTTP EOF cases and stop | 22/23 |

The codec matrix contains MP3, FLAC, Vorbis, Opus, AAC-LC, HE-AAC and HE-AACv2,
including 22.05 kHz mono, 44.1 kHz stereo and 48 kHz stereo cases. All eleven
fixtures run with automatic and explicit codec selection on each transport.
The separate exact terminal-state suite currently covers HTTP only; HTTPS
matrix cases check stopped playback but do not independently check the durable
`stream ended` text and WebSocket state for every codec.

The tiny FLAC cases test the final partial output block on HTTP and HTTPS.
They replay driver-accepted byte/frame counts from serial evidence, not
physical DMA drain or captured analog PCM. WebSocket verdicts come from the
original runner; the offline EOF replay independently checks the saved REST
samples.

### Incomplete HE-AAC 48 kHz EOF observation

The explicit-codec `he-48000-stereo` case retains `FAIL — URLError`.
Two REST observations already show `audio=false`, `stream ended` and zero PCM
rate/channels. The next polling request fails while establishing the TCP
connection after 5,000 ms. Request 820 has two failure records (connect and
request-including-connect); these describe one failed request, not two outages.
The observation ends early, and its WebSocket terminal-state check is not
reached. The independent replay keeps this case failed despite the two valid
stopped samples.

The automatic-codec HE-AAC 48 kHz case and both subsequent HE-AACv2 cases pass.
The evidence does not show stale EOF metadata, a decoder crash or an allocation
failure. It also does not establish why the new TCP connection timed out.
The normal five-second connection timeout is retained; there are no retries
that could hide this failure.

## Heavy FLAC and continuity

The same 610-second FLAC fixture is observed for 180 seconds over HTTPS with
frequent WebUI polling. The server uses normal TCP backpressure for file
delivery. Its average encoded rate is 1,283.224 kbit/s. Both runs use the same
fixture bytes and delivery settings; their conditions are sequential.

| Measurement | Earlier PCM-tail candidate | Minimum-prefill candidate |
| --- | ---: | ---: |
| Mean CPU busy | 79.480% | 79.566% |
| Selected DMA queue-overrun count | 0 | 84 |
| Driver-write errors | 0 | 0 |
| Minimum sampled free heap | 57,796 B | 57,348 B |
| Minimum sampled largest free block | 34,816 B | 34,816 B |
| Median / minimum RSSI | -66 / -70 dBm | -67 / -70 dBm |
| Maximum WebUI response | 125 ms | 141 ms |

CPU, heap and selected DMA measurements exclude the first ten seconds.
RSSI and maximum WebUI response use the full playback observation.

CPU, decoder, queue and DMA telemetry cover the required windows. The
candidate's full observed DMA counter interval also records 84 overruns,
with no driver-write errors. Idle heap returns to the same two observations
as before playback: 133,128/133,140 bytes free, largest block 106,496 bytes,
17 tasks.

| Overrun group | Nearby decoder input timeouts | Maximum host socket write in overlapping delivery windows |
| --- | ---: | ---: |
| 2 | 2 | 47 ms |
| 37 | 22 | 406 ms |
| 45 | 24 | 547 ms |

In the two larger groups, decoded progress falls to approximately 4.6 and
4.5 seconds per five-second window. CPU utilization decreases during one of
these windows; the evidence does not indicate sustained CPU saturation.
Host write time includes receiver backpressure and scheduling. These periodic
records show an association with input starvation, not proof of a Wi-Fi,
Windows, TLS or profiling root cause.

The earlier and current configurations differ in both minimum prefill and
pipeline profiling. The earlier zero count is therefore a useful control,
not evidence that the 250 ms delay itself caused the regression.

With the permanent TLS reserve enabled, the input queue is held at its
minimum: four 2,060-byte packet slots, including headers and leases. Even
8,192 bytes of full payload represent only about 51 ms of this FLAC stream.
Waiting 250 ms before decoding does not create 250 ms of buffered audio.
Growing every codec's queue globally would consume the memory margin needed
by HE-AAC and must be tested separately.

## Memory, restoration and scope

No allocation, decoder, TLS, panic, watchdog, unexpected reset or serial-capture
failures were recorded. The WebUI connection timeout above remains a separate
client-transport failure. Across the entire
regression, including transitions, the minimum CPU-log free heap is 15,284 B
and the minimum sampled largest block is 4,608 B. The lowest reported
since-boot heap watermark is 7,852 B; it is not an instantaneous per-case
measurement. These values do not include an unmeasured safety guarantee.

All 33 independently replayed station changes pass. Settled idle heap after
the first and third cycles is 133,140 B, largest block 106,496 B, with 17 tasks.
The controller then restores `idf61-qio80-8c1f2d2d` by application-only OTA,
verifies unchanged Wi-Fi, playlist and settings, and records three successful
AAC 44.1 kHz stereo playback observations. No diagnostic image is left running.

The fresh clock readback confirms nominal 48,000 Hz and the startup flash
probe confirms QIO 80 MHz with four matching mapped application CRC reads.
This says nothing about analog background noise or absolute crystal accuracy.
Listening remains deferred because the user is unavailable to listen.

The [quiet candidate](ESP32C3_QUIET_MIN_PREFILL_BUILD_20261009.md) is saved and
build-audited separately. These diagnostic results do not qualify that image.
No production defaults are changed.

## Next checks

1. Recheck HE-AAC 48 kHz EOF with transport timing and serial capture, retaining
   this failed original observation. Include exact terminal checks on HTTPS.
2. Repeat the heavy-FLAC case on matched profiling builds, alternating the
   0 and 250 ms minimum, before attributing the result to startup policy.
3. If input-starvation events recur, compare HTTP/HTTPS and controlled record
   sizes; preserve socket-write timing, CPU, input waits and DMA counters.
4. Evaluate a larger input allowance for high-rate codecs only if necessary,
   with full AAC memory, allocation, station-switch and OTA regression.
5. Finish TLS closure/framing, certificate rejection and OTA checks on the
   selected image, including the previously unclassified OTA TLS errors.
6. Check the quiet build on public radio and
   complete the fractional-clock listening comparison when possible.

## Evidence

The [frozen archive](../tests/results/esp32c3-min-prefill-regression-20261009/)
contains 186 indexed files (7,640,991 bytes), including original observations,
per-request transport timing, 81 source snapshots, tiny tail fixtures,
public certificates, independent format/EOF/switch replay, and the earlier
FLAC control used for comparison. Existing build and ten-minute HE-AACv2
results remain in the [minimum-prefill report](ESP32C3_MIN_PREFILL_20261009.md).
The new run confirms four mapped flash CRC reads and nominal clock registers.

```powershell
python tests/results/esp32c3-min-prefill-regression-20261009/replay.py --output .build/replay-min-prefill-regression
```

Use a new output directory. Replay verifies frozen hashes and reproduces both
original verdicts and the adverse continuity finding without accessing the
board or network. Private settings and certificate keys are excluded.
