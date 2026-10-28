# Selected bigfloat warning review

The 42 creator-code warnings reported on each native target do not reveal a
new reachable defect in the checked basic-arithmetic closure under its stated
input and resource contract. Eleven warnings belong to that closure and have
the guarded/bounded explanations below. The other 31 belong to unselected
debug, decimal, string or transcendental code. Several of those are real type
contract problems if those entry points are enabled; this review does not
declare all creator code safe or suppress its diagnostics.

This review changes no arithmetic, corpus, sanitizer, compiler option or
component selection. It does not certify the forthcoming gain functions.

## Evidence and version boundary

The actual LX6 and RV32 compiler logs are retained in
`.build/vorbis-bigfloat-profiles-20261028-03/`. Each reports 40 diagnostics in
`portable/libbf.c` and two in unchanged `upstream/cutils.c`, with no compiler
error. The adapter and C++ header smoke test are clean under `-Werror`.
Classification per target is 21 `-Wsign-compare`, 13 `-Wformat=` and eight
`-Wunused-parameter` warnings. There is no shift-count warning in this set.
The separately retained adapter-TU Clang warning is discussed below; it is
not an additional creator GCC warning hidden in the 42 count.

The profiles03 libbf log bytes are identical across targets, SHA256
`eb42047c6084b8f4fdd534a149c3f15063647a7123808812b507865273c6f0d0`.
Both cutils logs have SHA256
`0b731a16c99e2127823cedc0fe14c728ad152ad1203e60e096bcafd2b581d97d`.
Locations in the tables are **profiles03 historical source lines**, including
macro expansion locations. That profile compiled the first portability copy,
SHA256 `598d82bf113286953a72b2c1f8824d1411745bcc4e4928bab5c8ccf8989c9bbe`.

The current portable source additionally contains the confirmed zero-length
copy repair, SHA256
`158da48780e54571ae2ce56ef7049f9829f62817c005009c9018bdf74d92a378`.
That insertion shifts subsequent source lines by one; the function identities
and reviewed comparison expressions remain the same. Final native profiles04
completed on that two-repair copy, retaining the same 40+2 creator warnings per
target, clean adapter/header `-Werror` checks and one original-header Clang
warning. All 14 process records are terminal, with eight ELF32 objects and
eight .su records. Its report is
`.build/vorbis-bigfloat-profiles-20261028-04/report.json`, SHA256
`fe56791c7a310c1039fca41f724b889231aeef3e4cc92bedbeef829190702090`.
This is source compilation, not native arithmetic execution.

The immutable original is still SHA256
`8abc36c9feaeaeb04729e3494c6b693611a518442d11c6546c86bc08b30a1228`.
The [source manifest](../idf/components/native_vorbis_bigfloat/upstream-manifest.json)
and [exact two-hunk patch](../idf/components/native_vorbis_bigfloat/portability.patch)
bind both local repairs. Failed historical attempts remain separate evidence.

Host04 completed ASan/UBSan execution on the current two-repair portable copy:
699 rows per limb model, 461/823 actual allocator-refusal ordinals, exact
directed Fraction/isqrt comparisons and recovery, with real NTT initialization
on dense 8192-bit products. The retained source/fixture campaign is
`.build/vorbis-bigfloat-host-20261028-04/`. These finite checks supplement the
source argument; they do not prove all precisions, all upstream entry points,
native runtime execution or full Vorbis gain.

## Contract used to assess selected comparisons and shifts

The reviewed closure starts only at
[the checked adapter](../idf/components/native_vorbis_bigfloat/bigfloat.c), not
at arbitrary exported LibBF symbols. Operands are initialized, finite,
normalized numbers belonging to the same live context. Mantissas and precision
are bounded by P=1048576 bits; precision 0/1 and unknown rounding modes are
rejected. Physical binary tops are in [-P,P]. The adapter publishes a private
result only after error, finiteness and range checks, and its allocator makes
shrink/free infallible while preserving the actual allocated capacity.

The [engine closure argument](../idf/components/native_vorbis_bigfloat/README.md)
bounds normal temporary limb counts by 65540 on the native32 path. Signed
indices, cancellation counts and ordinary bit offsets remain well within
INT32_MAX. Exact-import normalization also uses BF_PREC_INF: its large
negative bit offsets remain within the signed limb type; they are not being
mistaken for small ordinary precision offsets.

On the actual native profiles `LIMB_BITS==32` and pointer size 4 were asserted.
The source uses uint32 limbs with uint64 intermediate arithmetic. The observed
`slimb_t` typedef is signed long, while `limb_t` is unsigned long. Positive
bounded indices convert exactly; a negative value must be excluded before
an unsigned bounds comparison. Intentional all-ones arithmetic remains unsigned.
The implementation also relies on the pinned GCC targets' signed-conversion
and arithmetic-right-shift behavior. This is not a portability proof for a new
compiler or arbitrary raw `bf_t` bytes.

The NTT resource proof supplies a valid search candidate and bounds selected
k<=16 on native32, below the recursive k>19 path. Its allocation, count and
shift products are bounded; allocation refusal is permitted. This argument
does not assume that a requested precision means the NTT ran: Host04 checked
the actual per-context NTT initialization for large operands.

## Eleven warnings in the selected closure

| Historical location / function | Count | Reason and boundary |
| --- | ---: | --- |
| 363, `get_bit` | 1 | `i < 0 || i >= len` short-circuits negative indices before the unsigned comparison. Nonnegative i and bounded len fit the signed type. Out-of-range positions return zero before dereference. The final shift uses `pos & (LIMB_BITS-1)`, in 0..31. |
| 551, `__bf_round` | 1 | The carry loop begins at a nonnegative limb position only when discarded nonzero bits require an increment. Its precision<=0 branch is handled separately. If precision exceeds the available bits, inexact/add-one is false. Thus i is nonnegative and bounded by the temporary length; the carry shift is masked to 0..31. |
| 632, `bf_normalize_and_round` | 1 | i starts at 0 and increases to bounded l. The highest retained limb is nonzero, so clz is in 0..31. The two complementary shifts execute only when shift!=0, making both counts 1..31. The zero case leaves before these accesses. |
| 873, `count_cancelled_bits` | 1 | Comparing unsigned v2 to -1 intentionally converts -1 to the limb's all-ones value. This tests the binary pattern used by the cancellation loop, not a negative array index or signed magnitude. Cancellation length remains bounded by the finite operand span. |
| 965 and 1001, `bf_add_internal` | 2 | The source access is guarded by `ap >= 0 && ap < a->len`; the result loop starts i at 0. The signed offsets can represent the bounded alignment span. Their intentional unsigned-to-signed offset construction is assessed for the pinned target semantics, not generalized to arbitrary C implementations. |
| 1049, `mp_add` | 1 | i starts at 0; n is a bounded nonnegative limb count and cannot approach signed overflow. Carry wrap is in unsigned limb arithmetic. |
| 1379 and 1384, `mp_recip` | 2 | These two comparisons occur in the n<=2 base case: loop limits 2*n and n+1 are at most 4 and 3. Negative index promotion cannot occur. Both scratch allocations are checked before access and released on failure. |
| 2079, `mp_sqrtrem` | 1 | `n2=n/2+1` is positive, at most 16385 for the selected native32 top-level sqrt request. Its comparison with the unsigned stack-array count 8 is exact. The heap branch checks its allocation before recursion. |
| 7773, `int_to_ntt_limb` | 1 | The scalar integer backend does not need parameter m when returning its integer representation. This is an unused parameter, not a dropped allocation status or unchecked shift. The selected NTT indices and input residues are assessed under the separate engine closure. |

These are ten signedness comparisons and one unused parameter. No warning was
removed and no blanket cast was added. The bounds cease to be applicable if a
caller mutates a live number, bypasses the adapter, supplies another context's
storage or changes the precision/exponent envelope without reviewing closure.

## Thirty-one warnings outside that closure

| Functions / historical locations | Count | Disposition |
| --- | ---: | --- |
| Binary debug printers `dump_limbs`, `mp_print_str`, `mp_print_str_h`, `bf_print_str`: 696/698/708/748 and macro 66 expanded at 710/721/724/747 | 9 | Eight printf argument-type mismatches and one sign comparison. On native picolibc long and int are distinct types even when their widths match. These are real variadic type-contract warnings if invoked. The checked arithmetic API does not call these printers; debug macro branches remain disabled. Do not enable them without a separate formatting repair/review. |
| `bf_get_exp_min`:1645 | 1 | Its scan is not used by the selected adapter; dyadic/floor export uses checked owned bit extraction instead. The warning is retained rather than extending this review to every integer/power helper. |
| `bf_atof_internal`:3005; `bf_ftoa_internal`:3760 | 2 | String parser/formatter entry points are excluded. Their independent radix, precision, buffer and allocation contracts are not established by basic arithmetic operand bounds. |
| `bf_exp`, `bf_pow`, `bf_cos` and their exp/log/cos/sin/tan internals:4280/4422/4431/4791/4938/4963/4972/5006 | 8 | Three signedness comparisons and five unused parameters. These functions and creator constants are not selected. No enclosure proof follows from accepting their directed-mode argument or from finite reference agreement. |
| Decimal debug printers, decimal sqrt/digit/add/division helpers:5780/5791/5794/6054/6272/6273/6308/6647/6913 | 9 | Five printf mismatches, three sign comparisons and one unused parameter. Decimal arithmetic is outside the binary checked contract. These remain visible diagnostics, not qualified code. |
| cutils `dbuf_default_realloc`:150; `dbuf_printf`:225 | 2 | The default allocator's opaque parameter is unused. The formatter compares signed vsnprintf length with an unsigned buffer size; its full formatting/error contract needs separate review if exposed. Neither function is called by the selected basic arithmetic. Binary bit helpers used from cutils.h are a separate inline path. |

The adapter-TU Clang warning at upstream/libbf.h:155 assigns
`(flags >> BF_EXP_BITS_SHIFT) & BF_EXP_BITS_MASK` to int. The mask is 0x3f, so
the result is in 0..63 and the conversion is exact on both supported targets.
It remains reported, with no new suppression. It is not evidence of an
out-of-range shift count.

## Confirmed defects and retained safeguards

Two concrete defects were already corrected independently of this warning
classification:

- Native profiles02 rejected passing slimb_t* (picolibc long*) as the int*
  output of `bf_get_int32`. The portability copy now receives into a local int,
  preserves the returned status and assigns the value to slimb_t. No pointer
  reinterpretation or warning downgrade is used.
- Host03 UBSan stopped at `bf_set`:313 after zero+zero addition reached
  `memcpy(NULL,NULL,0)`. The portable copy now skips exactly the zero-length
  copy. Host03's terminal failure and sources stay preserved; Host04 exercised
  the repaired path under the same sanitizers and corpus.

The upstream zero-operand add branch can also discard a failed copy status;
the adapter's sticky allocator latch prevents publication of that result.
Every allocation failure is evaluated before its private result is committed.
This safeguard must remain even when compiler warnings are unchanged.

Stock `bf_get_float64` is still excluded because its unchecked failed copy can
lead to a NULL limb access before a caller can examine a latch. Stock signed-si
setters/helpers are excluded for unrestricted INT64_MIN negation. The selected
wrapper instead imports an unsigned magnitude and exports dyadics/floor
integers without either unsafe path. No test or diagnostic setting was relaxed
to make an excluded path appear acceptable.

## Residual limits

This is a review of the recorded warnings and selected closure, not a complete
proof of LibBF. It does not qualify creator debug/string/decimal/transcendental
APIs, arbitrary compiler semantics, every allocation/precision combination,
native execution, physical real-time performance or universal RAM fit. Native
source profiles and per-function .su records do not measure complete runtime
stack depth. Passing the finite host campaign does not establish certified
pi/sine/log remainder bounds or full-domain floor0 gain. Actual resource
refusals remain typed retryable engine outcomes, never Vorbis format limits.
