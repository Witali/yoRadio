# Selected directed bigfloat arithmetic

This internal component reuses LibBF2025-06-03 basic arithmetic.
It supplies checked directed primitives for a future certified gain layer; it
does not certify pi, phase reduction, sine, logarithms, floor0 gain or complete
Vorbis synthesis. It is not selected by the production decoder.

The creator is Fabrice Bellard. All six files in `upstream/` retain their
original bytes and MIT notices. `upstream-manifest.json` binds the official
[source archive](https://bellard.org/libbf/libbf-2025-06-03.tar.gz) and every
retained file. `portable/libbf.c` is mechanically generated from the unchanged
original with exactly the two local edits in `portability.patch`: a local int receives
`bf_get_int32` output before assignment to slimb_t. The pinned native picolibc
defines int32_t as long, so its slimb_t pointer cannot be passed as int pointer.
The status and value are preserved without casts or diagnostic suppression.
A second guard skips `bf_set`'s copy when the source length is zero: Host03
UBSan confirmed that zero+zero addition otherwise calls memcpy with NULL
pointers and length0, violating the builtin's nonnull contract.
The manifest records both exact old/new replacements and original/final hashes. No
arithmetic algorithm or selected source operation is changed by this patch.
The creator's [documentation](https://bellard.org/libbf/readme.txt)
explicitly identifies missing rigorous error proofs and allocation-error
reporting for some transcendental functions. Passing finite reference vectors
cannot replace those proofs.

## Selected contract

Initialize one context with copied allocate/release callbacks and opaque
storage, then initialize each `bf_t` with the checked API. Serialize operations
on that context. Numbers must stay in that context; allocator storage outlives
all numbers/caches. Clear each number before ending its context. Context end
clears caches and refuses to deactivate if live numbers still own storage.

Only exact unsigned/dyadic import, copy, addition, subtraction, multiplication,
division, square root and directed rounding are selected. Precision is2..1048576
bits. Directed down/up are the only accepted rounding modes. Every arithmetic
operation prepares a private result and publishes it after status, finiteness
and engine-range checks. It can safely alias the destination with an operand;
all failures preserve the old destination fields and allocation contents.
NaN, invalid arithmetic, division by zero, underflow and overflow never become
successful interval endpoints.

The custom realloc bridge allocates before freeing on growth. A failed growth
leaves the old block intact. Shrink/free are infallible; shrinking retains the
actual allocation capacity instead of pretending the backend returned bytes.
The sticky allocation-failure latch catches even an upstream ignored status.
After an allocation refusal, clear that latch explicitly before retrying.
Cleanup, stats and read-only exports remain available. Statistics count actual
backend allocation bytes including the alignment/header overhead; transient
growth includes both old and replacement blocks. `ntt_initialized` reports an
actual engine cache created only by NTT initialization, not requested precision.

Dyadic export is canonical signed odd magnitude times a signed binary exponent,
using portable little-endian uint32 words. Floor export returns a signed
arbitrary-limb integer magnitude, including -1 for a tiny negative input. It
never narrows that integer value into int64 or the machine-sized `bf_t.expn`.
Measures/exports allocate nothing and preflight every output resource; failed
exports preserve all output metadata and bytes. Unused output capacity is not
written. Zero exports count0, exponent0 and negativefalse.

## Conservative engine envelope and closure

These are engine resources, not stream limits: significant mantissas have at
most P=1048576 bits, physical binary tops are in[-P,P], and input dyadic
magnitudes have at most32768 uint32 words. An unaddressable or larger engine
request returns retryable ENGINE_LIMIT. Actual allocator refusal returns
NO_MEMORY. No claim is made that this envelope is a universal required
precision bound for encoded floor0; a future wider backend/resource policy may
be required rather than treating a legal stream as malformed.

The stock header selects32-bit limbs/uint64 intermediates on LX6 and RV32;
64-bit hosts with int128 use64-bit limbs. A host build with
`-U__SIZEOF_INT128__` selects the original32-bit limb path without changing the
header. P is divisible by both limb widths. Valid published values have at most
32768/16384 limbs. Their smallest represented binary scale is >=-2P.

Addition with exponent distance<=1 can have at most P+1 cancelled bits and a
total span<=P+64; at greater distances cancellation is bounded by1 and the
precision request limits result scratch. Exponent distances are <=2P. Ordinary
finite-precision bit offsets stay below a conservative16P+4096, far below
INT32_MAX. Exact-import normalization also uses the stock BF_PREC_INF sentinel:
its derived negative offsets remain above -BF_PREC_INF-1, safely within slimb_t
on both limb models (the sentinel is2^(LIMB_BITS-2)-1).
Multiplication starts with at most twice the operand limb count. Division uses
n=max(input limbs,ceil((precision+2)/LIMB_BITS)), at most32769/16385. The main
reciprocal/remainder products have total length at most2(n+1). Within
`mp_recip`, the second product has lengths2h+1 and h+1, where
h=n-floor((n-1)/2): one factor can be n+3. Their total3h+2 is <=2(n+1) for n>=6.
For n<=5, the base or small recursive cases need at most11 product limbs and
cannot reach the100-limb NTT threshold. Sqrt uses at most twice this n and
logarithmic recursive depth. Thus the global temporary limb-count bound is
65540/32772 and direct byte products are <=262160;
the extra NTT buffers below are also bounded before source integer arithmetic.

Unchanged NTT is retained. On32-bit limbs its largest multiplication has
length<=65540. The creator's3-modulus search has a valid dpl36,k16 candidate:
ceil(65540*32/36)<=65536 and16+2*36<=89. Its cost is3342336. Every k>=17 candidate
costs at least7077888, so the selected k<=16. On64-bit limbs length<=32772;
dpl84,k15 is valid (15+168<=185), cost1572864; every k>=16 costs>=3342336.
Both stay below the scalar transform's k19 cache boundary, so recursive
`ntt_conv` with an ignored child status is unreachable, and the no-candidate
abort is unreachable. The search's products/costs are bounded below2^31.
NTT buffer/strip allocations use these k values, five moduli at most and
STRIP_LEN16; their byte products also remain below2^31. Actual memory may still
be refused and must be unwound. The engine's default29/61-bit exponent range
has ample headroom for the selected transient tops (bounded by16P+4096);
the wrapper also rejects every reported overflow/underflow.

This closure assumes well-formed initialized objects, immutable borrows, valid
callbacks and the unchanged source/control paths. It is an auditable resource
bound, not a formal verification of the complete upstream implementation.

## Deliberately excluded entry points

The wrapper never calls the stock constants/transcendentals, string parsing or
formatting, `bf_get_float64`, `bf_set_si` or signed-si helpers. In this release,
the add/sub zero-copy branch can lose an allocation error; the bridge latch
handles it before publication. The stock float64 exporter instead can
dereference NULL after an ignored failed copy, before a caller can check a
latch, so it is excluded. The signed setter negates INT64_MIN in signed C;
unsigned magnitude import avoids that path. No upstream source patch hides
these findings. Future interval constants/functions need explicit rational or
Taylor remainder bounds over the checked basic arithmetic.

## Observed qualification and remaining gates

The [host checkpoint](../../../tests/results/vorbis-bigfloat-20261028/CHECKPOINT.md)
checks 701 exact Fraction/isqrt cases on both host64 and forced32 limb builds
with ASan/UBSan. All 1288 selected allocation refusals recover with the exact
output, preserving old destination fields/storage. Dense 8192-bit products
enter actual NTT; export/capacity/alias/context controls remain explicit.
The [native source profiles](../../../tests/results/vorbis-bigfloat-20261028/SOURCE_PROFILES.md)
compile the final adapter, portable dependency and C++ header for LX6/RV32.
They are compile-only evidence, with no SDK/QEMU execution or final linked
code-size result. The [warning review](../../../docs/CYD_VORBIS_BIGFLOAT_WARNING_REVIEW.md)
distinguishes the checked closure from excluded entry points and retains
their diagnostics. Original creator bytes and both explicit repairs are pinned.

Actual target execution, native stack/heap/code measurements, full gain and
downstream synthesis remain required. The finite corpus and conservative
envelope are not a universal mathematical precision certificate or an MCU
memory-fit claim. Published x86 code-size figures are not ESP32 measurements. LibBF
stores significands and work arrays on the allocator; sqrt/reciprocal have
recursive stack frames. NTT retains per-context caches until context end.
Code size and total temporary heap depend on the linked selected closure;
the build uses the full portability copy and unchanged cutils with function-section collection
provided by the native toolchain. No global rounding mode, shared error state,
task, lock or production binding is introduced by this adapter.
