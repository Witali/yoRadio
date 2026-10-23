# Additive public wide lookup2 quant-width control

This source proposal adds eight valid encodings of the existing four dimension16
lookup2 inputs. For each sparse/dense and sequence0/1 original, it changes the
declared quant width from2 to9 and16 while preserving every unsigned multiplicand
0..3, minimum−1, delta1, dimension16, Huffman/tree fields, and sequence flag.
All original rows, including unused sparse rows, remain present. The resulting
mathematical vectors are expected to be identical at all three widths.

Only the setup `value_bits_minus1` field and the widths used to encode the same
multiplicands change. ID, comment and complete audio bytes remain identical.
The complete valid host-reference carrier keeps the original serial, page
numbers, granules and flags. Only its setup page changes, including required
lacing/length and CRC fields. Other page bytes must be identical. No transport,
EOF/reset, malformed-input, private-handle, proprietary-binary, or deferred
scope is involved.

The original four public inputs and every existing17/25-case corpus are
preserved. Existing CYD and C3 full25 numerical NONPASS results, the bound2
project policy and both failed wide sparse/dense target relations remain
unchanged. Wider equivalent encodings may help compare valid storage-width
paths; this proposal does not attribute an opaque implementation cause, propose
a production repair, or assume that a width control will improve target PCM.
The specific public-source hypothesis is the type3 consumer's scalar-storage
branch at `q_bits <= 8` versus `q_bits > 8`. Widths9 and16 exercise the latter
while preserving exact mathematical vectors. This says nothing about the
opaque target consumer's implementation.

## Frozen source and ordinary imports

`originals/` contains byte-identical copies of the original four ID, comment,
setup, audio and complete reference carrier files, plus the full original matrix
SHA `7ec364dea889ead32407d90914b7f6fb91d515d03dfa82dd6a1f7affdac139b8`.
The source-only freeze completed with exit0, chunk `2906a5`; it copied20 raw
files and that matrix, and did not invoke a generator, witness or codec.
`source-pins.json` SHA is
`75cb073a50c88b93086ebddf18a83108cdda69b46a96f3f7c1a29dadad97db96`.

The future generator uses ordinary SHA-pinned canonical module imports:

- `tests/vorbis_format_corpus/generate_map2_regression.py`,
  `49015a8a849682ad886c970ea3b1a3bc06f02f21a4f01785b7d52695e23d3caa`.
- `tests/vorbis_format_corpus/generate_books.py`,
  `de9b09de59a0825feda741c0343c6d60821ddad1258ce7df5ae342c68e268fc1`.
- `tests/vorbis_block_matrix/generate_minimal.py`,
  `8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1`.

Their guarded generator mains are not called. No helper is copied, monkeypatched,
or rebound. The original setup/audio encodings must reproduce the frozen bytes
before any additions are constructed. All source inputs are rehashed afterward.

## Separate additive and comparison scopes

`generate_width_controls.py` has create-only output in a fresh independent
checkout `.build` directory. It prepares:

- `additions8/matrix.json`: exactly8 new cases, qbits9 four then qbits16 four.
- `comparison12/matrix.json`: four original byte-identical copies, then those8
  additions, with four explicit `[original width2, width9, width16]` expected
  same-decoder PCM equality groups.

Original order is sparse sequence0, dense sequence0, sparse sequence1, dense
sequence1. Each matrix has its own raw copies and relative paths. Case, packet
and expected PCM counts are derived from descriptors. The expected counts are
112 packets/225280 PCM bytes for additions8 and168/337920 for comparison12.
These are declared geometry expectations, not actual observed PCM.

`bitfields.json` records canonical writer reports only. A root-owned independent
reference run is still required to establish real PCM equality. The new raw
inputs supplement existing corpora and cannot replace or reclassify any failure.

## Independent raw witness

`inspect_width_equivalence.py` imports only the standard library, with its own
bounded LSB bitreader, public packed-float-to-`Fraction` conversion, explicit
finite setup suffix scan, and bitwise carrier CRC implementation. It does not
import a writer or rely on writer field reports. It checks all original quant
rows and exact fractional vectors, unchanged Huffman/minimum/delta/sequence
fields, exact quant payload widths, unchanged setup prefix/suffix/padding,
complete metadata, and identical ID/comment/audio. It validates every carrier
page and requires every non-setup page to remain byte-identical.

Five in-memory construction controls exercise exact width, minimum, delta,
sequence and multiplicand invariance oracles. They never emit a target input.
The witness records exact vectors for every original entry, including holes.
Its successful construction result would establish wire/vector equivalence,
not independent decoder acceptance, numerical conformance or a target fix.

## Root-owned future steps

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 .build/cyd-vorbis-wide-width-prep-01/generate_width_controls.py --output '<fresh independent .build corpus>'
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 .build/cyd-vorbis-wide-width-prep-01/inspect_width_equivalence.py --corpus '<fresh independent .build corpus>' --output '<fresh independent .build witness.json>'
```

After source review and those actual construction receipts, the root owns
independent Xiph/reference qualification of all12, exact same-decoder equality
checks, and any later target campaign/measurement. Keep partial/NONPASS evidence.
No generator, witness, test, reference, compiler, SDK, QEMU, Git or physical
device operation was run by this source preparation. No full G6, format,
production-radio or physical acceptance is claimed.
