# Floor0 public source diagnosis: preparation only

The bound root measurement completed all17 cases and rejected the unchanged
project bound2. Eight books and three floor1/residue0 controls have max error1;
the six floor0 cases fail. This audit does not remeasure PCM, diagnose an opaque
decoder from those errors, change fixtures or weaken policy. Mapping2 repair and
the remaining floor0/G6 gap are separate results. The original NONPASS remains.

The root report is `.build/cyd-vorbis-format-checked-numeric-measurement-02/report.json`,
SHA256 `80ec50711edd6463b0e3420293729e47f1adf26d29f7e61f1a959c4ffcb2f11c`.
Its six floor0 maxima are40664/1649/40664 and65535/65535/65535.
These are bound report metadata, not a fresh measurement by this preparation.

## What the source supports

The current [setup parser](../../idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c#L613)
reads order/rate/barkmap/ampbits/ampdB/book-count with widths8/16/16/6/8/4,
then book indices8. This agrees with [Vorbis I6.2.1–3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
and [public pinned Tremor](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/floor0.c#284).
The fixture selector correctly uses ilog(number-of-books). An extra final scalar
for order5/dimension3 is allowed; six decoded scalars supply five used values.
The spec defines the Bark mapping, separate odd/even products and exponential
gain; the floor0 section gives no embedded-profile omission for this behavior.
Section1.2.4 also retains floor0 as part of the format. These are scoped source
findings, not a conformance certificate or a universal S16 tolerance.

The [local ABI declaration](../../idf/esp32-cyd2usb-native/main/vorbis_repair_abi.h#L65)
has the same member order as [public Tremor codec_internal.h:64–72](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/codec_internal.h#64).
Its `unsigned char books[16]` differs from upstream plain `char`; fixture indices
are only2/3, so this signedness difference does not change these values. Existing
ILP32 size/offset assertions establish the declared layout, not all opaque vendor
field semantics. No new vendor ABI proof was performed here.

The [fixture source](../../tests/vorbis_format_corpus/generate_floor0.py#L21)
uses rate48000, stereo and ampdB60. Even6 uses ampbits6/barkmap64/one book;
odd5 uses ampbits8/barkmap128/two books. Floor books are dense two-entry,
dimension3, lookup2, sequence0, q_min0, q_delta`0x62000001` =1/16.
Vector values are7..25, selector words0/1 and last-vector accumulation are
explicit. Used LSPs are increasing dyadic angles below3 radians. No wrong field,
selector width or units error is established by this source review.

The local normalization gives q_delta=2^25, q_delp=−29, q_bits5.
Public Tremor requests Q24 for floor0; the largest fixture multiplicand product
25×2^25 fits signed32, and shifting by5 gives exactly value×2^20.
This argues against a simple quantization scale/overflow explanation for these
values. It does not prove the vendor runs identical arithmetic.

## Discriminating hypotheses, not a diagnosed repair

1. **Zero-minimum representation.** Local `_float32_unpack` sets point−9999
   for zero. [Public Tremor codebook.c:727–732](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/codebook.c#727)
   subsequently forms `point-q_minp` and right-shifts q_min by that count.
   At floor point−24 this is a shift9975 on a 32-bit zero: undefined in C,
   although hardware often returns zero. The eight passing books instead use
   minimum−1, so their result does not cover this representation. Whether the
   opaque vendor uses this code or exhibits a zero-minimum failure is unknown.
   A minimal equivalent-vector control sets minimum1/16 and subtracts1 from
   each multiplicand, retaining delta1/16/sequence0/q_bits5 and every audio byte.
   Each component remains exactly x/16; independently require equal Xiph PCM.
2. **Positive gain saturation.** [Public Tremor floor0.c:47–59](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/floor0.c#47)
   saturates positive dB input to Q31 unity. [Xiph libvorbis lsp.c:228–257](https://github.com/xiph/vorbis/blob/v1.3.7/lib/lsp.c#L228)
   uses an exponential. Establish whether actual active bins request positive
   gain and whether a separately pinned public Tremor reproduces the mismatch.
   No curve evaluation or decoder was executed here, and this audit does not
   assert that every failing packet crosses that boundary.
3. **Bark/bin approximation or fixed-point products.** Public Tremor uses tables
   and integer frequency stepping, while libvorbis computes its Bark mapping
   directly. Public floor0.c:124–140/244–275 and libvorbis floor0.c:102–129 show
   the difference. Compare maps and requested gain at the original active bins
   before attributing error to a book or to parity. Public inverse1 stores a
   Q4 amplitude and Q24 coefficients (Tremor floor0.c:311–330); that interface is
   distinct from the local setup fields. Actual vendor equivalence is unproven.
4. **Floor-specific bridge interpretation.** An equivalent-LSP book encoding
   control and a test of the local parser's own returned fields would isolate
   setup/book publication from downstream floor synthesis. Do not inspect
   proprietary offsets or infer their contents from header size assertions.

Order5/6 alone is not an explanation: parity, amplitude width, Bark size,
book count and coefficient choices all change together in the present fixtures.
Likewise, S16 endpoint differences do not by themselves establish bad gain,
clipping cause, channel swap or a particular integer overflow.

## Proposed tests, root-owned and not executed here

- Run the pure `inspect_fixture_fields.py` after source review. It rehashes
  frozen construction inputs, independently extracts their actual bit fields
  and checks exact dyadic/Q24 values and packet floor metadata. It performs no
  curve, residue, synthesis, reference or PCM computation. Its result is only a
  construction witness, never numeric qualification.
- In an isolated unit test of **our** parser, supply the actual setup payload
  and controlled public bit-reader seam, then compare its returned floor fields
  and book quantization fields with that witness. Do not inspect live vendor
  handles. This is proposed compiler work for root, not run by this preparation.
- Keep all original six failing fixtures; compare the same bytes through an
  explicitly pinned public Tremor build and Xiph, retaining full per-packet PCM
  and source/terminal facts. Separately inspect public requested-dB/map values
  at the original residue's active bins. This tests the saturation/approximation
  hypothesis without making an opaque vendor the oracle.
- First add the minimum1/16/multiplicand-minus1 control above; retain the
  original zero-minimum failures and independently require byte-equal Xiph
  output. It changes representation without changing any decoded LSP value.
- Add separate valid, independently referenced diagnostics: identical used LSPs
  encoded with dimension1 versus3 and lookup1 versus2; and matched order5/6
  cases holding ampbits/Bark size/book count fixed. A lower-amplitude case can
  test a predicted saturation boundary, but must not replace existing cases or
  close their failed gate. Verify equivalent-LSP PCM relations before target use.

The original bound2 remains a project regression criterion. Full G6, format
conformance, production, Ogg transport, error/OOM/reset, physical and unrelated
codec qualification remain unclaimed. No policy, decoder or canonical source
change is proposed by this audit.

`source-pins.json` records local raw identities and primary source URLs/revisions.
Web source raw bytes were not downloaded or assigned fabricated hashes.
`source-checks.json` records AST and local raw-hash checks only. The fixture
inspection proposal itself remains unrun.
