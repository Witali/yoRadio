# Remaining floor0 numerical work

Full floor0 support remains required by the
[Vorbis transfer plan](CYD_VORBIS_TRANSFER_DESIGN.md). The refreshed
[31-case current-source checkpoint](../tests/results/vorbis-current-format31-20261024/CHECKPOINT.md)
still fails the unchanged project limit of 2 signed16 units. Its twelve floor0
cases include all six original odd/even cases and their six equivalent
representations. They are not omitted or relabelled as supported.

## Public source findings

[Vorbis I section 6.2.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
specifies Bark mapping, odd/even LSP products and an exponential floor gain.
Xiph v1.3.7 [lsp.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/lsp.c)
and [scales.h](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/scales.h)
implement that gain without a unity ceiling for positive dB.

The retained public low-memory
[Tremor floor0 source](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/floor0.c)
instead caps positive-dB conversion at unity. Its inverse1 also stores amplitude
in Q4 and LSP coefficients in Q24. The
[owned public-curve experiment](../tests/results/cyd-vorbis-public-floor0-curve-20261023/CHECKPOINT.md)
checked 168 calls using explicitly constructed values in those representations.
It did not observe the opaque backend's actual callback memo or establish its
internal cause. The public-source discrepancy is a candidate explanation only.

## Requirements for a complete correction

Replacing only inverse2 with an exponential cannot generally restore original
amplitude precision already absent from its input. In addition, a fixed Q24
signed32 spectrum cannot represent every legal positive-gain result. Early
spectral clipping can change later IMDCT and overlap results. An implementation
must preserve sufficient precision and range throughout the floor and synthesis
path; fitting a reconstruction to the current six fixtures is insufficient.

The next implementation needs an explicit precision/range design before
production changes. It must retain the full original and equivalent corpus,
cover odd/even and order-one LSP, absent floor, zero amplitude, odd declared
rates, Bark boundaries and positive/zero/negative dB, and define conversions
without undefined behavior. Any wider or floating path needs independent
numerical checks and separate ESP32/C3 resource measurements. The boards have
different arithmetic capabilities; a QEMU result is not a physical audio
performance measurement.

No new floor0 renderer, private backend inspection, deferred public-book guard,
Ogg or AAC work is enabled by this analysis.

## Owned scaled coefficient core, 2026-10-25

The [wide numerical design](VORBIS_WIDE_NUMERIC_DESIGN.md) now defines the
precision boundary and the continuation through owned public raw operations.
Its first [implemented component](../idf/components/native_vorbis_numeric/README.md)
evaluates floor0 polynomials and amplitude/gain with normalized mantissas and
separate exponents. A scaled-denominator entry point allows the later stable
angle path to bypass irreversible cosine rounding. The module is not connected
to either radio application or the vendor inverse2 callback.

The [numerical checkpoint](../tests/results/vorbis-floor0-numeric-20261025/CHECKPOINT.md)
passes 60541 host operations with ASan/UBSan and a Decimal120 direct polynomial
oracle, including all 168 retained owned unit inputs. Separate native captures
and comparisons pass 327 exact-coefficient/gain cases on each architecture.
All original and expected data and the predeclared error policy are retained.
Host cosine/Bark approximation tests are a distinct layer; native finite API
groups do not qualify the complete angle-domain curve. Compiler frames are
recorded separately from complete task/libm stack usage.

This is an implemented numerical building block, not a complete floor0 decoder.
Original-angle evaluation was the next numerical layer at that checkpoint;
the implementation below now provides it. Owned dequantization/residue/coupling,
IMDCT/overlap, final PCM conversion and raw lifetime/retry/reset/integration
still need implementation and qualification. The historical full31 PCM
NONPASS remains open and is not requalified by coefficient-only tests.

## Original-angle arithmetic, 2026-10-25

The [original-angle checkpoint](../tests/results/vorbis-floor0-angles-20261025/CHECKPOINT.md)
adds denominator/gain entry points accepting all finite binary64 LSP angles
and the mathematical Bark-bin angle `pi*bin/map`. Fixed-size integer phase
reduction and scaled half-angle sine products avoid cosine subtraction and
subnormal halving. Exact-rational Machin/continued-fraction checks independently
certify the phase constant and grid; a separate Chudnovsky/Decimal direct-cosine
oracle checks the compiled arithmetic.

All 2376 host cases and 28 metadata controls pass ASan/UBSan. Both SDK/QEMU
captures finish 200 cases and eight API groups; separate comparison accepts
all 400 native values. The previous 60541-operation coefficient regression
also passes, with its complete output byte-identical to the prior checkpoint.
The composed gain uses a combined absolute/relative bound; a very large
relative error near zero is retained, not hidden or treated as exact gain.

This completes the standalone angle calculation, not the complete decoder.
The quantization/LSP stage below now supplies exact symbolic values without Q24
narrowing; complete owned entropy/setup and audio packet parsing are still
required. Residue/coupling/IMDCT/overlap must retain their range. Full31
reference PCM, public raw lifecycle/integration and G6/G8 remain required.

## Exact quantization/LSP handoff, 2026-10-25

The [quantization checkpoint](../tests/results/vorbis-quantization-20261025/CHECKPOINT.md)
implements raw quantization-section parsing/materialization and exact lazy
vector/scalar/LSP reconstruction. Original packed words plus integer multipliers
preserve values across the full exponent range; affine floor APIs consume the
two exact terms before a floating sum. Final partial vectors and the reference
cross-vector carry are retained. The [design](VORBIS_QUANTIZATION_DESIGN.md)
defines caller-owned storage, uint64 counts, error and lifetime contracts.

All 6572 host cases, 152 API controls and 79834 exact values pass (77573
reconstructed and 2261 direct affine inputs retained through floor calls);
92 affine floor comparisons pass against independent Fraction/Decimal1440
equations. Both native captures finish 200 cases/152 controls with zero warnings;
separate comparison accepts 15036 exact values and 184 floor results. The phase
constant/grid proof is separate from complete libm/FP accuracy. Previous
60541 coefficient and 2376 angle host output streams remain byte-identical.

This is an owned data-preservation layer. It does not validate a Huffman length
list, parse complete setup/audio packets, replace residue/transform/overlap or
register a production decoder. Historical full31 PCM failures, complete
floor0/G6/G8 and physical/radio acceptance remain open.

## Complete codebook and audio-word handoff, 2026-10-25

The [owned codebook checkpoint](../tests/results/vorbis-codebook-20261025/CHECKPOINT.md)
now supplies complete setup descriptors, entry-order Huffman assignment and
audio codeword decoding to the exact VQ/LSP layer. Original sparse indexes,
one-bit singleton behavior, partial vectors and aggregate cursor/output
transactions are covered by independent exact comparison. All 382 sanitized
host cases/719 controls and all 400 native cases pass. The host additionally
checks every setup and consumed-payload cut point for its finite input corpus.

This closes the standalone per-codebook dependency. Remaining floor/residue,
mapping/mode setup and audio packet handling must use that dependency through
an owned decoder. Wide coupling, floor multiplication, IMDCT/overlap, final
PCM and public raw lifetime/retry/reset/EOF integration are still required.
The historical full31 PCM NONPASS and complete floor0/G6/G8 are not requalified
by exact codeword/VQ checks; physical throughput and radio acceptance remain.

## Owned full setup and mode/window selection, 2026-10-25

The [complete setup checkpoint](../tests/results/vorbis-setup-20261025/CHECKPOINT.md)
now supplies floor/residue/mapping/mode configuration and audio-prefix selection
above the codebook layer. Independent exact comparison accepts all 300 sanitized
host rows and 400 native rows, including complete configuration/getter values.
The retained real encoder-derived header cases are host-only and preserve their
stored bodies; no new reference decoder or PCM process is implied.

Configuration preserves unsigned floor0 zero metadata because section6.2.1
does not state positive header minima; Xiph rejects those values earlier.
Active zero-order/rate/Bark-map arithmetic and packet treatment remain explicit
subsequent requirements, without an invented constant-floor policy. Other
remaining work is complete floor/residue audio decoding, wide synthesis/final
PCM and public raw lifecycle/ownership integration. This does not requalify
historical full31 failures, full floor0/G6/G8, physical or radio behavior.
