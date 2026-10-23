# Public floor0 formula diagnostic: source-only proposal

This preparation has not evaluated any curve or formula, run its controls,
decoded audio, invoked a reference, compiler, SDK, QEMU or Git, or changed a
canonical file/campaign. Only primary-source reading, source assembly, AST
parsing and raw-byte identity checks are performed here. Root owns review and
execution. There are no measured requested-dB/gain results in this proposal.

The inputs are the six **original** floor0 cases, all14 packets each, both
channels, both actual block sizes and all16 nonzero residue bins per channel.
The prospective coverage is6 cases/84 packets/168 channel-packets/2688 bin
observations, including each primer. No equivalent-min control replaces an
original. The parent-owned new31/minimum experiment and original numeric
NONPASS remain separate evidence; no fixture or bound2 policy is changed.

## Primary formulas and scope

Sources are [Vorbis I6.2.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
[Xiph floor0.c](https://github.com/xiph/vorbis/blob/v1.3.7/lib/floor0.c),
[lsp.c](https://github.com/xiph/vorbis/blob/v1.3.7/lib/lsp.c),
[scales.h](https://github.com/xiph/vorbis/blob/v1.3.7/lib/scales.h), all libvorbis
files at tag `v1.3.7`, and
[public Tremor floor0.c](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/floor0.c)
at the stated immutable revision. Gitiles identifies that floor0 blob as
`864af70bdaf05d4e65ccde227a17277b675d592c`. Web bytes were not downloaded
or given fabricated SHA256 values; `source-references.json` records this.

For block B, this own diagnostic names n=B/2, linear frequency rate*i/(2n),
Nyquist-normalized frequency i/n and cycles/sample i/(2n). It computes the
corrected public Bark expression, its Nyquist normalization, integer Bark map
and mapped angle. The separate final linear Bark term is outside arctan,
as specified by erratum20150227. Unrounded scaled-map values and distance to
the closest integer boundary are retained for rounding analysis.

Own direct squared products use alternating LSP indices and the public
odd/even normalization. The result records p, q, their sum and square root,
amplitude_raw, amplitude_bits, denominator, offset, exact rational normalized
amplitude and requested dB. Gain uses exp(0.11512925*dB). Large gains retain
the finite exponent and explicit representation status instead of inventing
an infinite JSON value or inferring target arithmetic failure.

This is a mathematical binary64 diagnostic with a fixed evaluation order,
not bit-exact execution of libvorbis C float operations. Transcendental libm
results are not promised identical across operating systems. It does not
evaluate Tremor integer Bark stepping, cosine/inverse-square-root tables,
fixed-point products or its actual PCM. Its Q4 amplitude normalization is
recorded separately as a public parameter fact, not used to impersonate that
complete integer path.

Public Tremor's positive input-dB branch returns Q31 unity. The diagnostic
therefore adds an explicitly **conditional overlay**: if the same ideal
requested dB were supplied to that branch, a positive value would be limited
to unity. This identifies candidate conditions for later public-Tremor work.
It does not assert that integer approximations produce the same dB/map,
attribute behavior to the opaque vendor backend, or explain PCM errors from
clipping/overflow assumptions. Public Tremor PCM remains a separate gate.

## Original raw field witness

Thirty raw local inputs are copied unchanged and bound by `source-pins.json`:
the matrix/construction/manifest, four files for each original case and the
earlier reviewed witness/provenance. Nothing imports or monkeypatches a
generator, imports that witness, opens a vendor handle or examines a binary.
`provenance/reviewed-fixture-witness.py` is retained as exact reviewed history.
The earlier diagnosis text contains historical hypotheses, not new findings.

The new owned reader consumes every declared setup/audio field sequentially,
checks each offset/width/value, enforces byte bounds and verifies final padding.
It uses the actual raw values for floor fields, selected explicit book values,
amplitude, selector and wire words. Exact Fraction arithmetic reconstructs
LSP vectors and last-vector accumulation; the odd-order unused scalar is
recorded separately. Expected construction metadata is a cross-check, not a
substitute for reading the raw bits.

For these finite known codebooks, two floor entries have length1 and the
four residue entries length2. The bounded witness explicitly accounts for
the residue's reversed wire bits and residue0 dimension placement8 bins apart.
It independently requires all first16 values to equal the original metadata
and be nonzero. This fixture-specific extraction is not a general entropy,
residue or audio decoder, and produces no synthesis/MDCT/PCM.

## Proposed controls and execution

Five proposed control groups cover Bark zero/monotonic behavior, closed-form
odd/even normalization, independently expressed doubled-cosine products,
the dB exponential coefficient and an explicit positive-unity overlay case.
They have **not** been run during preparation. The numerical tolerances in
these algebra sanity checks concern this own formula only; they do not alter
the project's PCM bound or establish codec conformance.

After review, root may execute:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 `
  '.build/cyd-vorbis-floor0-curve-prep-01/curve_diagnostic.py' `
  --output '.build/cyd-vorbis-floor0-curve-run-01/report.json'
```

The output path must be fresh and separate from all input preparations.
The diagnostic rehashes every frozen input before and after evaluation and
includes its own raw source/pins hashes. It reads no PCM or target report.
Successful completion means only that all finite own-formula observations
were calculated; numeric/fullG6/vendor/production/physical flags stay false.
Only actual future output can establish which original bins request positive
dB under the declared formulas.
