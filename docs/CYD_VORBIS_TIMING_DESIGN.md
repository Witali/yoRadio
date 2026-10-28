# Granule positions and bounded current-output trimming

The [timing API](../idf/components/native_vorbis_timing/include/native_vorbis_timing.h)
implements integer metadata decisions independently of synthesis. Its inputs
are decoded block sizes, packet granule positions, EOS and an explicit sequence
discontinuity indication. It touches no packet bytes, DSP buffers, overlap or
PCM. The caller consumes previous ready data before accepting another block.

Primary sources are the [Vorbis mapping appendixA.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
[Ogg granule field definition](https://xiph.org/ogg/doc/ogg-multiplex.html),
[packet-position documentation](https://xiph.org/vorbis/doc/programming.html),
and pinned Xiph [block.c](../idf/components/native_vorbis_xiph/upstream/libvorbis/lib/block.c)
restart/sequence-gap/granule decisions. The original Xiph license is retained
in the component. No original decoder source is changed.

## Units and wire domain

Counts are original-rate PCM frames **per channel**, independent of channel
interleave, output bytes and later resampling. The first block primes and has
zero ready frames; later blocks have(A+B)/4. All legal64..8192 power-of-two size
pairs are supported. Xiph's optional half-rate API is separate from this
full-rate metadata contract, rather than a new encoded-format restriction.

Wire granules use signed64: -1 is unset,0..INT64_MAX are known. Values below-1
are invalid Vorbis position metadata. This does not exclude a negative inferred
starting offset; that offset is the difference between a known endpoint and
the nominal decoded count, and determines leading trim. High-bit wire patterns
other than the all-ones sentinel are not reinterpreted as large positive
timestamps. A transport may retain their original bytes for diagnostics.

## Reference decisions

| Event | Current ready-data decision |
| --- | --- |
| First block after init/reset | Prime; return0 frames. |
| First known endpoint below nominal decoded count | Drop leading excess. |
| First known endpoint with EOS | Drop trailing excess instead. |
| Later EOS endpoint below prediction | Drop trailing excess. |
| Non-EOS endpoint mismatch | Resynchronize position, retain ready samples. |
| Endpoint ahead of prediction | Resynchronize without manufacturing silence. |
| Unset EOS endpoint | Retain data; add no wire anchor or trim. An existing estimate still advances. |

Every drop is bounded by currently ready data. The API returns a contiguous
subspan [discard_start,discard_start+count); it cannot rewind delivered frames.
For two64-sample blocks,32 frames are ready. A first known endpoint10 discards22
at the beginning unless EOS, which discards22 at the end. Endpoint64 requires
no drop and corresponds to a positive inferred start. A first-and-last audio
page therefore uses trailing trimming rather than assuming a negative start.

A sequence gap forgets the position and local decoded count but retains the
previous block size. Its current block can still emit data; the new local count
starts at0, matching Xiph. Hard restart/seek reset is different: it discards the
previous size and primes again. The stream owner separately chooses and applies
its numeric lapping/reset policy. EOS is sticky until hard reset; logical-link
ownership decides when a new stream begins. This helper neither infers sequence
numbers nor validates Ogg page placement. AppendixA.2's page-flush requirement
for nonzero initial offsets belongs to transport validation.

Unknown EOS positions and inconsistent non-EOS anchors have reference-compatible
recovery behavior here; that is not a declaration that such Ogg pages conform
to the container mapping. Malformed metadata rejection and stream recovery
remain separate responsibilities.

## Safe counters without a stream-length limit

Use C=INT64_MAX+4096. Internal local-count and predicted-end fields retain
min(mathematical_value,C). For any wire anchor G<=INT64_MAX and ready span<=4096:

```
value >= C  =>  value-G >=4096
min(max(value-G,0),ready) == ready
```

Capping therefore preserves every trim decision. Below C the counters remain
exact. Saturating increments compose, explicit anchors resynchronize prediction
and gaps reset the local count. An indefinitely unmarked stream does not cause
counter overflow or acquire an artificial accepted-length cap. At C, public
bounded state fields describe only a lower bound, not an exported exact total
or inferred start. A known prediction beyond the signed wire domain has an
explicit EXCEEDS_WIRE_DOMAIN result; end_position is0 in that case, rather than
a narrowed or misleading exact timestamp.

For example, a previous endpointINT64_MAX followed by32 ready frames and an
EOS endpointINT64_MAX drops32 frames. The untrimmed prediction exceeds signed64,
but its valid trim calculation fits unsigned64 and must not be rejected as an
overflowing stream. Excess is compared with the ready span before narrowing;
the ILP32 `long extra` intermediate from the original reference is not copied.

All state/event validation precedes writes. Failed init/reset/push preserves
the actual object bytes; successful push publishes a local candidate state and
result. State, event and result are disjoint and caller-serialized. No heap,
VLA, floating arithmetic, task or production selection is introduced. Timing
decisions alone do not establish PCM correctness, first-page transport validity,
floor0/wider synthesis, raw lifecycle, native resource use or physical behavior.
The original full31 PCM/bound2/all14 relations and deferred scopes remain open.
