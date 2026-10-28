# Exact S16 conversion after scaled overlap

The [pair API](../idf/components/native_vorbis_pcm/include/native_vorbis_pcm.h)
converts two independently scaled binary64 contributions to signed16 PCM:

```
clamp_S16(roundTiesToEven((a*2^Ea + b*2^Eb)*32768))
```

The pinned Xiph [vorbisfile conversion](../idf/components/native_vorbis_xiph/upstream/libvorbis/lib/vorbisfile.c)
also scales by32768 and saturates to[-32768,32767]. This adapter deliberately
defines nearest-even exactly for the supplied dyadic terms. It does not rely
on a floating environment, overflowing float-to-int conversion, or early
per-term clipping. Exact cancellation of two huge terms yields zero; an
arbitrarily tiny nonzero term can still decide an ordinary half-integer tie.

Both source counts must match. Each entire signed64 exponent is accepted, and
every finite binary64 coefficient is accepted, including signed zero and the
minimum subnormal. A zero count permits null arrays/output. Descriptors remain
required; capacities count elements and must have addressable byte extents.
All shapes, capacities, pointers and finite-input checks precede output writes.
Every refusal preserves source bytes/descriptors and output. Immutable sources
may share storage, but output is disjoint. No heap, VLA or `__int128` is used.

## Exact comparison

Decode a binary64 coefficient to a signed integer significand and a power of
two, include the PCM factor2^15 in its exponent, then normalize its nonzero
significand to exactly53 bits. The exponent is a portable signed two-word
integer; adding binary64/normalization offsets cannot wrap an int64 endpoint.
Only unsigned carry arithmetic operates on that representation.

For a candidate S16 code k, compare the exact sum with k+.5 by adding its
negation as a third normalized dyadic. Sort nonzero terms by exponent. If the
largest exponent exceeds the second by at least2, that largest term exceeds
the sum of both smaller terms in magnitude and determines the sign. Otherwise
the largest two exponents differ by0 or1: align and add/subtract them exactly
in at most55 significand bits. The remaining two-term comparison orders their
top-bit positions, and only aligns significands if those positions match.
That alignment fits55 bits. It never subtracts unbounded exponents or shifts
by an unbounded count. Exact cancellation exposes the third term unchanged.

A16-step binary search over codes[-32768,32767] uses those exact comparisons.
At equality, choose the even neighboring integer. Endpoints saturate, including
-32768.5->-32768 and32767.5->32767 after nearest-even reaches32768. No real-time
performance or memory saving is claimed; target timing remains a separate gate.

## Independent qualification

The host oracle forms complete arbitrary-precision integer sums for exponent
spans up to8192 bits, then rounds by integer division/remainder. It does not
reuse the C ternary comparator or threshold search. Across larger gaps, a
finite53-bit coefficient's smaller term can affect rounding only at an exact
half tie; the oracle retains its sign there. Explicit symbolic half-tie
identities and2,000 `Fraction` comparisons check that independent rule.

The corpus has2,479 batches/478,388 outputs: all65,538 signed half-grid
boundaries around and beyond the S16 endpoints, positive/negative infinitesimals
at INT64_MIN, subnormal tie-breakers, all integer codes and clipping edges,
all2,047 finite binary64 exponent fields, integer significand widths1..53,
nearby exponent distances-2..2, the complete selected extreme-scale matrix,
huge cancellation, and deterministic random finite values. Refusal checks
snapshot actual input bytes and supplied descriptors immediately around each
call, including injected NaN/Inf bits before restoration. Seven corrupted
captures are rejected by a pure reader.

The source-only GCC profiles compile C and C++17 for LX6 and RV32IMC. Clang-Tidy
finds no production warnings/errors. Five fixture diagnostics concern its own
pre-call object-byte snapshots, including padding; those verify unchanged
storage rather than equality of independently constructed objects. No warning
suppression is used. Public own frames176B on each ISA and private comparator
frames336/320B exclude callees and task high-water.

This boundary is exact for its two supplied terms. It does not establish the
accuracy of approximate floor/IMDCT/window calculations, arbitrary floor0 gain
representations, granule/EOS trimming, the complete31-case PCM campaign,
native execution or production radio integration. No production component
selection, audio backend, task placement, or deferred scope is changed.
