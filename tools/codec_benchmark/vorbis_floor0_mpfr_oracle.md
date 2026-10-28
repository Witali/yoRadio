# Independent host floor0 gain oracle

`vorbis_floor0_mpfr_oracle.c` uses real MPFR >=4.2 headers and GMP. It is an
independent directed reference for one **supplied exact Bark index**, not a
production decoder or a memory-safe MCU backend. Default GMP/MPFR allocation
failure may terminate this host process. There is no recoverable allocation,
deadline, firmware memory-fit or universal correct-PCM claim.

The local dependency build is under
`.build/vorbis-floor0-mpfr-oracle-deps-20261028-01/`: official pinned MPFR4.2.2,
static library, installed GMP development header/library, no system installation.
Its `build-report.json` retains commands, terminal status and hashes. The source
manifest beside this document pins the official release. Oracle qualification
and sanitizer compilation are separate from that dependency build.

Example host compile, after the dependency build (replace `$prefix` with its
absolute Linux `install` path):

```sh
cc -std=c11 -O1 -g -Wall -Wextra -Werror -fno-fast-math -ffp-contract=off \
  -I"$prefix/include" tools/codec_benchmark/vorbis_floor0_mpfr_oracle.c \
  "$prefix/lib/libmpfr.a" -lgmp -o oracle
./oracle --max-precision 8192 requests.txt
```

`--version` prints actual MPFR/GMP runtime versions. The explicit caller budget
`--max-precision BITS` is required for numerical requests; it bounds requested
precision before any MPFR allocation. A valid above-budget request returns
`resource/caller_precision_budget` with null numerical fields and terminal0.
There is no hard-coded universal mathematical precision cap. With that option
and no file argument the oracle reads stdin. One complete request per
LF-terminated line; CRLF is accepted:

```text
F0MPFR1 precision order bark_bin bark_map amplitude_bits raw_amplitude offset [minimum_bits delta_bits minimum_multiplier delta_multiplier]...
```

All integers are canonical unsigned decimal: no signs, leading zeros (except
`0`), hex prefixes or extra tokens. Spaces/tabs separate numeric tokens. The
four-field tuple uses the public `native_vorbis_affine_t` order and appears
exactly `order` times. Ranges: order0..255; map1..65535; bin0..map-1;
amplitude_bits0..63; raw0..2^bits-1 (bits0 requires raw0); offset0..255;
each affine field0..UINT32_MAX. Precision is the requested **bound** precision,
within the actual library's `MPFR_PREC_MIN..MPFR_PREC_MAX`. This is not a promise
that any fixed precision resolves every legal request, nor that extreme library
precision values can be allocated without fatal host resource failure.

Malformed, binary, overlong or trailing partial records emit an `invalid` JSON
record and make the terminal exit code2. There is no silently accepted partial
last line. Valid requests emit one JSON line in order, numbered from1:

```json
{"schema":"F0MPFR1","ordinal":1,"status":"unity","reason":"exact_identity","precision":128,"denominator":{"lo":{"hex":"1","exp2":0},"hi":{"hex":"1","exp2":0}},"log2_gain":{"lo":{"hex":"0","exp2":0},"hi":{"hex":"0","exp2":0}},"floor_lo":"0","floor_hi":"0","floor_equal":true}
```

This example is produced by `F0MPFR1 128 0 0 1 8 255 60` followed by newline.
Each dyadic means `int(hex,16) * 2^exp2` **exactly**. Hex integers are signed,
without `0x`; zero is canonical `{hex:"0",exp2:0}`. Nonzero exports remove
trailing binary zeros when the signed export exponent permits it. Floors are
unbounded signed hexadecimal integers, never machine-word conversions.

| Status/reason | Available values and meaning |
| --- | --- |
| absent/raw_zero | Denominator/log/floors null; floor synthesis is unused and no mathematical domain evaluation is needed. |
| pole/exact_zero_denominator | Exact denominator `[0,0]`; log/floors null; positive scaled amplitude divided by zero. |
| indeterminate/exact_zero_denominator | Exact denominator `[0,0]`; log/floors null; zero offset gives `0/0`. |
| unity/exact_identity | Positive denominator retained; exact log `[0,0]`, floors0. |
| certified/floor_agrees | Directed denominator/log bounds retained and both endpoint floors agree. This certifies this integer floor only, not linear-gain rounding or later PCM. |
| unresolved/denominator_lower_zero | Denominator retained; log/floors null. Retry the original exact input with greater precision. Rounded cancellation is not relabelled a pole. |
| unresolved/integer_boundary | All bounds and both different floors retained. Refine or retain the uncertainty. |
| range/mpfr_range_or_nonfinite | Library exponent/range or unexpected nonfinite refusal; unavailable fields null. |
| resource/caller_precision_budget | Valid precision exceeds the explicit caller budget; all bounds/floors null, retryable without entering MPFR. |
| invalid/protocol | All numeric fields null, including precision; terminal failure. |

For each exact affine angle, the oracle first constructs the complete signed
integer on the `2^-788` grid using GMP. It imports that integer at sufficient
precision for an **exact** MPFR input, even when the requested bound precision
is smaller. It then bounds its cosine directly. The Bark cosine uses
`mpfr_cosu(integer_bin,2*map)` with an exact integer input. There is no binary64
input, rounded affine sum, production phase grid or half-angle implementation.

Let `c=cos(pi*bin/map)`, and let `E/O` be products of
`[2*(cos(phi_i)-c)]^2` at even/odd indices. For odd order,
`D=O*(1-c^2)+E/4`; for positive even order,
`D=O*(1-c)/2+E*(1+c)/2`; order0 is exactly `D=1`. Interval differences and
products use directed MPFR arithmetic. Squaring an interval crossing zero has
lower bound0 and maximum squared endpoint as upper bound. Thus cancellation in
the independent direct-cosine method causes wider bounds or refinement, not a
false nonzero/zero claim.

Exact poles are recognized before numerical evaluation: a rational affine
angle can share the cosine of a rational multiple of pi only at angle0 and
Bark0 in this domain. There P vanishes and Q vanishes precisely when an
even-index affine angle is exactly0. Non-pole requests require a strictly
positive **numerical lower bound** before division. Offset0 is an exact unity
identity after the exact pole exclusion, even if its retained coarse direct-cos
denominator lower bound is zero; that route performs no division.

With `A=raw*offset/(2^bits-1)`, the enclosed logarithm is
`L=(11512925/100000000)/ln(2) * (A/sqrt(D)-offset)`. Both rationals are exact
before directed conversion; negative intermediate intervals select the correct
constant endpoints. No huge `exp2(L)` is constructed. An integer-boundary
interval may remain unresolved indefinitely, including an exact boundary not
otherwise established as an identity. Every retry starts from original input.

Creator references: [Vorbis I6.2.3 and9.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
[MPFR4.2.2 manual](https://www.mpfr.org/mpfr-4.2.2/mpfr.html),
[GMP allocation contract](https://gmplib.org/manual/Custom-Allocation).
This oracle does not certify discrete Bark selection, MCU resource handling,
wider transforms, previous-block precision/history or final PCM decisions.
