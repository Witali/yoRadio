# Exact setup owner for the future Vorbis numeric route

The separate `native_vorbis_setup_owner` component implements ownership of the
existing exact setup representation. Its [API](../idf/components/native_vorbis_setup_owner/include/native_vorbis_setup_owner.h)
accepts identification/setup packets, returns a borrowed immutable setup view,
and provides failure-atomic replacement and idempotent clearing. It does not
change either application's decoder registration or the Xiph resource port.

The complete setup parser remains in `native_vorbis_numeric` and allocates
nothing. The owner first validates both packets and all four object-byte sizes,
then allocates its control object, books, active words, actual multiplicands and
configuration records through callbacks. Empty word/multiplicand arrays are
skipped. This is at most five allocations, without expanded floating tables.
All narrowing to `size_t` occurs after object-addressability checks. The existing
measure API retains full uint64 requirements; no new format limit is imposed.

After materialization, every view pointer belongs to those allocations. Packed
minimum/delta fields, original sparse entry indexes and integer multiplicands
remain intact. Incoming packet storage can be overwritten and freed. This is
the prerequisite for preserving VQ values before Xiph consumes its static books;
connecting the owner to a raw decoder still remains.

Each owner stores allocator callbacks/context by value. Its context outlives
the owner and returns malloc-aligned, disjoint live allocations. Any failed
replacement frees its partial candidate and preserves the previous handle,
borrowed pointers and bytes. Success publishes the new handle before releasing
the old allocations through the old allocator. Clear publishes NULL first.
Prior borrows end only on successful replacement or clear. Callers serialize
reads and lifetime operations; callbacks cannot reenter or modify the handle.
Writable handle storage cannot overlap inputs, allocator metadata or owner
storage. Replacement temporarily needs both owners; this is not a peak-memory
saving claim.

The owner has its own OK/INVALID/RANGE/TRUNCATED/NO_MEMORY status domain. It
distinguishes allocator refusal from numeric CAPACITY, which describes caller
storage shortage. Header ordering, BOS, comments, Ogg transport and raw decoder
error translation remain separate responsibilities.

## Qualification

The [host checkpoint](../tests/results/vorbis-setup-owner-20261026/CHECKPOINT.md)
contains all 300 earlier setup cases, all 31 unchanged Xiph header pairs and
four additional zero-pool/sparse cases: 335 total, 295 valid and 40 full-header
failures. The independent setup oracle generates every expected retained field.
The C fixture compares all books, words, raw packed values, multiplicands,
configuration records and typed getters after freeing both packet buffers.

It also refuses every allocation ordinal during creation and replacement,
checks independent live owners and allocator contexts, mutates the caller's
allocator descriptor, verifies zero-size skips, preserves byte snapshots on
failure, and sweeps every incomplete valid-header prefix. Actual ASan/UBSan
results are 5,378 successful opens, 399,810 parse failures, 2,982 allocation
refusals and 19,038,727 assertions, with no sanitizer diagnostics. The parse
total includes 399,770 prefix cuts and 40 full-header failures. All three empty
pool combinations execute. RANGE addressability rejection is source-reviewed,
not dynamically exercised by this finite host corpus.

Initial Xtensa Clang analysis found padding in the generated test-case metadata.
Reordering those fields and using designated initializers removes 8 bytes per
constant row on Xtensa without changing the corpus or component. Both complete
host runs are retained; the final six-unit Clang run has zero warnings/errors.

[Native target preparation is incomplete](CYD_VORBIS_SETUP_OWNER_TARGET_DEFERRED_20261026.md).
No SDK build or QEMU execution qualified this owner. Full native qualification
must retain all 335 cases and their prefix sweeps, with scheduling at the
fixture's polling points. The archived initial subset prototype is not that
gate. Production stack/heap behavior, numeric route selection, floor/residue/
coupling/transform integration, original unshifted PCM and the three physical
outputs remain open. Existing deferred scopes were not resumed.
