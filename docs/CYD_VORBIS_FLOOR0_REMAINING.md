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
Stable original-angle evaluation, owned dequantization/residue/coupling,
IMDCT/overlap, final PCM conversion and raw lifetime/retry/reset/integration
still need implementation and qualification. The historical full31 PCM
NONPASS remains open and is not requalified by coefficient-only tests.
