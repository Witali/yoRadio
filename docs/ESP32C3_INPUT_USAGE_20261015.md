# Measure encoded-input slot utilization

The [retained-owner growth experiment](ESP32C3_AAC_RETAIN_INPUT_20261015.md)
partially improved controlled AAC starvation but failed an allocation during
a TLS format change. Before consuming more RAM, measure how densely the
existing four slots store validated audio.

## Implementation and scope

The adaptive queue now supports publishing a nonempty prefix of an acquired
lease. `adaptive_input_commit_size()` rejects lengths above the requested
extent, zero lengths, foreign pointers and non-WRITING states. A rejected
commit keeps the lease available for correction or cancellation. FIFO,
ownership, reclamation and control-slot behavior are unchanged.

The audio producer publishes `sizeof(encoded_packet_t) + data_size` rather
than the full acquired capacity. This changes the reported item extent, not
encoded bytes, codec selection, DSP, buffer capacity or allocation policy.
The existing unsized commit API remains available to other queue clients.

Diagnostic `/api/native/health` input snapshots add:

- `ready`, `reading`, `writing`: data-slot counts by ownership state.
- `ready_bytes`: committed packet bytes waiting for the decoder.
- `reading_bytes`: full committed packet extents held by the decoder.

Counts exclude the independent control node. WRITING includes unpublished
confirmation candidates, whose data cannot yet be called playable audio.
Bytes include the packet header; READING does not subtract the decoder's
already-consumed prefix. These are queue-use measurements, not exact remaining
audio duration. No additional queue storage, packet buffer or heap allocation
is introduced; the stats return value has five additional scalar fields.

The host reader remains compatible with old snapshots. If any usage field is
present, all five are required and checked: state counts sum to occupancy,
byte counts fit the committed packet counts/capacity, and absent queues are
zero. Unknown fields are still filtered.

## Host evidence

- ASan/UBSan actual queue: 60,000 concurrent packets, alternating original and
  trimmed commits, FIFO/data integrity, pressure/reclamation, partial failures,
  control-slot independence and snapshot invariants. Dedicated cases verify
  exact received length, failed-commit correction and cancellation.
- Actual staging/router: four held candidate slots with concurrent consumer,
  128-byte control fragments, ordered MP3/AAC drains, cancellation and exact
  output bytes for 1/7/2048-byte input fragments.
- Actual send/finish path: 34 encoded AAC/MP3 cases at those fragment sizes,
  false signatures, maximum ADTS candidates, metadata, EOF, midstream recovery
  and cancellation; exact encoded-byte replay passes. This is not a PCM test.
- Health reader: 13 unit tests pass. A conservative full response bound is
  2,743 bytes including NUL, below the existing 2,816-byte workspace, including
  optional arena counters and all 16 maximum-width ISR events.

[Saved host evidence](../tests/results/esp32c3-input-usage-20261015/)
contains sources, reports and hashes. Physical measurement is pending.

## Physical measurement plan

Build the local-CA diagnostic with the original four-slot policy, one-second
prefill and AAC extra slots disabled. Repeat the same owned AAC-LC TLS pause
schedule. Quantify ready-packet utilization and unpublished/reading leases;
retain fault/output/recovery gates. Only then design bounded packing across
reads, preserving EOF, Stop, ordered codec changes and maximum-frame liveness.
Do not infer a small packet from the server's write size: ESP-IDF's HTTP reader
normally accumulates the requested read length before returning.
