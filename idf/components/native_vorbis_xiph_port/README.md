# Focused Xiph resource port

This separate candidate preserves the pinned `native_vorbis_xiph` baseline.
Its generator validates both complete manifests, retains every original byte
under `base/`, and creates only ten modified translation units and three owned private headers under `ported/`.
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

A ninth exact edit removes both partition-sized stack arrays from
`vorbis_book_decodevs_add`. It decodes each word once and scatters directly as
specified by [Vorbis I 8.6.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).
On nominal packet EOP, complete earlier words in the current partition remain
published as section 8.6.2 requires. Successful per-sample additions are
unchanged; the separately allocated PCM and codebook value arrays never alias
in the decoder. This adds no allocation or new OOM status. Empty-book, positive
dimension and upper-layer geometry assumptions are otherwise unchanged.

Seven further exact edits check every allocation in header book/floor/
residue/mapping/comment/mode parsing. Explicit checked variants report
OV_EFAULT for required allocation failures; malformed headers keep their
existing status. The original pointer-returning callback signatures remain
as thin wrappers. The public header parser uses a local status and checked
dispatch tables bound to the pinned registry sizes at compile time. There is
no shared mutable error state, TLS, errno inference, public ABI change, or
modified baseline header. Legal zero-size NULL allocations are preserved.
The generated private header declares only these checked entry points.

Seven additional edits check the shared decoder DSP, MDCT and floor/residue
lookup initialization, with partial-owned arrays safe for cleanup. The PCM
pointer array is zero-initialized; pcmret is freed independently. A private
checked MDCT initializer preserves the original void wrapper and transform
arithmetic. Public synthesis initialization retains its documented 0/1 return
contract. Failed initialization may have consumed static books; callers close
the entire stream and replay headers to recover. Encoder-only paths and packet
allocations are not covered by this decoder-init change.

An independent comment-API edit removes all query allocations and makes
append failure atomic. Checked private variants return OV_EFAULT/OV_EINVAL;
the original void wrappers retain their signatures. Three required allocations
prepare new pointer/length arrays and one string before publishing state.
Existing string/vendor pointers and length-delimited bytes remain unchanged;
tag appending writes directly into its final string. Queries preserve ASCII
case-insensitive matching and borrowed value pointers without temporary tags.
This metadata-only qualification does not resume the deferred DSP scheduling
gate or change its watchdog NONPASS.

Neither production application selects this component. The previous unchanged
31-case numerical checkpoint remains separate. Resource tests must not imply
general OOM recovery or a complete decoder stack bound: packet arena/floor/residue allocation paths still require qualification.
DSP target qualification remains separately deferred. Channel-sized mapping/residue scratch and unchecked allocations elsewhere
still require work. No deferred vendor/Ogg scope is
reopened, and no physical performance claim is made.
