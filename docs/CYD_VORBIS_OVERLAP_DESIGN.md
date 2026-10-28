# Adjacent-block synthesis without early scale alignment

The [overlap API](../idf/components/native_vorbis_overlap/include/native_vorbis_overlap.h)
uses the actual adjacent block sizes, as allowed by
[Vorbis I sections1.3.2 and4.3.8](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).
The [pinned Xiph implementation](../idf/components/native_vorbis_xiph/upstream/libvorbis/lib/block.c)
also delays window application until the actual neighbor is available.

For previous size A and current size B, ready data spans the interval between
their centers and has length(A+B)/4. Let M=min(A,B). Both slopes occupy M/2
samples; the preceding plateau has length(A-M)/4 and the following plateau
has length(B-M)/4. At output coordinate t, the previous full-block index is
A/2+t and the current index is t+(B-A)/4; out-of-support contributions are zero.

| Transition | Ready interval |
| --- | --- |
| short to short | short falling/rising slopes |
| long to long | long falling/rising slopes |
| long to short | previous unity plateau, then short slopes |
| short to long | short slopes, then current unity plateau |

The implementation uses nonnegative plateau/sliding indices, avoiding unsigned
subtraction of B-A. It borrows the existing prepared binary64 windows. The first
block only caches its unwindowed right half; no ready data is emitted. This
works for either first size, including equal configured short/long sizes. Each
accepted block caches its own unwindowed right half for the next neighbor.
A silent current block still emits the previous nonzero tail. There is no
invented final zero packet to flush history.

The result retains two scaled blocks, one contribution per ready sample from
each neighbor. Exponents are copied independently, including both signed64
endpoints; they are never subtracted, narrowed or used in floating scaling.
The consumer must add both terms before final rounding/clipping. This preserves
huge cancellation and tiny half-tie perturbations at that boundary, provided
the incoming windowed terms themselves have retained the needed information.

Init reserves long_size/2 history doubles. Output needs up to long_size/2 doubles
for each term; at8192, these three arrays use98304bytes, excluding source blocks,
windows, transform/setup and radio state. This is an explicit resource cost,
not a measured RAM saving. State and all input/output/lookup borrows are disjoint
and caller-serialized. Output buffers must be consumed before reuse.

Measure is read-only and publishes its result last. Push checks all descriptor
shapes, byte extents, capacities, complete source values and active history
values before writing anything. Every returned failure preserves state, history,
both outputs and result, so the caller can retry with adequate output storage.
After all checks it writes terms, copies the new right half and publishes state
and result. Reset validates configuration, discards previous size/exponent and
leaves history bytes untouched. A following priming block does not read them.
No heap, VLA, internal lock, task or changed production selection is introduced.

Window products remain ordinary binary64 operations. For example a minimum
subnormal multiplied by a small positive slope can round to zero before an
exponent1074 would make its unwindowed physical value one. Keeping separate
exponents prevents **additional** alignment loss; it does not repair this prior
underflow, inherited IMDCT approximation or arbitrary floor0 gain spans. Tests
retain and count such witnesses. Full-range floor0/synthesis and complete PCM
accuracy therefore remain open, rather than declaring a new accepted-format cap.

Granule/EOS trimming, sequence discontinuity decisions, per-channel scheduling,
final PCM conversion and raw/radio integration belong to subsequent layers.
Original31 PCM cases/bound2/all14 relations and SDK/resource/physical gates are
not closed by standalone overlap tests. Production affinity and backends remain.
