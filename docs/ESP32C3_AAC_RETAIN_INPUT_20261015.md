# Retained SBR owner with bounded AAC input growth

## Experiment and acceptance plan

The [first input-growth trial](ESP32C3_AAC_INPUT_GROWTH_20261015.md) never grew
the LC queue because the unused pending SBR owner was freed before readiness
was checked. The [two-second startup wait](ESP32C3_AAC_PREFILL2_20261015.md)
also failed to improve output continuity. This experiment makes the existing
default-off growth policy retain the actual compact owner during LC playback.
No DSP, supported profile, precision or sampling-rate changes are involved.

1. Test pending-owner lifetime through LC, header changes, late SBR, failed
   reservation/open, Stop and destruction. Preserve the no-growth baseline.
2. Measure real resident input slots and heap on the board. Request four
   extra slots, retain the configured 32,744-byte SBR/PS owner, and keep the
   permanent 17,058-byte TLS RX reserve. Use one-second startup prefill.
3. Repeat the matched TLS pause schedule and require actual growth before
   interpreting continuity improvement. Retain all failed controls.
4. If beneficial, qualify late SBR/PS, large AAC frames, same-connection
   profile/rate/channel and codec changes, other codecs, Stop/EOF/replacement,
   TLS/WebUI/OTA and settled recovery on a final quiet image.

## Memory policy

`AAC_INPUT_EXTRA_SLOTS=0` preserves LC's existing release behavior. When
nonzero, an unused pending owner survives successful LC PCM and LC header
changes. It transfers to the decoder when SBR requests its owner and is freed
on destruction. Failed-open fallback still discards it to preserve viable LC
playback; growth remains unavailable until an owner is subsequently acquired.
Readiness is now reconsidered after later successful output, rather than only
the first frame. The producer still attempts growth only once per connection.

The configured advisory AAC headroom defaults to 32 KiB, with an experimental
range of 16–64 KiB. The first physical trial uses 16 KiB, because the retained
owner itself consumes about 32 KiB before packets are added. Each additional
slot requests 2,060 bytes on this build; four request 8,240 bytes plus allocator
overhead. Combined additional live storage can therefore be about 41 KiB.
FLAC retains its separate 32-KiB policy. Neither free-heap threshold is a
contiguous reservation or an acceptance criterion in place of real failures.

Queued or leased packets cannot be reclaimed to satisfy a future allocation.
The owner protects the largest SBR/PS block, not all future allocations: frame
growth, control structures, codec reopen and concurrent networking remain
physical acceptance requirements. Active SBR owners are released on codec
close; acquiring a fresh owner after a profile change still needs testing.
Production growth remains disabled. No production memory-safety claim yet.

## Host evidence

ASan/UBSan checks pass for the actual owner wrapper and native adapter with
growth disabled/enabled: reservation failure, retry after failed open, output
buffer retry, LC release/retention, unchanged pending pointer across LC header
changes, transfer to late SBR, active-owner reopen, scoped allocation failures
and complete destruction. DSP is mocked.

Nine actual TLS/input-allocator variants pass, including independent FLAC/AAC
policies and combined growth with 16/32/64-KiB AAC headroom. Each performs
8,000 concurrent TLS allocations. Tests check per-slot headroom, partial OOM,
live static TLS storage, FIFO/lease ownership through shrink and reconnection,
saved queue-target limits and complete release.

[Owner tests](../tests/results/esp32c3-aac-retain-input-20261015/host-owner/)
and [allocator tests](../tests/results/esp32c3-aac-retain-input-20261015/host-tls/)
are retained.

## Physical result: growth works, candidate not accepted

Image `idf61-aacret-20261015`, source `36e02e5d`, app SHA-256
`8fb627555b1eeb412fcdcefe8c9c9ea81b956e627803c0ba0547ba2bc8f3c6b7`
passes linked AAC/HTTP/allocator and ISR/timer audits. Compared with the local-CA
baseline, configuration differs only by four extra AAC slots and the new
16,384-byte headroom setting. Startup prefill stays at one second. Static BSS
increases by eight bytes; the substantial owner/packet cost is dynamic.

### Controlled delivery pauses

The queue actually grows from four to eight resident slots. With the same
owned AAC-LC fixture, pacing, byte offsets, host send buffer and TLS cipher,
the longest pause produces 33 completion-queue drops, versus 48 on the control.
This is a partial improvement in this single matched experiment, not a pass or
an analog measurement. The shorter pauses produce no new drops.

| Measurement | Four-slot control | Retained owner + eight slots |
| --- | ---: | ---: |
| Actual longest host pause | 1.510316 s | 1.513596 s |
| Completion drops / write errors | 48 / 0 | 33 / 0 |
| Allocation / decoder / watchdog faults | 0 / 0 / 0 | 0 / 0 / 0 |
| Minimum sampled free heap / largest block | 59,152 / 32,768 B | 17,692 / 4,608 B |
| Settled free-heap median before / after Stop | 138,928 / 138,932 B | 138,920 / 138,948 B |
| Passed checks | 10 / 11 | 10 / 11 |

The new run retains 105 health samples on one boot; the final status is at
89.258 seconds of a 90-second observation. Its settled largest block stays
110,592 B and task count stays at 16. Retained all-wait events have recent
output checkpoints (0.106–8.775 ms) but stale PCM/input/network checkpoints.

### TLS format changes expose a real allocation failure

All four sequences reach their expected formats and EOF, with no sampled
active-output increments or decoder/watchdog failures. However, `changing`
(LC 44.1 → LC 48 → HE 48 → HEv2 44.1 kHz) records **one failed 1,630-byte
allocation with capability mask 2060** (`INTERNAL | DMA | 8BIT`). The report
retains this failure even though playback proceeds. Its caller is not captured;
do not identify it as Wi-Fi or a decoder allocation solely from its size.

| Sequence | Original result | New allocation failures | Decoder failures |
| --- | --- | ---: | ---: |
| changing | FAIL | 1 | 0 |
| implicit-sbr | PASS | 0 | 0 |
| mp3-he-mp3 | PASS | 0 | 0 |
| aac-mp3-hev2 | PASS | 0 | 0 |

All four share one boot. The allocation counter remains at one in the later
cases; those passes do not erase it. Independent replay checks every saved
decoder-health counter and separately verifies formats, EOF and output deltas.
The campaign reaches a lifetime minimum free heap of 7,152 B. Low free memory
itself is not the rejection reason; the actual failed allocation is.

The same `changing` fixture and TLS cipher are then replayed on the unchanged
four-slot local-CA control image. It **passes**, with no allocation, decoder,
watchdog or measured output faults. Its minimum sampled heap/largest block are
29,996 / 14,336 B, and lifetime minimum heap is 20,432 B. This supports rejecting
the new memory policy, while one A/B observation cannot identify the precise
allocation caller or distinguish total pressure from transient fragmentation.

All three deployment controllers restore the original production image and
verify unchanged Wi-Fi, playlist and settings, with playback stopped. Lab
certificates and diagnostic instrumentation do not qualify production timing.

[Build](../tests/results/esp32c3-aac-retain-input-20261015/build/),
[pause run](../tests/results/esp32c3-aac-retain-input-20261015/physical/),
[four transitions](../tests/results/esp32c3-aac-retain-input-20261015/transitions/)
and [matched transition control](../tests/results/esp32c3-aac-retain-input-20261015/baseline-changing/)
are preserved. Production growth remains disabled.

## Next investigation

Measure actual queued payload bytes and packet-size distribution before adding
more slots. Occupied-slot counts include unpublished candidate/producer leases
and do not measure playable audio. The HTTP client normally fills the requested
read length, while the frame router flushes its partial output at every
`send_stream_audio()` return. Therefore 1-KiB server writes alone do not prove
half-full queue slots. Confirm their utilization before changing batching.

Investigate packing validated same-codec bytes into existing slots across reads
with bounded latency, prompt EOF/cancellation, ordered codec drains and no
deadlock when the confirmation window holds four leases. This may improve
usable buffering without the roughly 41-KiB combined cost of this experiment;
its benefit is currently a hypothesis. Preserve full AAC frame/profile support
and verify the 8,191-byte candidate and low-bitrate cases before deployment.
