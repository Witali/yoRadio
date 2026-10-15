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

## Hardware qualification pending

Build with the same local-CA diagnostic profile as the utilization control,
changing only the tail-coalescing flag. Compare committed READY bytes, ownership
distribution, output events, real allocation failures and settled recovery on
the same AAC TLS pause schedule. Then check TLS format transitions and finite
files. An improvement in packet fill alone is insufficient for production.
Public-source and quiet production timing qualification remain separate.
