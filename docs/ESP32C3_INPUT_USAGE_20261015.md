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
contains sources, reports and hashes.

## Physical result

The diagnostic image `idf61-inuse-20261015`, built from `5f1efbc1`, passed
build/link/IRAM audits and ran the same 90-second AAC-LC TLS pause schedule.
Normalized configuration comparison against the four-slot local-CA control
found no differences. AAC extra slots stay disabled, prefill stays one second,
and the TLS receive reserve stays 17,058 bytes. No PCM algorithm changed.

App SHA-256: `9a3f23ec215b4a8e477cc923f4afec940d44a347795f8bb739c4ba4d4d551eea`.

| Measurement | Result |
| --- | ---: |
| Campaign checks | 10 PASS / 1 FAIL |
| Sustained usage samples / observed interval | 68 / 73.975 s |
| Resident / minimum / limit | 4 / 4 / 4 |
| READY=2, READING=1, WRITING=1 | 67 samples |
| READY=0, READING=1, WRITING=1 | 1 sample |
| Nonempty READY slot fill, min / median / max | 50.0% / 56.87% / 99.13% |
| Sample-weighted READY slot fill | 70.61% |
| Unused capacity in nonempty READY slots, median / max | 1,777 / 2,060 B |
| Committed READY bytes, median including empty sample | 2,337 B |
| Completion drops / write errors | 47 / 0 |
| Allocation / decoder / watchdog faults | 0 / 0 / 0 |
| Minimum sampled heap / largest block | 59,028 / 32,768 B |
| Settled free heap before / after Stop | 138,924 / 138,956 B |
| Settled largest block / tasks, before and after | 110,592 B / 16 |

Fill is calculated as `ready_bytes / (ready * packet_capacity)`, only when
READY is nonzero. Packet capacity is 2,060 bytes. Committed extents include the
12-byte packet header (confirmed from target ELF DWARF). These are sampled
occupancies, not a count-weighted distribution of every packet or a precise
measurement of audio duration. READING includes its consumed prefix; WRITING
is unpublished and is excluded from playable bytes. The unused READY capacity
is already allocated RAM, not a free-heap gain.

Actual host pauses were 0.5005, 1.0119 and 1.5014 seconds. Only the longest
pause overlaps new completion drops. READY is empty at 66.430 s; 47 drops
appear between that sample and 67.536 s. The retained all-wait ISR events show
output checkpoints only 0.009–7.678 ms old, but PCM, encoded and HTTP progress
hundreds of milliseconds old. This supports starvation in this imposed-gap
experiment; it does not prove the cause of the earlier public-station failure
or establish analog continuity. The difference from the control's 48 drops
is not evidence of an improvement from telemetry.

The controller restored the original `idf61-prod-20261013` image, verified
Wi-Fi/playlist/settings equality, and left playback stopped. Raw failures,
queue observations, replay scripts and hashes are in the
[physical archive](../tests/results/esp32c3-input-usage-20261015/physical/).
This laboratory image is not production-qualified.

## Next experiment

Partial READY packets are now demonstrated. Test bounded coalescing of validated
bytes across reads, using the existing slots. Retaining a partial producer
lease can itself reduce READY capacity, so success must be measured as usable
queued data and output continuity, not merely fuller individual packets.
Flush before the staging window needs its fourth slot, before ordered codec
drains, at EOF and at a bounded latency; cancel leases on Stop and failures.
Verify maximum ADTS frames, low bitrates, fragmented reads, metadata, format
changes and cancellation before replaying this hardware schedule. Do not
enable a new memory policy on the basis of the fill measurement alone.

### Original measurement plan

Build the local-CA diagnostic with the original four-slot policy, one-second
prefill and AAC extra slots disabled. Repeat the same owned AAC-LC TLS pause
schedule. Quantify ready-packet utilization and unpublished/reading leases;
retain fault/output/recovery gates. Only then design bounded packing across
reads, preserving EOF, Stop, ordered codec changes and maximum-frame liveness.
Do not infer a small packet from the server's write size: ESP-IDF's HTTP reader
normally accumulates the requested read length before returning.
