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

## Further hardware qualification

Keep the feature off by default. Check the complete finite-file matrix and
quiet public HTTPS playback before considering it for production. More densely
filled slots do not eliminate the measured long-gap starvation or explain the
earlier public-station and WebUI TCP failures. Preserve those open findings;
do not widen output acceptance merely because memory and transition gates pass.
