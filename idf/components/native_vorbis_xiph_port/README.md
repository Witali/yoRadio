# Focused Xiph resource port

This separate candidate preserves the pinned `native_vorbis_xiph` baseline.
Its generator validates both complete manifests, retains every original byte
under `base/`, and creates only three modified translation units under `ported/`.
Each declared before fragment must match exactly once. `PORTING.json` records
all edits and compiled file hashes. No fuzzy patching or external patch tool is
used. The source version and successful decoding arithmetic remain upstream's.

The declared deviations cover optional arena consolidation after realloc
failure, and decode-codebook scratch/checked allocation cleanup. The latter
also makes a valid first-table word shift explicitly unsigned. The port uses
the same base-library units, types, floating configuration and narrow GCC
diagnostic adaptations as the original evaluation.
The first ASan/UBSan corpus run also found signed byte-promotion shifts in
libogg 1.3.5. Four reader functions backport the unsigned-long shifts present
in [official libogg 1.3.6](https://github.com/xiph/ogg/blob/v1.3.6/src/bitwise.c).
Bit-reader tests use an independent per-bit LSB/MSB oracle; the rest of 1.3.5
remains pinned. No sanitizer or numerical threshold is disabled.

Neither production application selects this component. The previous unchanged
31-case numerical checkpoint remains separate. Resource tests must not imply
general OOM recovery or a complete decoder stack bound: other block, DSP,
header, floor and residue allocations still require qualification. In
particular, `vorbis_book_decodevs_add` has partition-sized stack scratch outside
the decode-book initialization repaired here. No deferred vendor/Ogg scope is
reopened, and no physical performance claim is made.
