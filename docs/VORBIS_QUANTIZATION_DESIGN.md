# Exact quantization values for owned Vorbis synthesis

The [owned numerical component](../idf/components/native_vorbis_numeric/README.md)
now includes [quantization fields and lazy reconstruction](../idf/components/native_vorbis_numeric/quant.c).
It follows [Vorbis I 3.2 and 9.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
without consuming a vendor book or extending an opaque handle. It remains
outside both radio application component lists.

## Original data and lookup

The measure API starts at the four-bit lookup type after the codeword lengths.
It preserves the original packed minimum/delta words, dimensions, declared
entries, sequence flag, value width, required multiplicand count and bit extent.
Lookup1 uses an integer root and repeated quotient/remainder entry digits;
lookup2 retains all declared rows, including sparse-unused rows. Selecting a
used entry is the separate entropy layer's responsibility. This API does not
validate a Huffman length list or parse the rest of the setup header.

The maximum lookup2 count is `(2^24-1)*(2^16-1) = 1099494785025`, independently
of target `size_t`. Counts/spans use uint64; storage uses addressable caller
capacity. Materialization remeasures and matches the layout before any write.
Truncation and metadata errors precede a capacity refusal, and refusal leaves
storage and the book unchanged. The parser allocates nothing and does not
expand a complete table of floating vectors. Empty lookup0/2 metadata is
retained at this layer; lookup1 with zero dimensions has no defined integer
root. Positive-dimensional VQ and consuming-context validation remain distinct.

An exact reconstructed scalar is stored as two raw packed words and two
unsigned integer multipliers:

`value = unpack(minimum_bits)*A + unpack(delta_bits)*B`.

For sequence0, `A=1` and `B=q[j]`; sequence1 uses `A=j+1` and the prefix sum of
the multiplicands for `B`. Dimension/value limits give `A<=65535` and
`B<=65535^2=4294836225`. Vector-prefix and single-component APIs avoid allocating
unused output. The scalar API can evaluate component65534 without an entire
65535-element output row. All requested data are checked before committing
outputs; packet, entries and book/storage are immutable and disjoint from
outputs during calls.

## Floor0 handoff without an early floating sum

[Xiph sharedbook.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c)
confirms the per-vector sequence recurrence. The normative packed-float
formula uses the full exponent `exp10-788`; the reference's exponent clamp is
an implementation limit and is not copied. The
[floor0 reference loop](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor0.c)
retains a separate last coefficient across vectors from one selected book.
The owned LSP builder does the same, discarding only the unused final prefix
tail. The specification's step6/step11 restart numbering is ambiguous about
resetting that carry, so this detail is checked against the actual reference
loop and its final-prefix behavior.

The affine form survives exact cancellation and large exponent differences.
Each packed21-bit mantissa times a uint32 multiplier is less than2^53 and is
exactly representable before binary scaling. The two resulting binary64 terms
are individually exact and finite; their floating sum can lose a small term.
The new affine floor API therefore reduces them separately and combines their
phases as integers. It never rounds their sum into an ordinary LSP double.

The phase grid now has2304 fractional bits with a4096-bit `2/pi` constant.
Every exact affine value is `N*2^-788` with magnitude less than2^289. Separate
exact-rational certificates bound nonzero phase separation for these values
and the earlier full binary64 domain. This certifies the grid/constant budget,
not libm accuracy or the full synthesis/PCM result. The original double-angle
and supplied-coefficient APIs remain separate layers.

## Remaining decoder work

This implements a quantization section and exact entry/LSP value layer. The
owned decoder still needs entropy/codeword setup, complete floor/residue/mapping
configuration, audio packet handling, wide residue/coupling, transform/overlap,
PCM conversion and public raw lifecycle/integration. Original full31 PCM
failures and G6/G8 remain open. It does not resume the deferred public-consumer
guard, Ogg or AAC work. Production task cores/priorities/stacks, display and
audio backends remain unchanged; emulator frames do not establish physical
throughput or complete task/heap margins.

The [actual checkpoint](../tests/results/vorbis-quantization-20261025/CHECKPOINT.md)
retains 6572 sanitized host cases/152 controls/79834 exact values and 92 independent
affine floor comparisons. Separate replay accepts 200 cases on each SDK/QEMU
architecture, including 15036 exact values and 184 floor comparisons. Both old
host output streams remain byte-identical. Complete library/codec/physical
qualification does not follow from these standalone API checks.
