# Exact Vorbis setup ownership

This optional component owns the four arrays used by the existing
`native_vorbis_numeric` setup parser. It retains the original packed VQ fields,
active Huffman entries, multiplicands and configured graph after incoming
identification/setup buffers are released. It does not expand floating tables.

The opaque handle uses caller-supplied allocator callbacks. A replacement is
published only after complete validation, addressability checks, allocations
and materialization. Failure preserves the previous handle and every borrowed
view. A successful replacement or clear ends those borrows; each owner releases
its storage through its original allocator. The allocator context must remain
live, allocations must have malloc-compatible alignment, and callers serialize
all reads and lifetime operations. There is no default allocator or global state.

The control object and four actual-size arrays need at most five allocations;
empty word/multiplicand pools are skipped. Failure-atomic replacement temporarily
holds both owners, so it does not promise lower peak memory. Individual storage
objects are checked against `size_t` without adding a format limit. The existing
allocation-free measure API exposes complete uint64 storage requirements.

This is the ownership prerequisite in the
[VQ integration plan](../../../docs/CYD_XIPH_VQ_RANGE_DESIGN.md). Neither radio
application selects it yet. Header ordering/comments, stream registration,
selection of the numeric route, floor/residue/synthesis wiring and target
resource qualification remain separate. It does not resume any deferred scope.
