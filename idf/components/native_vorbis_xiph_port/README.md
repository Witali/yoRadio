# Focused Xiph resource port

This separate candidate preserves the pinned `native_vorbis_xiph` baseline.
Its generator validates both complete manifests, retains every original byte
under `base/`, and creates eleven modified C units, four owned private headers
and a three-file public header overlay under `ported/`. Two overlay headers
remain byte-identical; the codec header declares the unsigned-rate extension.
Each declared before fragment must match exactly once. `PORTING.json` records
all edits and compiled file hashes. No fuzzy patching or external patch tool is
used. The source version and successful decoding arithmetic remain upstream's.

The declared deviations cover optional arena consolidation after realloc
failure, and decode-codebook scratch/checked allocation cleanup. The latter
also makes a valid first-table word shift explicitly unsigned. The port uses
the same base-library units, floating configuration and narrow GCC
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

Nine packet-path edits make arena growth transactional and check PCM, floor
memo, lazy floor0 map and residue allocations. A local checked floor dispatch
distinguishes required allocation failure from nominal unused-floor/EOP; mapping
propagates negative residue/floor statuses before synthesis can return success.
No complete residue partition, no stages and no active residue2 channels remain
successful no-work cases. Existing registry signatures and public ABI are retained.
The port extends vorbis_synthesis's error results with OV_EFAULT for required
allocation failure; the [upstream API](https://xiph.org/vorbis/doc/libvorbis/vorbis_synthesis.html)
documents 0/OV_ENOTAUDIO/OV_EBADPACKET only. On
any nonzero result the block must not be submitted to synthesis_blockin. Close
the block/DSP/info/comment owners and replay all three headers for recovery.
This does not qualify encoder allocation paths or change nominal EOP behavior.

Mapping and residue0/1 channel-pointer scratch now has a fixed two-channel
stack fast path. More channels use checked block storage and propagate
OV_EFAULT on refusal. Mono/stereo allocation behavior is unchanged; wider
streams trade channel-sized task-stack use for temporary arena heap ownership.
This is a bounded-stack change, not a measured total RAM or speed saving.
No-work residue paths return before allocating the wider scratch.

The public rate field now uses unsigned long where long is 32 bits; on LP64 it
retains long. This represents the entire positive unsigned 32-bit identification
rate without clamping or storing negative bits. Public struct storage, alignment
and offsets stay unchanged, while the source signedness is an explicit 32-bit
API extension. Consumers must rebuild with the matching generated headers;
old binaries using signed long cannot interpret newly accepted high values.
Two checked 16-bit reads distinguish 0xffffffff from EOP. Zero remains invalid,
signed bitrate hints stay unchanged, and existing granule_time division sees
the positive rate directly. No physical output-rate capability is implied.
The overlay exports codec.h plus unchanged vorbisenc.h/vorbisfile.h copies so
their quoted sibling include selects the same type. Encoder and convenience
library rate consumers remain separately unqualified.

Neither production application selects this component. The previous unchanged
31-case numerical checkpoint remains separate. Resource tests must not imply
general OOM recovery or a complete decoder stack bound: packet-path qualification
is recorded separately. DSP target qualification remains separately deferred.
Native stack/resource qualification and unchecked allocations elsewhere
still require work. No deferred vendor/Ogg scope is
reopened, and no physical performance claim is made.
