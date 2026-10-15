# Reuse partial queued input tails

The [physical utilization measurement](ESP32C3_INPUT_USAGE_20261015.md) found
two READY slots only 56.87% full at the median sampled instant. This experiment
packs additional validated bytes into the existing partial FIFO tail instead
of allocating more slots or withholding an output lease across network reads.

## Ownership and ordering

`CONFIG_YORADIO_INPUT_TAIL_COALESCE` is experimental and defaults to **off**.
It depends on the frame router; no codec or sample-rate support is removed.

The single producer can reopen a partial READY data tail only when another
queued node precedes it. Under the existing queue lock, the tail is removed
from the FIFO and becomes a WRITING lease. The consumer can therefore never
read it while it is being extended. The producer copies outside the lock,
then republishes the tail before returning from the current send call.
The sole queued packet, full packets, READING leases and the independent
control tail cannot be reopened. The queue adds no fields or heap storage.

The router appends only to a nonempty AUDIO_CONTINUE packet with matching
generation and codec and a valid committed extent. EOF, drain and family or
generation changes remain ordering barriers. Rejected candidates are
immediately republished with their original extent. Cancelling a reopened
lease restores its original data length and republishes its valid prefix;
newly appended bytes do not become visible. All existing flushes at read ends,
control-storage changes and staging pressure remain in place. There is no
new network wait or delayed-publication timer.

## Host verification

- Actual queue/router, ASan/UBSan: 600,000 exact ordered bytes with concurrent
  consumer; 31,381 successful tail reopens in the recorded run. Deterministic
  checks cover control/full/sole-tail exclusions, drained predecessors,
  consumer ownership, codec/generation/EOF/drain barriers and prefix restoration.
- Existing queue/TLS-pressure suite: 60,000 concurrent packets; ownership,
  reclamation, deferred limits, tick wrap and allocation-failure paths pass.
- Actual send/finish path: the 34-case encoded AAC/MP3 corpus passes with the
  feature off, on with immediate consumption, and on with queued consumption.
  Each tests chunks of 1, 7 and 2,048 bytes, maximum ADTS candidates, false
  headers, metadata, exact replay, format changes, EOF and cancellation.
- Four-slot staging pressure with independent 128-byte control storage and
  concurrent cancellation passes with the feature enabled.

[Saved host evidence](../tests/results/esp32c3-input-tail-20261015/) includes
reports, source snapshots and hashes. Encoded-byte equality does not by itself
qualify physical playback, CPU timing or TLS memory pressure.

## Physical TLS pause comparison

The linked diagnostic image `idf61-intail-20261015` was built from `24f61ec`.
App SHA-256: `f9a375c8aeabd9d4c3d1657d71260e05326321d6d1ecaad5267f8601c68e15e6`.
The configuration audit finds only `CONFIG_YORADIO_INPUT_TAIL_COALESCE=n→y`
relative to the local-CA baseline (normalizing the absent option to `n`).
Disassembly confirms `stream_route_emit` calls `adaptive_input_reopen_tail`.
Static IRAM/DRAM sections are unchanged; flash code grows by 68 bytes relative
to the input-utilization image. The queue allocates no additional packet.

The same owned AAC-LC fixture, TLS cipher, byte offsets and requested pause
schedule were used. Both observations last 90 seconds, each with 68 sustained
samples. No DSP algorithm changed.

| Measurement | Utilization control | Tail coalescing |
| --- | ---: | ---: |
| Resident data slots | 4 | 4 |
| Median nonempty READY slot fill | 56.87% | 100% |
| Sample-weighted READY slot fill | 70.61% | 97.91% |
| Median committed READY bytes | 2,337 | 4,120 |
| Median unused nonempty READY capacity | 1,777 B | 0 B |
| Median READING full-lease fill | 96.92% | 100% |
| Actual longest host pause | 1.5014 s | 1.5144 s |
| Completion drops / write errors | 47 / 0 | 45 / 0 |
| Allocation / decoder / watchdog faults | 0 / 0 / 0 | 0 / 0 / 0 |
| Minimum sampled heap / largest block | 59,028 / 32,768 B | 59,168 / 32,768 B |
| Settled heap before / after Stop | 138,924 / 138,956 B | 138,928 / 138,924 B |
| Campaign verdict | 10/11, output FAIL | 10/11, output FAIL |

This confirms more usable queued data, **not** elimination of starvation.
The 45 versus 47 completion events in single runs are not a demonstrated
continuity improvement. Only the longest imposed pause overlaps new output
increments; the shorter actual pauses are 0.5004 and 1.0059 seconds.
Retained all-wait events show output checkpoints 0.332–6.331 ms old but PCM,
encoded and HTTP progress hundreds of milliseconds old.

READY=2 / READING=1 / WRITING=1 appears in 67 of 68 samples; one near the long
pause has only one READY packet containing 50 committed bytes. Extents include
12-byte packet headers, and READING is not its remaining unconsumed suffix.
These are sampled occupancies, not a distribution of every packet. The median
READY increase of 1,783 bytes is within existing allocated RAM, not a reduction
of heap use or an exact increment of buffered audio duration.

The controller verified restored original production image, unchanged
Wi-Fi/playlist/settings and stopped playback. The
[physical archive](../tests/results/esp32c3-input-tail-20261015/physical/)
preserves both the failure and independent usage/output analysis.

## TLS format transitions

The same candidate then passes **4/4** transition sequences on one boot:

| Sequence | Format and EOF | Output drops / write errors | Allocation / watchdog faults | Min sampled heap / largest block |
| --- | --- | ---: | ---: | ---: |
| LC 44.1 → LC 48 → HE 48 → HEv2 44.1 kHz | PASS | 0 / 0 | 0 / 0 | 29,984 / 17,408 B |
| Implicit SBR: LC 22.05 mono → HEv2 44.1 → LC 48 kHz | PASS | 0 / 0 | 0 / 0 | 28,572 / 15,360 B |
| MP3 → HE-AAC → MP3 | PASS | 0 / 0 | 0 / 0 | 26,392 / 13,824 B |
| AAC → MP3 → HE-AAC v2 | PASS | 0 / 0 | 0 / 0 | 34,928 / 21,504 B |

Independent replay checks all 268 saved boundary/active health rows for decoder
faults, boot continuity, expected formats, EOF and output increments. Resident
slots remain four. Lifetime minimum free heap reaches 18,132 bytes; no allocation
failure is recorded. Each fixture body is delivered completely using TLS 1.2
ECDHE-RSA-AES256-GCM-SHA384. This includes the transition that failed with the
earlier eight-slot retained-owner experiment. The runner restores the original
production image and verifies unchanged settings and stopped playback again.

[Transition evidence](../tests/results/esp32c3-input-tail-20261015/transitions/)
retains original reports, fixture hashes, source references and independent audit.
These are format/transport/output-counter checks, not PCM capture or an analog
continuity measurement.

## Quiet finite-file qualification

The public-root-only, non-ISR-diagnostic candidate `idf61-tailq-20261015` is
saved under `firmware/development/esp32c3-idf61-input-tail-quiet/`.
App SHA-256: `0edeb859478dc22894e0f369bd62756b7b15a0c5dbf62d78a2d9594789444547`.
Firmware source is `595a4dc3`; the strengthened file runner is `0a35e7c0`.
Configuration differs from the previous quiet confirmation image only by the
tail-coalescing flag, normalizing the previously absent extra-AAC option to
zero. The local CA and pipeline recorder are absent; public certificate
verification, all AAC profiles and existing TLS reserve are retained.

The finite HTTP matrix passes **28/28 checks**: 22 file/hint cases plus idle,
recovery, settings and lifetime-health checks. MP3, FLAC, Vorbis, Opus, AAC-LC
at 22.05/44.1/48 kHz, HE-AAC at 44.1/48 kHz and HE-AAC v2 at 44.1 kHz pass
both AUTO and explicit codec selection (including the separate high-bitrate
AAC-LC fixture).

The runner now rejects new completion-queue drops/write errors in paired
steady file observations. Independent replay verifies all 22 windows, each
5.462–6.741 seconds, with zero increments. Startup and the separate EOF idle
window are excluded. This additional gate was not part of the earlier 28/28
file result; it does not convert that older report into equivalent coverage.
Seven file-gate regressions, 13 health tests and five sustained-output tests
pass. Complete fixture delivery, expected decoded formats, natural EOF and
pre-cleanup EOF memory recovery pass for all 22 files.

All 680 health observations retain one boot, zero allocation/decoder/watchdog
faults, minimum sampled heap 28,708 B and largest block 13,312 B. Settled heap
changes from 139,472 to 139,520 B; largest block stays 110,592 B and task count
stays 16. No traced HTTP request fails. The controller restores the original
production image and verifies unchanged settings and stopped playback.

[Quiet build and file evidence](../tests/results/esp32c3-input-tail-quiet-20261015/)
contains raw reports, independent replay, request timings, source references
and hashes. The finite windows do not establish ten-minute public HTTPS
stability or full PCM/acoustic continuity.

## Quiet public AAC HTTPS, ten minutes

The **same quiet image** then passes **7/7** checks on `groovesalad-128-aac`
over HTTPS with normal certificate verification. The independent source probe
confirms AAC-LC 44.1-kHz stereo. The final playback sample is at 599.819 s;
the exact saved steady window contains 1,074 paired observations over 584.579 s,
with **zero new completion-queue drops and zero write errors**. Independent
replay reproduces every saved format/response/memory/decoder/output verdict
using the original start/end boundaries, rather than shifting the window.

| Measurement | Result |
| --- | ---: |
| All health observations / boots | 1,123 / 1 |
| Allocation / decoder / watchdog faults | 0 / 0 / 0 |
| First matching decoded format | 3.348 s |
| Maximum combined status/health request | 471.98 ms |
| Failed traced HTTP request phases | 0 |
| Minimum sampled free heap / largest block | 58,384 / 32,768 B |
| Settled heap before / after Stop | 139,476 / 139,392 B |
| Settled largest block / task count, both endpoints | 106,496 B / 16 |
| RSSI min / median / max | -73 / -65 / -53 dBm |

Stopped-state recovery passes. The controller restores the original production
image, verifies unchanged Wi-Fi/playlist/settings and leaves playback stopped.
[Saved public evidence](../tests/results/esp32c3-input-tail-quiet-20261015/public-radio/)
includes raw reports, transport timings, exact-window replay and source hashes.
No broadcast audio is archived.

The earlier quiet image recorded 36 completion drops on this station, whereas
this run records none. Live content and network conditions differ between
runs: this is a successful observation, not a controlled causal demonstration
that tail packing alone eliminated the original fault. The imposed 1.5-second
TLS-pause failure remains recorded separately, and this does not resolve the
earlier FLAC/WebUI TCP timeout or prove acoustic continuity outside the window.

## Further hardware qualification

Keep the feature off by default until public HTTPS files, quiet transitions,
network recovery and OTA regression are checked on this image. More densely
filled slots do not eliminate the measured long-gap starvation or explain the
earlier WebUI TCP failures. Preserve those open findings; do not widen output
acceptance merely because memory and transition gates pass.

## Quiet public HTTPS files

The exact quiet image completed both AUTO and explicit FLAC, Opus and Vorbis
files from independently decoded public HTTPS references. The original runner
reports **14/16**, with both FLAC cases rejected by `Progressive heap loss`.
These failures are retained in the
[original HTTPS evidence](../tests/results/esp32c3-input-tail-quiet-20261015/public-files/).

Independent inspection of the two FLAC cases finds expected format, natural EOF
at 60.793 / 60.797 seconds versus a 60.480-second reference, and zero new output
completion drops/write errors over 56.289 / 56.099 seconds. WebUI responses stay
below 412 ms. The original three-sample endpoint medians fall by 8,592 / 8,508 B,
but five-second buckets repeatedly revisit approximately the same 61–71 KB
heap range throughout playback. This is evidence of endpoint phase sensitivity,
not proof of a continuing leak or of its allocator source. Largest-block
endpoint medians are 49,152→49,152 and 53,248→49,152 B.

All 865 health samples retain one boot and zero allocation, decoder and watchdog
faults. Opus/Vorbis pass their existing format/duration/EOF, memory and output
checks. All three codec recovery checkpoints pass. After FLAC, settled free
heap is 139,520 B versus 139,484 B initially, with the largest block unchanged
at 110,592 B. No failed TCP connect was recorded in this campaign. The controller
restored the original production application, verified settings and stopped
playback. The earlier TCP timeout remains historical evidence; its cause has
not been identified by this successful transport observation.

### Memory-check correction and independent replay

The shared check now compares the first/last contiguous thirds, retaining the
same 2,048/4,096-byte tolerances and a separate late-fall check below the initial
range. The old three-sample endpoint loss remains visible. Seven trend tests
cover phase aliasing, slopes, loss superimposed on recurring allocations, abrupt
late loss and fragmentation, including losses injected into both real FLAC
recordings. The existing sustained-output, public-file, health and quiet gate
tests also pass; no firmware or decoder code changed.

The [separate retrospective review](../tests/results/esp32c3-input-tail-quiet-20261015/memory-review/review.json)
keeps hashes and original case results. All six files pass independent format,
memory, decoder, output and natural-EOF recovery checks on the original time
boundaries. FLAC median heap loss over thirds is +324 / -236 B and largest-block
loss is zero in both cases. Each original FLAC failure remains in the original
14/16 report. This resolves the observed endpoint-comparison false alarm; it
does not prove allocation ownership or exclude slower leaks. A fresh hardware
run with the revised runner, quiet network/transition and OTA checks remain due.
