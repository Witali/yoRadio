# Six additive equivalent-LSP controls: source proposal only

This preparation does not run its generator or witness, tests, a reference,
compiler, SDK, QEMU, Git or device operation. Root must review the sources before
running the pending commands below. AST parsing and raw input hashing are the
only executed source checks. No new fixture or PCM result is claimed yet.

The original six floor0 cases, all nine floor/residue candidates, and the
existing complete 17/25 NONPASS campaigns remain untouched. These controls
supplement the failing original cases; they never replace them or qualify G6.
The project maximum absolute error policy2 remains unchanged. No amplitude,
rate, frame, channel, lag or output scaling adjustment is introduced.

## Exact representation change

The public [Vorbis I specification, lookup2 vector decode and floor0 packet decode](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
defines the scalar from the minimum, delta and unsigned multiplicand, then
separately accumulates the last LSP value between codebook vectors. The current
fixtures have sequence0, so the following identity holds for each scalar:

`0 + x * (1/16) = (1/16) + (x-1) * (1/16)`.

The nonzero minimum and unchanged delta are both packed `0x62000001`: mantissa1,
exponent784, hence exactly `2^(784-788) = 1/16` in Vorbis floating notation.
Original multiplicands7..25 become6..24, retaining their original five bits.
The dense two-entry dimension3 Huffman books and sequence0 flag remain identical.
Both coefficients and the extra unused scalar in order5 remain exact dyadic
values. None of this predicts an opaque decoder's result or diagnoses its code.

Only these original variants receive additions, across the same three block
pairs64/256,256/2048,64/2048:

- `floor0-even6-r0` to `floor0-even6-r0-minp1`;
- `floor0-odd5-r0` to `floor0-odd5-r0-minp1`.

The ID/comment headers, audio bytes, `packets.json`, amplitudes, book selectors,
Huffman words, residue words, modes, offsets, granules, rate/channels and frame
counts are copied byte-for-byte or required unchanged. Only the floor books'
minimum and multiplicand setup bits change. The carrier retains its original
serial, lacing, granules and page boundaries: only its setup packet payload and
the setup page CRC differ. Non-setup pages must remain byte-identical.

## Sources and outputs

`generate.py` is a distinct additive generator, not a monkeypatch of an older
generator. It normally imports the SHA-pinned canonical
`tests/vorbis_format_corpus/generate_floor0.py`, which normally imports the
SHA-pinned canonical minimal helper. It calls only the existing pure definitions
and first requires a byte-exact reconstruction of the frozen original setup.
It re-emits identical-width fields through `Bits`; no helper implementation is
copied or globally rebound. It reads all pinned files again before output.

All output is create-only in a fresh independent `.build` directory:

- `matrix.json`: precisely six additions, unique IDs ending in the same block pair.
- `comparison-matrix.json`: six unchanged copied originals followed by six
  additions, with six expected same-decoder PCM equality pairs. Existing host
  driver02 understands these pair declarations. A new actual campaign must
  measure them; construction cannot establish PCM equality.
- `relations.json`: original/new IDs, original matrix hash, exact changed field
  offsets/widths/values and actual raw file identities for each of six pairs.
- `construction-fields.json`: new setup reports and unchanged audio bit reports.
  Its configuration `books` continue to mean decoded vector components in1/16
  units, as they do in the original generator. An explicit `representation`
  declaration distinguishes the new minimum/multiplicands.
- `pure-checks.json` and a complete hashed `manifest.json`.
- Six raw/carrier/metadata files for each addition and each unchanged original
  copy:78 files total, including the six top-level JSON files.

`generator-from-canonical.diff` is the exact full source difference from the
pinned canonical floor generator to this separate generator. The large diff
reflects a different additive workflow, not edits to canonical code.
`transformation-contract.json` lists the six pairs and the exact allowed setup
changes without executing generation. `source-pins.json` binds the frozen
original input inventory, canonical helpers, unchanged historical NONPASS
reports and primary public source references. No web-byte hash is invented.

## Independent raw/Q24 witness

`witness.py` does not import either generator or any support helper. It reads the
actual encoded setup syntax bit-by-bit, obtaining offsets independently from the
bytes, validates the unchanged floor/residue/mapping/mode fields, and evaluates
the public lookup2 equation using `Fraction`. For each original/new floor book,
it requires exact component and signed32 Q24 equality; it then parses all84
audio packets independently and checks used and ignored accumulated LSP values,
amplitudes, selectors, original metadata, every offset/mode and frame count.
It independently recomputes every carrier CRC and validates every page against
raw packets, granules and the allowed setup-payload/CRC-only difference.

Three negative controls modify actual bit fields of an equivalent setup in
memory. Wrong minimum, wrong delta and one wrong multiplicand must each cause
its precise expected rejection. They are local construction controls only.
The witness does not compute a floor curve, residue synthesis, MDCT, PCM,
reference, audible quality or target acceptance. Its flags keep all these
qualifications false. These controls remain **unexecuted** in this preparation.

## Pending root-owned commands

From `C:/Work/yoRadio/.worktree/esp32-cyd-c3-review`, after review:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 `
  '.build/cyd-vorbis-floor0-equivalent-prep-01/generate.py' `
  --output '.build/cyd-vorbis-floor0-equivalent-generated-01'

& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 `
  '.build/cyd-vorbis-floor0-equivalent-prep-01/witness.py' `
  --repository 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review' `
  --generated '.build/cyd-vorbis-floor0-equivalent-generated-01' `
  --output '.build/cyd-vorbis-floor0-equivalent-witness-01/report.json'
```

Then run a separately owned/recorded actual host-reference campaign over
`comparison-matrix.json` through reviewed host driver02. Require all12 Xiph
outputs with exact complete PCM equality in each original/new pair, actual WAV
metadata/per-packet framemd5 and nonzero-channel checks. Native FFmpeg lookup2
refusals must retain their original NONPASS status. No claim follows from an
expected mathematical relation alone. Only after these checks should a separate
reviewed all-originals-plus-additions target contract/campaign be assembled.
Neither the old17 nor25 campaign may be overwritten, narrowed or relabeled.

Full G6, standard conformance, Ogg transport, fault/OOM/reset/lifetime controls,
callback ABI, radio integration, production and physical gates remain open.
No device, COM, flash, reset, network target, private vendor handle or binary
offset is involved.
