# ESP32-C3 FLAC input capacity experiment — 2026-10-09

## Design and scope

`CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS` is an experimental integer option,
**disabled by default (`0`)**. It extends the adaptive compressed-input queue
only for the custom FLAC decoder, after the current stream has produced PCM.
The decoder's channel workspace and encoded-frame window are allocated while
parsing STREAMINFO, before that signal. The producer makes one bounded growth
attempt per stream generation. Failed or terminal first-frame feeds do not
request expansion.

The tested value `4` changes the usual queue from four to eight 2,060-byte
slots: **8,240 additional bytes**, plus allocation overhead. The configured
user target is still an upper bound. Each allocation checks for 32 KiB of
nominal remaining internal heap; this is advisory headroom, not a reservation
or a guarantee against fragmentation or concurrent allocations. Partial
expansion is safe. The dedicated **17,058-byte TLS RX reserve is unchanged**.

Cleanup lowers the queue limit. Idle slots are freed immediately, while
WRITING, READY and READING slots retain their data until the consumer returns
them. The following connection starts with the minimum limit. A successful
allocation in flight is discarded if the limit was lowered before publication.
Neither AAC nor the other codecs requests FLAC expansion.

Implementation commit: `bfcd15f7` (`Add bounded FLAC input growth experiment`).
See the reproducible host commands in [the testing guide](ESP32C3_TESTING.md#experimental-flac-input-capacity-after-decoder-initialization).

## Matched firmware and host validation

Both images use pinned ESP-IDF `9a97f6c54ec638111ce55cd36581b3c192f15207`,
full compact AAC/SBR/PS, TLS RX reserve, adaptive input, 250/500 ms prefill,
QIO 80 MHz and the experimental fractional nominal 48 kHz clock. Their only
SDK configuration difference is extra input slots `0` versus `4`. Their
firmware source snapshots are identical. The unrelated CLZ experiment is
not compiled into either image.

| Property | Extra slots 0 | Extra slots 4 |
| --- | ---: | ---: |
| Application bytes | 1,621,952 | 1,622,736 |
| IRAM text bytes | 47,690 | 47,690 |
| Initialized DRAM bytes | 12,856 | 12,856 |
| BSS bytes | 45,664 | 45,672 |
| Input storage after successful expansion | 8,240 | 16,480 |

The linked AAC, HTTP/TLS and allocator audits pass for both images. All 128
text/constant sections compared across 18 FLAC/AAC objects are byte-identical
before link relocation. This checks unchanged codec code, not physical PCM
capture or analog quality.

Host validation passes with AddressSanitizer and UndefinedBehaviorSanitizer:

- Queue ownership, allocation races/faults, deferred retirement and 30,000
  concurrently produced/consumed packets with changing limits and reclamation.
- Five TLS allocator variants, including enabled FLAC growth; 8,000 concurrent
  allocations per variant, zeroing, fallback, exhausted heap and intact reserve.
- 42 stream-task cases with growth enabled and 37 with it disabled, plus 37
  using the alternative retained-RX TLS configuration, including
  actual HTTP disposal, stale-generation rejection and AAC exclusion.
- 88 startup-prefill cases across ring/adaptive input and minimum delays.

The first stream-harness compilation exposed missing stubs for the existing
TLS profiling callbacks. The harness now includes the real disabled-profile
header; the failed compilation and subsequent successful runs are retained.

Images and exact metadata:

- [Extra slots 0](../firmware/development/esp32c3-idf-6.1-r9a97-flac-input0/manifest.json),
  app SHA-256 `c80d24f53a8304db598a5c189847dbe9f24414b50f024d9e5b3694490a67de6b`.
- [Extra slots 4](../firmware/development/esp32c3-idf-6.1-r9a97-flac-input4/manifest.json),
  app SHA-256 `7067791397ce68d0578d819731d1212a17c5760a9c3be08c8980bf3e85cc5abc`.

These are laboratory images containing the local test CA and profiling.
The fractional clock remains unqualified for analog quality; the user cannot
listen at present. Production defaults are unchanged.

## Physical results

The same heavy 48 kHz stereo 16-bit FLAC fixture ran over trusted HTTPS for
180 seconds under repeated WebUI requests, in order **0 → 4 → 0**. The server
used unpaced finite-file delivery and pacing ratio 1.0. CPU is informational;
no CPU ceiling was used to reject a run. The table's CPU and queue waits use
complete measured windows after the existing ten-second warmup.

| Measurement | Control before, 4 slots | Candidate, 8 slots | Control after, 4 slots |
| --- | ---: | ---: | ---: |
| Mean CPU busy | 78.94% | 79.23% | 79.65% |
| Decoder input-wait wall time | 25.18% | 0.16% | 24.69% |
| Decoder input timeouts | 56 | 5 | 20 |
| Output empty-PCM wait wall time | 12.02% | 0.086% | 11.58% |
| DMA completion-queue events, measured windows | 77 | 7 | 11 |
| DMA completion-queue events, whole observed run | 82 | 24 | 12 |
| DMA write errors | 0 | 0 | 0 |
| Minimum free heap in CPU samples, bytes | 57,624 | 48,596 | 57,592 |
| Minimum largest free block, bytes | 34,816 | 34,816 | 32,768 |
| Median RSSI, dBm | -67 | -67 | -67 |
| Settled heap recovery after Stop | PASS | PASS | PASS |
| Original report entries | 3/4 PASS | 4/4 PASS | 4/4 PASS |

Independent paired network/heap samples observe a slightly lower candidate
minimum of **48,444 bytes**; the table deliberately retains the CPU-sample
metric used by the original gate. Full CPU/decoder/flow telemetry coverage is
available for all three runs. Queue waits are elapsed wall time, including
preemption, not CPU utilization.

The candidate demonstrably expands to eight slots and almost eliminates
waiting for compressed input in this fixture. However, the second control
has fewer **whole-run** DMA events than the candidate. The control variation
82 → 12 prevents a claim of reliably improved continuity. The candidate's 24
events occur in two early sampled intervals (17 and 7); the seven events
inside measured windows remain failures of a zero-event continuity target.
These counters are not a count of acoustically confirmed gaps.

The first control fails the original progressive-heap gate: first/last
measured medians are 60,704/57,672 bytes. After Stop, free heap returns to
132,996 bytes, compared with baseline samples 132,992 and 132,960; largest
block and task count also recover. Paired free-heap/TCP-credit correlation is
-0.947. That supports receive-buffer occupancy as a possible contributor,
but is not allocation-ownership proof and does not erase the failed gate.

**Decision: retain the experiment with default `0`.** The reduction in input
and empty-PCM waiting is useful, but a repeatable continuity improvement has
not yet been established. The existing decoder precision and full AAC format
support are preserved. Further paired, at-most-ten-minute tests should
separate startup effects and controlled network jitter before promotion.

### Switching, TLS recovery and restoration

All nine seven-second playback observations across three cycles of FLAC,
HE-AAC 48 kHz stereo and HE-AACv2 44.1 kHz stereo pass full-format checks.
Expansion occurs only in the three FLAC generations. However, the combined
switching/heap test **fails**: the settled largest free block drops from
98,304 to 90,112 bytes. Free heap recovers from a first-cycle median of
132,796 to 132,944 bytes, with the same 17 tasks. This is fragmentation
evidence, not proof of a leak or proof that this option caused it. A matched
switching control with expansion disabled is still needed.

Four exact HTTPS EOF cases pass: FLAC and HE-AACv2, each with automatic and
explicit codec selection. REST replay confirms stopped state, `stream ended`
and cleared PCM fields; the original WebSocket checks also pass. There are
five report entries including cleanup.

The subsequent 75-second full HE-AACv2 HTTPS run grows from small to full
16,384-byte plaintext TLS records after playback starts. All five original
entries pass, with zero observed DMA events and write errors. Weighted
steady-state CPU is 59.38%; minimum free heap is 25,900 bytes. **The largest
free block is only 5,632 bytes.** No additional input slots are requested by
AAC. The static TLS reserve permits large records without requiring another
contiguous 17 KiB heap allocation, but this small remaining block is a reason
to investigate fragmentation, not a production-stability claim. Idle largest
block remains 86,016 bytes before/after this phase; free heap changes from a
median of 132,964 to 132,760 bytes and passes its recovery tolerance.

Overall: **22/24 original report entries pass**. Both failed memory gates
remain failed. No decoder, allocation, TLS, panic, watchdog, capture or
unexpected-reset fault is recorded within the six test phases; no traced
board HTTP request fails. Host tests, playback success and original report
counts do not override the nonzero FLAC DMA observations.

The outer controller restores the saved quiet production application
(`21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a`),
verifies Wi-Fi, playlist and settings unchanged, and observes restored
playback three times. Four experimental installations are independently
checked against the application identity, QIO 80 MHz register readback,
four mapped-flash CRC passes each and the fractional-clock registers.
These successful application OTA operations do not replace the full negative
OTA-upload suite for the new candidate.

## Evidence and next checks

[Frozen original reports and replay](../tests/results/esp32c3-flac-input-growth-20261009/index.json)
include both failed gates, raw filtered counters, transport timing, exact
firmware configuration, source snapshots and host failures/successes. Private
settings and TLS private keys are excluded. Replay without touching a board:

```powershell
python tests/results/esp32c3-flac-input-growth-20261009/replay.py --output .build/flac-input-growth-replay-new
```

Next: repeat the same FLAC/AAC switching sequence with extra slots disabled,
compare fragmentation before changing allocation policy, and use controlled
jitter plus paired runs of at most ten minutes to test continuity. Keep the
option off by default until those checks and candidate OTA regression pass.
Analog clock qualification still requires a later listening or capture test.
