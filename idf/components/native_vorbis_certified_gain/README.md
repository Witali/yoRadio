# Directed floor0 log-gain enclosure

**Deferred at the user's request on 2026-10-28.** This source has not been
compiled or numerically qualified. Work continues on reuse of the Espressif
decoder; retain this candidate for a future explicit resume only. See
[the saved-work record](../../../docs/CYD_VORBIS_EXTENDED_DEFERRED_20261028.md).

This component computes an enclosure of mathematical `log2(G)` at one supplied
exact Bark index. It is a candidate arithmetic layer, not a selected firmware
decoder, an Ogg adapter, a Bark-index implementation or a wider PCM pipeline.
It does not construct the potentially enormous linear gain `G`.

The creator equations are [Vorbis I 6.2.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
and pinned Xiph 1.3.7 `lib/lsp.c`. The independent host reference uses direct
MPFR cosines; this implementation instead uses stable half-angle products over
the [proved interval functions](../native_vorbis_interval/README.md).

## Exact inputs and denominator

Each encoded affine angle has two terms. A packed mantissa has at most 21 bits,
its unsigned multiplier at most 32 bits, and its packed exponent is in
`[-788,235]`. Thus each exact term has at most 53 significant bits and the
two-term sum has at most 1077, including a carry across the complete exponent
span. Import both integer/dyadic terms and add at 1100 bits before interval
operations. No binary64 sum or trigonometric approximation discards the input.

Let `theta=pi*index/map`, `d_i=4*sin((theta+phi_i)/2)*sin((theta-phi_i)/2)`,
`E=product(d_even^2)`, `O=product(d_odd^2)`,
`minus=4*sin(theta/2)^2` and `plus=4*cos(theta/2)^2`.
Then the specification's denominator is:

- odd order: `D=(O*minus*plus+E)/4`;
- positive even order: `D=(O*minus+E*plus)/4`;
- order zero: `D=1`, preserving the existing packet semantics.

The sign of each `d_i` is immaterial after squaring. Squares have a rigorous
nonnegative lower bound; products are never silently flushed to zero. Any
failure to establish a positive lower bound requests precision rather than
inventing a malformed-stream result.

Exact dyadic LSPs are rational. They can have the same cosine as a rational
multiple of pi in `[0,pi)` only at LSP zero and Bark index zero. There D is
zero precisely when an even-index LSP is zero. Detect that identity before
the offset-zero shortcut. Positive offset yields POLE, zero offset yields
INDETERMINATE, with no fabricated PCM policy. Once poles are excluded, zero
offset is unity even when coarse numerical work could not separate D from zero.

## Log gain and uncertainty

The implemented formula is
`L=(11512925/100000000)/ln(2) * (raw*offset/((2^bits)-1)/sqrt(D)-offset)`.
All integer operands enter exactly before directed arithmetic; `raw*offset`
is not narrowed through a fixed-width product. The specification's decimal is
retained exactly as a rational, rather than replaced with a rounded double.
Every returned finite interval encloses L; its width also includes constant,
phase, sine, product, square-root and division errors.

Floor measurement/export returns both signed arbitrary-length integer bounds.
They may differ. Retain that uncertainty or recompute from original inputs at
more precision; no universal finite refinement count or fixed fractional-bit
guarantee is claimed. The concrete tiny-LSP example can require a gain exponent
whose integer magnitude exceeds 1572 bits, while L itself remains a finite
bigfloat value. The exponent of G is separate data, not `bf_t.expn`.

## Lifetime and failure behavior

A caller-owned workspace retains its copied allocator, checked arithmetic
context and pi/ln2 caches for the current precision. Each initialized result
owns its denominator and log endpoints in that workspace. Clear all results
before ending the workspace; an early end refuses without clearing caches.
Inputs stay immutable and no input pointer is retained after a call. Retrying
requires the original exact inputs, which the caller continues to own.

Enclosure prepares a private complete result before swapping any endpoint into
the caller's result. Negative API/resource errors preserve all old metadata,
endpoint descriptors and allocation bytes. Private caches may change. OOM
remains latched until explicitly cleared; cleanup and exports do not allocate.
Successful ABSENT, POLE, INDETERMINATE, UNDEFINED_MAPPING and NEEDS_PRECISION
outcomes retain their separate meanings. A raw-zero floor does not read angle
or mapping data; active map zero does not read LSPs. Order remains an eight-bit
field. A positive map needs a valid supplied index and complete immutable LSPs.

Both output floor capacities and extents are preflighted before either buffer
or metadata is written. Output arrays/descriptors, live inputs and workspace
storage are disjoint caller-owned objects. Unused capacity is never written.
Operations on one workspace are serialized; there is no global rounding state.

## Qualification boundary

This source is awaiting host/reference/OOM and native qualification. A valid
interval algorithm does not by itself prove acceptable memory, stack or runtime
on a CYD. The existing checked engine envelope is a resource boundary, not a
Vorbis format restriction. Complete Bark selection, exp2 conversion, independent
wide exponents through IMDCT/window/history, final PCM decisions, transport and
the radio/TLS/TFT resource gate remain required. No task affinity, priority,
stack, display/audio backend or production registration changes here.
