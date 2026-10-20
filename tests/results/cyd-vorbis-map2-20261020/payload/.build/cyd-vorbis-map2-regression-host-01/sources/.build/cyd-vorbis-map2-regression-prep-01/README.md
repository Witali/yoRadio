# Public map2 valid-input regression construction

This is a fresh, source-only eight-case supplement. No decoder, reference tool,
SDK, compiler, QEMU, Git, private binary or device runs here; no actual PCM is
generated. All cases are complete candidate packets, with ample-buffer public
open/decode/close validation left to root. Earlier corpora/campaigns remain frozen.

The generator imports canonical `tests/vorbis_format_corpus/generate_books.py`
only after exact SHA256
`de9b09de59a0825feda741c0343c6d60821ddad1258ce7df5ae342c68e268fc1`.
That helper imports canonical `tests/vorbis_block_matrix/generate_minimal.py`,
whose actual path and SHA256
`8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1`
are independently checked. No helper copies, function replacements or global
rebinding are used. The reused helper writes/reads books, builds complete-tree
codewords, maps vectors, selects original entries, and supplies public bit/CRC
construction definitions. The only local tree exception accepts exactly one
declared entry with length1, emits code0, and consumes one bit per token.

Exactly eight stereo192000 cases use short256/long2048 and14 packets with modes
`SSLLLSLSSSLLSS`, covering all four adjacent transitions and long-neighbor states.
Every case expects7040 frames/channel and28160 s16le bytes; total112 raw packets,
225280 expected PCM bytes. These are overlap-accounting expectations, not decoded
observations. Floor1 rangebits10 gives endpoint1024, both y255 and multiplier1;
residue1 begin0/end16/partition16 uses two dense scalar classes and stagebook1.
The endpoint choice avoids conflating these map2 checks with the previously
documented native FFmpeg short-endpoint restriction.

Four explicitly declared future PCM equality groups are:

- `sparse_explicit_d16_seq0` ↔ `dense_active_d16_seq0`.
- `sparse_explicit_d16_seq1` ↔ `dense_active_d16_seq1`.
- `single_explicit_d2_seq0` ↔ `dense_twin_d2_seq0`.
- `single_explicit_d2_seq1` ↔ `dense_twin_d2_seq1`.

The sparse D16 book declares six original rows, lengths [1,0,2,3,0,3], active
original indices0/2/3/5 and holes1/4. All96 two-bit multiplicands are retained,
including two distinct unused rows. The dense ordered control has lengths
[1,2,3,3] and exactly those four active rows. Selected codewords/audio bytes and
integer spectra match within each pair. All four active entries are selected.
Two bits×16 dimensions=32 quantized bits; the current public setup expression
adds its leaf flag and yields5 storage bytes, directing this intended regression
to its wide map2 path. This is a source-derived expectation, not a target probe.

Original multiplicand rows (16 coordinates each) are:

- row0: [2,0] repeated8; row1: [3,0,1,2] repeated4 (unused).
- row2: [0,2] repeated8; row3: [2,2,0,0] repeated4.
- row4: [1,3,2,0] repeated4 (unused); row5: [0,0,2,2] repeated4.

The D2 single book declares one length1 mapped entry with two-bit multiplicands
[2,0], minimum-1, delta1. Its seq0 vector is [1,-1]; seq1 is [1,0]. The dense twin
has two identical rows and a complete [1,1] tree; both active entries are selected.
Thus each single/twin pair has equal integer spectra despite different entry
tokens. No malformed underpopulated book appears in the actual corpus.

Each case stores full30-byte ID, prefixed setup, comment, concatenated raw audio,
offsets/modes, every packet's expected frames/PCM, original-entry usage, exact
quantization rows, raw hashes, and CRC-checked Ogg reference carrier. Each audio
packet has its own page, primer granule0 and natural final EOS. Carriers serve
future host reference decoding only; no target Ogg path is involved.

The actual-byte bounded setup reader consumes every original map2 row before
checking the suffix. Audio scanning checks original entry tokens and padding;
integer vector accounting checks the four declared pair equalities. Eight pure
negative controls reject dropped original rows, incorrect prefix compaction,
illegal tree shapes, omitted single-entry token bits, nonidentical twin rows,
changed selected tokens and CRC corruption. Invalid controls remain in memory;
they are not target fixtures or actual decoder-fault tests.

```powershell
& $python -B .build/cyd-vorbis-map2-regression-prep-01/generate.py `
  --output .build/cyd-vorbis-map2-regression-prep-01/generated01
```

The [Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
3.2.1, defines lookup2 rows by original entry×dimensions, irrespective of sparse
codeword holes. Its Errata20150226 explicitly permits a single used length1
entry and requires consuming one bit; encoder code0 is used here. All other
underpopulation remains rejected in this construction API. Xiph v1.3.7
[_make_words/_book_unquantize](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c)
corroborates that exception and original-row lookup. The public setup source
read during design was `idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c`;
no production code is copied, executed or changed by this proposal.

Future root checks must keep all8 cases, preserve native lookup2 refusals as
nonpasses, validate actual metadata/packet durations/nonzero PCM and all four
same-decoder PCM equalities against independent references, then perform actual
public target capture and source/ABI closure. No tolerance is invented here.
No malformed-input target tests, resource pressure, errors, EOF/reset, private
state, AAC or hardware claims are in this scope.
