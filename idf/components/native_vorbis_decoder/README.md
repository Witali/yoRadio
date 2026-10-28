# Persistent public raw Vorbis owner

The public API owns setup, immutable window and transform lookups, per-channel
transform work and half histories, and reusable packet/floor scratch. It calls
only the existing public owned components. It retains no incoming header or
audio packet pointer, performs no transport parsing, and changes no production
registration, task, core, audio backend or display configuration.

Replacement first builds a separate setup owner and decoder candidate. All
initial storage and windows are prepared before the handle changes. The saved
allocator callbacks/context are copied; the context must outlive its handles.
Failure releases only the candidate. Successful replacement publishes the new
handle before releasing the old one. Clear nulls the handle before callbacks.

Measure reads a packet prefix and previews timing on a copy without allocating
or advancing state. Process checks exact interleaved S16 capacity and byte
extent before scratch growth or DSP work. Each channel is decoded/transformed
into private storage before one all-channel synthesis call commits PCM/history
and position. No callback or fallible work follows that commit. Failed packets
may change internal scratch, but preserve committed setup/history/timing/EOS,
the caller's output and the public result. Scratch growth allocates before
releasing the prior allocation; failed lookup construction publishes no cache.

Frame storage follows the existing conservative all-present measurement. These
are upper workspace requests, not measured per-packet RAM. Allocation refusal
is resource exhaustion and checked byte overflow is RANGE; neither adds a
format cap. There is no internal full PCM buffer. The caller owns the output
and must keep it disjoint from packet data, descriptors and the owner.

EOS and granules come from packet metadata, not HTTP completion or array order.
Successful EOS is terminal until no-allocation reset or setup replacement.
Reset retains storage/tables, discards overlap/position, and primes again
without reading old history. No synthetic final packet or zero-input flush is
provided. All use is serialized by the caller; no locking is introduced.

The mathematical scope is unchanged: ordinary floor0 gain and binary64 IMDCT
are approximate. Wider, precision and undefined floor0 routes have distinct
statuses and preserve committed state; they are not implemented fallbacks or
permission to misclassify valid packets. The owner remains unselected pending
numeric, container, resource and actual audio-task qualification. See the
[design](../../../docs/CYD_VORBIS_DECODER_DESIGN.md) for the remaining gates.
