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
are retained. Physical results are pending.
