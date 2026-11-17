# Warning review after Ogg word-page staging

The six profiles retain 100/98/99 warning occurrences for
PDM/continuous/legacy, for both vendor and custom FLAC. All warning sites
were compared by file, check, message and multiplicity with the
[previous catalog](../cyd-production-refresh-20261117/clang-warnings.json).
Line movements are retained in the new catalog.

One diagnostic changes in every profile. The earlier
`clang-analyzer-core.UndefinedBinaryOperatorResult` in the Ogg page store
is replaced by `clang-analyzer-core.NullDereference` at the header read
in `opi_feed`. The new trace enters `opi_set_word_allocator` with
`size == 0`, frees idle byte storage and sets both page and capacity to
zero. It then returns through the successful Family 1 page handler and
enters the next `opi_feed` with `size >= 27`, without an intervening write
to size. That transition is inconsistent with the single-owner state.
The actual next feed starts at size zero and reserves the 27-byte header
before storing input or reading the lacing count.

The source invariant is that a nonempty page has allocated byte-addressable
header storage. ACK/reset make size zero; allocator switching is refused
while size is nonzero or a page is ready. Allocation refusal returns
before adding bytes, and word allocation retains the header. Existing
ASan/UBSan page and lifecycle cases cover allocation refusal, ACK/reset,
byte/word switching, continued input and complete-page copying. The
creator-backed Family 1 regression and mixed SDK task campaign also pass.
[Runtime and host evidence](../cyd-vorbis-openeth-20261117/README.md)

No production guard, analyzer suppression or numeric oracle was changed
to remove this diagnostic. Its exact site remains in
[the current catalog](clang-warnings.json). All other diagnostics retain
the prior [warning review](../cyd-production-refresh-20261117/WARNING_REVIEW.md).
