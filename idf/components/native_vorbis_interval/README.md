# Rigorous intervals over selected bigfloat arithmetic

This internal layer constructs mathematical enclosures with explicit series
remainders. It uses the checked `native_vorbis_bigfloat` basic operations,
never the creator's constants/transcendentals, string conversion, float64
exporter or signed-si helpers. It is a component of the forthcoming certified
floor0 gain; it does not complete the gain, wider transform/history, decoder
integration or physical-board qualification.

The dependency retains the creator's MIT files and exact portability repairs:
[source manifest](../native_vorbis_bigfloat/upstream-manifest.json),
[basic-engine contract](../native_vorbis_bigfloat/README.md), and
[remaining gain requirement](../../../docs/CYD_VORBIS_CERTIFIED_GAIN_REMAINING.md).
The frozen foundation wrapper is SHA256
`dc848de646f25ff5a8a4997cd422718e23ace867502b19e6062ca22887a4d93a`;
its portable LibBF copy is SHA256
`158da48780e54571ae2ce56ef7049f9829f62817c005009c9018bdf74d92a378`.
No frozen dependency is modified here.

## Ownership and arithmetic

A scope borrows one serialized bigfloat context and requests precision p in
2..1048576. Exact dyadic/u64 imports and copies retain their full supplied
significands independently of p, subject to the foundation's checked engine
envelope. This matters for exact affine LSP terms much wider than an initial
requested endpoint precision. A live context is never copied. An interval owns
two independent initialized endpoint allocations belonging to that context.

Every operation validates the destination and inputs before arithmetic, builds
a private pair, and swaps both descriptors only after the pair is complete.
The old destination is then cleared from the private pair. This ownership
transfer cannot allocate. Operand/destination aliasing is supported for whole
interval objects; partial overlap, shallow copies of live ownership, callback
reentry and concurrent context mutation are outside the contract. Private
cleanup clears endpoints independently because an unfinished pair need not
have established ordering yet. Failure leaves the caller's endpoints and their
allocation contents unchanged; temporary ownership is released. Context cache,
allocation counters and sticky failure state can change. The caller explicitly
clears the foundation's OOM latch before retrying.

Addition and subtraction use directed monotone endpoints. Multiplication and
zero-free division take the minimum of four downward corner results and the
maximum of four upward corner results. A divisor containing zero returns
NEEDS_PRECISION, except an exact-zero divisor returns ARITHMETIC. These are
arithmetic-layer outcomes; they do not classify a Vorbis packet. Square uses
the two endpoint squares and inserts an exact lower zero when the input
contains zero. Sqrt applies monotonic directed endpoints to a nonnegative
input; uncertainty extending below zero returns NEEDS_PRECISION, and an input
entirely below zero returns ARITHMETIC.

Negation reverses two private endpoint copies and flips their signs exactly.
Power-of-two scaling also copies both endpoints exactly. It bounds the signed
scale before adding it to a nonzero endpoint's already bounded physical top,
then updates only that private descriptor's exponent. The result remains in
the checked foundation envelope. Scaling zero never adds an untrusted signed
exponent. Comparisons use validated finite descriptors; no global rounding
mode or unchecked numerical conversion is involved.

## Constant proofs

For 0<x<1, integration of the finite geometric expansion of 1/(1+t^2)
gives the alternating arctangent expansion. After terms through
x^(2k+1)/(2k+1), the absolute remainder is at most
x^(2k+3)/(2k+3). `atan_reciprocal` uses exact x=1/5 or 1/239, encloses every
term by directed interval arithmetic, and expands the partial-sum interval by
the next term's upward endpoint. Uncertainty from rounded x, powers and sums
is retained; the alternating remainder is an additional error bound.

Machin's identity is pi=16*atan(1/5)-4*atan(1/239). The tangent addition/double
angle identities give tan(4*atan(1/5)-atan(1/239))=1; the positive principal
angle selects pi/4. Applying the above arctangent enclosures, exact power-of-two
scales and outward subtraction therefore encloses mathematical pi. No rounded
constant or unexplained guard-bit claim is substituted for that remainder.

Integrating the positive geometric expansion of 1/(1-t^2) gives
ln2=2*atanh(1/3)=2*sum x^(2k+1)/(2k+1), x=1/3. Beyond the partial sum, replacing
every later denominator by the first omitted denominator bounds its positive
tail by2*next_term/(1-x^2)=(9/4)*next_term. The implementation uses an exact
dyadic9/4 and an upward next-term bound. It leaves the partial sum's downward
endpoint as a lower bound and adds the proved positive tail to the upper.

The truncation target is2^-p. That target bounds the explicit series tail;
it does not assert that the final enclosure has width2^-p. Every arithmetic
rounding contribution is already represented by the two endpoints. Pi's final
identity scales its arctangent tails by16 and4. Callers may request more
precision/refine when the resulting enclosure is too wide for their decision.
Constants have no internal global cache; a gain owner may retain proven pairs
externally at each requested precision.

## Reduction proof and arbitrary quadrants

The trig caller supplies a proved enclosure of mathematical pi, normally a
cached result of this component. Numeric endpoint checks alone cannot certify
that provenance. A nonpositive pi lower endpoint cannot establish division
and returns NEEDS_PRECISION.

The reduction computes an interval enclosing angle/(pi/2)+1/2, takes the exact
integer floor of its lower endpoint, and imports that integer without narrowing.
Only the integer's magnitude modulo4 and its sign are used as machine values.
The integer itself is portable little-endian uint32 data. For a negative
magnitude m, q mod4 is(-m) mod4. The floor buffer is allocated through the
foundation context's checked allocator and is always freed.

This is a *candidate* nearest quadrant, not a claim that a rounded quotient
proved a uniquely nearest integer. For every integer q the identities
sin(x)=sin(r+q*pi/2), cos(x)=cos(r+q*pi/2) hold with r=x-q*pi/2. Directed interval
multiplication/subtraction encloses that r despite uncertainty in supplied pi.
The routine verifies the complete residual enclosure lies in[-2,2]. Failure
returns NEEDS_PRECISION; it never silently reduces with an unproved small
residual. A wide input interval can remain undecided under refinement.

The usual exact quadrant identities choose sine/cosine and a sign from q mod4.
No fixed-width conversion of q, floating remainder, stock transcendental or
single approximate pi is used. A singleton zero residual returns sine0 and
cosine1 exactly before power/series evaluation. This does not invent symbolic
correlation for two independently supplied interval ranges.

## Taylor enclosure and tiny sine

For every |r|<=2, sine and cosine have their ordinary Taylor expansions. In
the discarded tail the absolute terms are decreasing: after the first
discarded sine term their ratio is at most4/(4*5); after the first discarded
cosine term it is at most4/(3*4). The alternating-tail theorem therefore bounds
the remainder after any retained polynomial by the next absolute term.

The partial polynomial is evaluated with interval recurrence, including an
interval square with nonnegative lower bound. A separate positive bound E is
updated upward using M^2 and exact factorial-step divisors, where
M=max(|residual.lo|,|residual.hi|). Hence E bounds that next absolute term for
every input in the residual interval, regardless of endpoint correlation loss
inside the polynomial. The sum is expanded symmetrically by E and intersected
with the known range[-1,1]. Range intersection does not replace a remainder.

Cosine stops when E<=2^-p. Sine stops when E<=M*2^-p. It does not compare tiny
sine against a fixed absolute epsilon. For example a residual near2^-789 stays
represented by its original nonzero scale. The comparison with the relative
target uses physical tops first. Only on equal tops does a read-only descriptor
view align the validated significand for exact comparison; no unrepresentably
tiny target is allocated, and no caller descriptor is changed. The equal-top
view itself has the physical top of the already checked E.

This bounds truncation, not the final interval's relative width. Reduction and
arithmetic endpoint widths remain visible. If they prevent a later positive
denominator or rounding decision, the consumer must refine or preserve a typed
incomplete outcome.

## Termination and resource bounds

All series loops have at most p+32 iterations, with no data-dependent unbounded
retry. Exhausting that budget returns NEEDS_PRECISION. For the constants, even
the coarsest supported precision encloses x<=3/8 and x^2<=3/16. An upward
binary rounding contributes a factor less than2, so the positive power bound
decreases by at most3/8 per iteration. The explicit small tail multipliers
therefore permit this conservative iteration budget when the engine can
represent the intermediate values. For trig, two upward point operations
give a next-term factor at most16/d, where d is the increasing factorial-step
divisor; after a fixed initial prefix this is less than1/2. The same budget
is conservative relative to M for sine and relative to1 for cosine.

At p<=1048576, the largest counter-derived factorial-step divisor is below2^43
and is formed in uint64. Odd series denominators stay below2^22. Physical-top
comparisons use signed64 values bounded by a few multiples of the engine
envelope. The floor buffer is at most32768 uint32 words; its byte extent is
checked before allocation. All automatic arrays have fixed sizes. There is no
VLA, heap-backed recursion, hidden default allocator, global cache or lock in
this layer. The foundation retains its own separately qualified scratch and
recursive integer algorithms.

Precision is not artificially capped at8192. The foundation's checked1M-bit
engine envelope is retained. A required intermediate can still leave its
physical exponent or mantissa range, or actual memory can be refused. Those
return ENGINE_LIMIT/NO_MEMORY transactionally; they are retryable resource
outcomes, not a universal precision promise or a Vorbis format restriction.
The finite loop count is a correctness guard, not an MCU running-time promise.

## Required qualification

This source addition has not itself launched a compiler, sanitizer, SDK or
emulator. Root review precedes any execution. Required evidence includes
independent exact interval primitives, MPFR directed constants/direct-cosine
gain comparisons, both limb models, every observed allocation ordinal with
recovery and endpoint byte snapshots, exact zero/tiny/huge quadrant cases,
unresolved reduction/divisor controls and actual native memory/stack/runtime
checks. Finite agreement does not replace the proofs above, and these interval
primitives do not establish full-domain gain or decoder production readiness.
