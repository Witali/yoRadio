# Actual packet-frame floor0 application before the reused IMDCT

The [original-data audit](CYD_VORBIS_FLOOR0_ROUTE_AUDIT_20261028.md) identifies
168 floor0 packets among the original434, all with ordinary finite gain
ranges. This component connects their existing exact packet-frame data to the
existing inverse transform. It adds no FFT, alternate packet decoder, Ogg
controller or production selection. Floor1 continues through its unchanged
exact product/conversion route. The whole original434-packet identity set must
be retained in qualification.

The [public API](../idf/components/native_vorbis_floor0_spectrum/include/native_vorbis_floor0_spectrum.h)
borrows a successful immutable frame/setup and one selected type0 channel.
Prepare publishes a plan; materialize consumes only a binary64 candidate plan
and writes a `native_vorbis_transform_block_t` for
`native_vorbis_imdct_transform_binary64`. The frame and all scratch/lookup
borrows stay alive and immutable until consumption. Even a failed reuse of the
front-end workspace expires the old frame and its dependent plan.

## Preserve domain meaning before choosing a representation

Original floor presence decides silence. Absent floors bypass Bark/LSP work,
including when inverse coupling left nonzero residue. Active zero rate/map
fields are unresolved mapping domains; the layer does not turn them into new
header errors. Order0 retains its decoded-packet semantics but has D=1. An
active zero residue can be silenced only after finite gain is established.

Every encoded affine LSP is a rational dyadic. At a mapped angle theta=r*pi,
0<=r<1, equality cos(phi)=cos(theta) requires phi=(2k±r)*pi. Nonzero rational phi
cannot meet that condition. At theta0, the Vorbis denominator retains the
even-index LSP product squared; hence an even-index exactzero LSP is exactly
the denominator-pole condition. Empty order has no such pole. The packed21-bit
mantissa times a uint32 multiplier fits53 significant bits. Each affine term
is therefore exactly binary64, with finite exponents, and nonzero affine sums
have quantum at least2^-788. Testing their floating sum forzero cannot invent
a zero by underflow. The sum need not otherwise be exactly representable.

This classifies poles before zero-residue shortcuts. Positive offset gives a
pole; zero offset gives the distinct indeterminate0/0 domain. Neither supplies
an invented concealment or PCM policy. If D is positive, offset0 is exact unity;
finite gain times exactzero residue is zero, even when its finite linear gain
would require an enormous representation. This does not resolve active mapping
domains when rate/map is zero.

## Candidate gain factors are approximate

Other nonzero bins use the existing owned original-affine scaled-log gain.
Split the usable stored logarithm L=q+f and compute binary64 exp2(f), with its
exact53-bit significand retained separately from q. A rounded f==1 is allowed
and represented by its correct factor exponent. No huge standalone exp2(L),
floating residue conversion, source clipping or fabricated floor1 product is
used. Zero residue bins need no gain evaluation after domain classification.

A scaled logarithm exponent>=53 has no retained binary64 fractional precision
and routes the whole channel to NEEDS_PRECISION. Lesser exponents are **not**
a universal gain-accuracy guarantee. The `minimum_log_fraction_bits` field
describes only stored-log resolution; upstream denominator/transcendental
errors are separate. Non-identity gains explicitly mark the candidate
approximate. The plan keeps the original amplitude/LSP/rate/map/residue data
for refinement. Neither int64 fit nor passing an ordinary corpus certifies
extreme finite gains. NEEDS_WIDER/PRECISION is not an implemented fallback or
permission to reject valid streams. Production route selection remains open.

## Joint integer multiplication and one rounding

Each source sample is a strict signed integer S with at most34 words and1087
magnitude bits at this helper boundary. Multiplication by a nonnegative53-bit
factor uses two32-bit passes and an unsigned36-word magnitude: |S*M|<2^1140.
Only then does the converter select high53 bits and guard/sticky information,
round nearest-even, and pack binary64 bits. Input sign is applied afterward.
There is no intermediate overflowing cast or double rounding of residue.

For nonzero products, scan their exact physical top-bit positions. Let H be
the maximum and h the minimum. The common output exponent is H-638. If
H-h<=1660, every working top lies in[-1022,638]; a rounding carry may reach639.
All nonzero inputs are normal, and magnitude<=2^639 satisfies the existing
IMDCT contract. A wider span routes the complete channel to NEEDS_WIDER,
retaining provenance. Zero channels write canonical+0 with exponent0.

Materialization validates all shapes/capacities, selected source domains and
factors/working tops before output writes. Failure preserves output/result;
prepare may change provisioned scratch during later numeric failure/routing
and publishes its plan last. Caller buffers/descriptors are disjoint and reuse
is serialized. No heap, VLA, new task or changed display/audio backend.
At4096 bins the map/factor arrays cost8192+65536bytes and the candidate output
32768bytes, excluding frame/setup/IMDCT/radio state. This is a storage cost,
not a claimed CYD optimization; buffers can be reused between channels.

The actual packet-to-spectrum/IMDCT test is distinct from the stopped
overlap/PCM composition controller: it executes no window, overlap, granule
trimming or PCM. Full31 PCM/bound2/all14 relations, wider/certified synthesis,
measured window underflow, raw lifecycle, native/resources/performance and
physical qualification remain open. Existing deferred scopes are untouched.

## Observed qualification

The [checkpoint](../tests/results/vorbis-floor0-spectrum-20261028/CHECKPOINT.md)
preserves the actual C packet front end: original identification/setup/audio
bytes are parsed again before this component runs. All434 original packets
retain their modes/cursors/header identities and fourteen relation identities.
The test does not feed previously captured gains into a detached transform.
Floor0 covers336 original channels; floor1 retains532 original channels through
its unchanged product/conversion path. Thirteen raw-packet supplements add
absence with coupling, exact unity/order0, mapping/pole/indeterminate outcomes,
finite zero, precision/wider routes and a tiny-negative-log normalization case.

Final447 packets/894 channels pass ASan/UBSan, with4,522 expected refusals and
5,155,393 guard checks. An independent exact integer oracle verifies116,960
joint roundings;5,376 nonzero original floor0 values use800-digit gain
references. Maximum floor0 relative error is4.850438525866904e-15 against the
fixed2e-12 corpus bound. The existing independent FFT oracle checks751,360
IMDCT values: maximum error/L1 is8.881784197001252e-16 against5e-12. These are
finite-corpus results, not certification of all valid encoded gain domains.

The separate integer-math campaign covers81,384 rows, all1,087 source widths,
53 factor widths and1,661 working tops,2,851,560 exact product words and66,151
exact rounded values. Nine math and ten frame corrupted captures are rejected.
Production clang-tidy has zero warnings/errors for both new C units; C/C++
source profiles produce six ELF32 objects across LX6 and RV32IMC. Own frames
exclude callees/task high-water; no SDK/native/firmware performance is claimed.
Frame-fixture lint retains twelve include/byte-snapshot diagnostics without
suppression; the integer fixture has none. The pure checkpoint reader verifies
archive contents and replays independent comparisons without archived execution.
