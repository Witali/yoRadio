# Bounded AAC input-capacity experiment

## Purpose and status

The [controlled TLS pause](ESP32C3_AAC_TLS_PAUSES_20261015.md) exhausted buffered
audio at 1.51 seconds with four resident input slots. Output-task checkpoints
remained recent. This experiment adds capacity after native AAC initialization,
without changing DSP, sampling rates, DMA scheduling or the TLS RX reservation.
It is implemented and host-tested; physical benefit and all-codec safety are
not yet established. Production defaults remain unchanged.

`CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS` accepts 0–8, default **0**. The planned
first trial requests four extra slots, capped by the user's saved target.
At the observed packet capacity of 2,060 bytes, four resident slots add
8,240 requested heap bytes, plus allocator overhead. Measure actual resident
count and heap use; a requested extra count does not prove allocation.

## Ownership and memory conditions

- Only the stream task restores slots, once per connection after successful
  native AAC output. FLAC and AAC share the existing bounded expansion helper.
- The decoder signals readiness only if the configured compact SBR/PS owner is
  allocated or reserved and no scoped allocation failure was recorded. The
  AAC-LC low-memory fallback may discard that reservation; it does not signal
  readiness. No decoder pointer is transferred to another task.
- Before each extra allocation, leave 32 KiB of advisory internal-heap
  headroom. This is not a reservation or a guarantee against concurrent or
  later allocations. The 17,058-byte TLS RX reserve remains intact.
- Existing adaptive-queue limits, allocation-pressure reclamation and lease
  rules apply. Only idle slots are reclaimed. Stop/EOF/next-connection cleanup
  lowers the limit, and busy extra slots retire when their leases end.
- Both FLAC and AAC still obey the saved user buffer target. No NVS settings
  change and no new full-frame buffer or codec data structure is introduced.

The owner check protects the largest pre-reserved AAC block; it does not prove
that every later allocation succeeds. Same-connection rate/channel/profile
changes, late SBR/PS, reopening and codec-family transitions remain mandatory
physical tests before enabling the option by default.

## Host evidence

Seven ASan/UBSan allocator variants pass: four original configurations,
FLAC expansion only, AAC expansion only, and both. Each variant performs
8,000 concurrent TLS allocations. Growth variants cover low headroom, partial
allocation failure, headroom changes between allocations, a live TLS reservation,
producer/consumer leases across shrink and preparation, retained floor buffers,
FIFO data integrity, complete release and target-capacity clamping.

The actual adaptive queue also passes 60,000 concurrent packet transfers,
ownership/FIFO checks, deferred-limit changes, allocation races/faults,
TLS pressure, tick wrap and separate control-slot storage.

[Retained sources, logs and reports](../tests/results/esp32c3-aac-input-growth-20261015/host/)
use pthread/heap stubs. They do not qualify target scheduling or actual TLS/PCM.

## Physical acceptance still required

1. Build/audit the local-CA diagnostic image with four requested extra slots.
2. Repeat the exact 0.5/1.0/1.5-second TLS pause schedule, source, host buffer
   and cipher; compare resident slots, heap and output/phase counters.
3. Run full-rate AAC-LC/HE-AAC/HE-AACv2, late SBR/PS and same-connection
   codec/rate/channel transitions; verify all allocations and settled recovery.
4. Check other codecs, Stop/replacement/EOF, TLS pressure and OTA on the final
   quiet candidate. Retain failed controls and do not infer public-stream
   causality merely from a passing local pause experiment.
