# AAC 16+16 storage: exponent range and eight-sample blocks

**Current policy (2026-10-02): production permits +/-3 PCM LSB; development permits +/-5.**
The older acceptance statements below describe the limits at measurement time.
Measured errors and archived evidence are unchanged. See [current precision policy](ESP32C3_AAC_PRECISION_POLICY.md).

## Selected representation

Use **`shift = exponent + 1`**, with a four-bit exponent `0..15` and shifts
**`1..16`**. Each complex sample has its own exponent shared only by its Re/Im
components. Store eight independent exponents in one `uint32_t` word, sample 0
in bits 3..0 and sample 7 in bits 31..28. This packs metadata without losing any
exponent bits; it does not give eight samples a common scale.

The experimental implementation is
[`packed_complex16.h`](../idf/esp32c3-oled-native/main/packed_complex16.h).
It is not linked into the production decoder and does not reduce its allocations.

| Exponent | Shift | Reconstruction multiplier |
| ---: | ---: | ---: |
| 0 | 1 | 2 |
| 1 | 2 | 4 |
| ... | ... | ... |
| 14 | 15 | 32768 |
| 15 | 16 | 65536 |

Select the **smallest shift after rounding** for which both signed mantissas
fit `[-32768,32767]`. Round to nearest, with ties away from zero. Arithmetic
after unpacking remains int32; a codec must not operate directly on these words.

## Why this range

Shifts `0..16` need 17 codes, which cannot fit four bits. Of the contiguous
16-step ranges with enough upper range for int32 inputs, `1..16` has the smallest
minimum step. It sacrifices exact storage of some small odd integers to retain
the upper range, without per-buffer scale metadata or an exception stream.

With a maximum shift of 15, the largest reconstructed positive value would be
`32767 * 32768 = 1073709056`, only about half of INT32_MAX. A table that skips an
intermediate shift can retain shift zero but doubles the quantization step at
that omitted scale. Such a table has no established advantage on our histories.

Do not choose the range solely from the FAAD recordings: the existing Espressif
14-bit history experiment reaches shift 18 on ABBA (one pair in the nearest
SBR-only run), whereas the FAAD fixed ABBA histories peak at shift 16 in that
14-bit representation. The backends use different scales. These observations
motivate checking the full int32 domain; they are not a new 16-bit PCM test.

### Boundaries and error

- Exact zero remains zero. At shift 1, `+1 -> +2` and `-1 -> -2`: at most one
  **internal int32 unit** of rounding error on that grid, not a PCM-LSB guarantee.
- INT32_MIN is represented exactly by mantissa -32768 at shift 16.
- A positive rounding carry at shift 16 is clamped to mantissa 32767 and counted.
  INT32_MAX therefore reconstructs to **2147418112**, with error **65535 internal
  units**. This is the explicit endpoint limitation of the signed representation,
  not integer wraparound or a claim of lossless int32 coverage.
- Without saturation, each component's error is at most `2^(shift-1)`;
  at the saturating endpoint it is at most `2^16-1`.

The implementation uses unsigned magnitude/bit operations and defined signed
multiplication; it avoids `abs(INT32_MIN)`, signed shifts and signed overflow.

## Process eight complex samples at a time

`pc16_pack8` reads eight Re/Im pairs, writes eight mantissa words and returns one
combined exponent word. The caller writes that exponent word once. There is no
per-sample read/modify/write of the exponent array in this path.

`pc16_unpack8` takes one exponent word by value, extracts its low nibble and
shifts the local word by four for each pair. The caller loads the exponent word
once. Exponent selection and rounding still occur independently for each pair.

```c
// Separate aligned arrays: N mantissa words, ceil(N/8) exponent words.
// Input/output arrays do not overlap. Initialize exponent words for tail writes.
for (size_t n = 0; n + 8 <= N; n += 8)
    exponents[n / 8] = pc16_pack8(real + n, imag + n, mantissas + n, NULL);

for (size_t n = 0; n + 8 <= N; n += 8)
    pc16_unpack8(mantissas + n, exponents[n / 8], real_out + n, imag_out + n);
// Use pc16_store / pc16_load for the remaining N % 8 samples.
```

A full block needs **36 bytes instead of 64**, or 43.75% payload saving.
Separate arrays need `4*N + 4*ceil(N/8)` bytes: for 1197 pairs, **5388 bytes**, a
theoretical saving of **4188 bytes** before scratch, allocator and alignment costs.
No padded per-sample structure is used. Shared exponent words require single-writer
ownership; this API does not provide atomic concurrent nibble updates.

The block path reduces metadata memory operations at the source level. RV32 CPU
speed, cache effects and net RAM saving remain unmeasured. Existing decoder
allocations are unchanged.

## Validation and remaining qualification

Run `python tests/test-aac-pc16-shifts.py` (native GCC on Linux, WSL GCC on Windows).
It compiles the actual header with `-O2`, warnings as errors and undefined-behavior
sanitization, then executes an independent int64 division oracle.

The [retained arithmetic result](../tests/results/aac-pc16-shifts-20261001/result.json)
records:

- 2,097,152 decoded component-code checks: all 65536 mantissa codes, all 16
  exponents, separately in Re and Im;
- 1,788,108 input pairs, including int32 extrema, all exponent boundaries,
  half-way rounding, small integers and deterministic random inputs;
- 19,152 nibble updates with adjacent-word/nibble preservation checks;
- 65,536 mixed-scale eight-pair blocks, bit-identical to individual packing and
  unpacking, with guard checks, saturation counts and a separate partial-tail test.

All passed with no UBSan error. This selects and checks the storage arithmetic;
it does **not** yet qualify final PCM precision, decoding speed or reduced codec
allocations. The old BFP16 experiment quantized analysis output at a different
boundary. The subsequent [201 history-only decoder comparisons](ESP32C3_AAC_PC16_QUALITY_20261001.md)
pass the temporary **±5 PCM LSB** limit but still fail the final **±2 PCM LSB**
limit with a maximum of 3 LSB. Block/scalar error statistics match.
