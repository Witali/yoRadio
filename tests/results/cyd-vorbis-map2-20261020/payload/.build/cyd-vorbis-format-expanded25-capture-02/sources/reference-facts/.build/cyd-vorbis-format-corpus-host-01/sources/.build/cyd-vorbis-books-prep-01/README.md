# Public raw Vorbis codebook corpus prep

This is a finite source/construction proposal. No codec, compiler, SDK or QEMU was invoked. Independent host PCM decoding and both target architectures are **pending**. Generated headers and packets are candidates for valid-format qualification, not conformance evidence by themselves.

`generate_books.py` uses only Python stdlib and the byte-identical `base_minimal.py` snapshot of `tests/vorbis_block_matrix/generate_minimal.py` (SHA256 `8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1`). It reuses the existing bit writer, public identification/comment writers and Ogg page/CRC helpers. It replaces the book, residue classification and audio token construction. The frozen snapshot's default matrix generation is never called.

## Finite coverage

All eight cases use stereo, 192000 Hz, short/long blocks 256/2048, floor1 with two endpoint values 255, residue1 over the first 16 coefficients, one 16-coefficient partition/channel, and `SSLLLSLSSSLLSS` modes. Its 13 overlaps are SS=4, SL=3, LS=3, LL=3; all four long-window neighbor flag combinations occur. Primer output is zero; expected overlap frames are `(previous_N + current_N)/4`. Each case totals 7040 frames/channel and 28160 PCM16 bytes; the corpus totals 112 raw packets and 225280 PCM16 bytes. A decoded packet needs at most 4096 bytes, within the existing 16384-byte guarded output arrays.

Each setup has a dense, complete, dimension1 lookup0 classbook with scalar entries 0 and 1, both selected in audio. Residue classifications are 2, both stage0 cascades select vector book1. Sparse holes occur in the vector book only. Every active vector entry is selected repeatedly; no unused entry is encoded.

| Case ID | Length coding | Vector lookup | Dimension | sequence_p |
|---|---|---:|---:|---:|
| ordered_lattice_d2_seq0 | ordered `[1,3,3,3,3]` | 1 | 2 | 0 |
| unordered_lattice_d2_seq0 | unordered dense `[3,1,3,3,3]` | 1 | 2 | 0 |
| sparse_lattice_d2_seq0 | unordered sparse `[1,0,2,3,0,3]` | 1 | 2 | 0 |
| ordered_lattice_d2_seq1 | ordered `[1,3,3,3,3]` | 1 | 2 | 1 |
| ordered_explicit_d2_seq0 | ordered `[1,3,3,3,3]` | 2 | 2 | 0 |
| unordered_explicit_d2_seq1 | unordered dense `[3,1,3,3,3]` | 2 | 2 | 1 |
| sparse_explicit_d4_seq0 | unordered sparse `[1,0,2,3,0,3]` | 2 | 4 | 0 |
| sparse_explicit_d4_seq1 | unordered sparse `[1,0,2,3,0,3]` | 2 | 4 | 1 |

Length0 marks unused entries 1 and 4. All trees satisfy Kraft sum1; no single-entry tree/erratum is used. Ordered packing includes an actual length2 count0 between the length1 and length3 groups. Unordered dense entries decrease from length3 to length1, exercising entry-order assignment rather than merely choosing the unordered syntax for sorted lengths. `matrix.json` records each MSb-first codeword and its reversed integer for the LSb writer. The generator checks the specification's eight-entry example separately.

Vector minimum=-1, delta=1 and two-bit multiplicands 0/2 produce bounded nonzero vectors. Type1 has integer `lookup_values=2` for entries5 and entries6, so higher original entries deliberately repeat some lattice coordinates. Type2 stores **all entries x dimensions** multiplicands including unused slots; table offsets keep original entry indices. The sparse d4 table distinguishes original entry2 from compacted entry1. Sequence accumulation resets for each decoded vector, not once per packet/channel.

## Output and repeatable construction

From this prep directory, with the pinned Python executable in `construction.command.json`:

```powershell
python -B generate_books.py --output generated02
python -B test_books.py
```

`generated01` is the executed construction and remains unchanged. Output must be a fresh direct child of this prep; files are create-only. Each case in `generated01/matrix.json` exposes relative `identification` (full30-byte header), `setup` (full type5 + vorbis prefix), `comment`, `audio` (concatenated full raw packets), `ogg`, `offsets`, `mode_flags`, `rate/channels/short/long`, per-packet frames/PCM sizes, natural cumulative granules and named features. The raw decoder adapter must strip the 7-byte setup prefix only where the existing public configuration API requires its payload. Do not strip or alter audio packets.

`reference.ogg` is a host carrier: one complete packet per page, all three headers first, primer granule0, subsequent granules equal cumulative raw overlap, and EOS only on the final packet with the natural final count. The carrier is not a target Ogg test. No target Ogg/EOF/reset/ownership, OOM, AAC, private decoder state or full-radio hook is involved.

`bitfields.json` retains byte/field offsets; `construction-checks.json` separates syntax checks from pending decoding. The eight host test methods check known word assignments/reversal, actual serialized book parsing including the ordered zero-count group, sparse original-index vectors, sequence resets, actual audio tokens/classes/padding, positive/equivalent/different spectra, malformed construction/CRC rejection, and manifest/carrier/count accounting. The token scan stops before floor synthesis/MDCT; it produces no PCM and is not an independent decoder.

## Required root-owned qualification

1. Pin actual reference tools and run independent Xiph/libvorbis and FFmpeg native decoding of each full carrier. Read actual identification and WAV metadata; never force `-ar`/`-ac`. Require rate192000, channels2, PCM16, exactly7040 frames/channel, nonzero complete output, per-frame natural durations and retained diagnostics. Check nonzero output for each present transition. Record any reference refusal honestly; two implementations agreeing is useful evidence, not a proof of full Vorbis conformance.
2. For each reference implementation separately, require byte-identical PCM for `{ordered_lattice_d2_seq0, unordered_lattice_d2_seq0, ordered_explicit_d2_seq0}` and `{ordered_lattice_d2_seq1, unordered_explicit_d2_seq1}`. Their complete spectral vectors/modes/floors are identical; only public book representation/Huffman packing differs. Require differing nonzero PCM for the seq0/seq1 pairs declared in the matrix. Cross-implementation float rounding is separate and needs measured evidence; do not demand cross-vendor byte equality or waive count/metadata errors.
3. Freeze the independently qualified actual packets/header/setup bytes. Open a fresh **original public vendor** handle first for every case, then a fresh checked handle, both at the recorded192000 rate. Check persistent per-handle output metadata on every packet, full input consumption, exact expected output bytes including primer0, 16-byte guards around output buffers and byte-exact original-vs-checked PCM per packet. Require nonzero per present transition and exact finite case/packet/order counts. No generic error, timeout, interruption or panic is a pass. CYD/Xtensa and C3/RV32 remain separate qualifications.

## Primary basis and limits

The [Vorbis I specification](https://xiph.org/vorbis/doc/Vorbis_I_spec.html), sections3.2.1/3.3, defines ordered/sparse entries, entry-order Huffman assignment, lookup0 scalar use, lookup1 lattice coordinates, lookup2 original-entry tables and sequence accumulation; sections4.3/8.6 define packet ordering/overlap and residue1 vectors. The implementation was checked against the public [Xiph1.3.7 sharedbook source](https://github.com/xiph/vorbis/blob/v1.3.7/lib/sharedbook.c), specifically `_make_words` and `_book_unquantize`. No Xiph implementation source was copied. These finite cases cover selected valid representations, not all dimensions/books/entropy patterns, malformed formats or resource limits. Construction alone cannot establish output nonzero PCM, target support or absence of decoder bugs.
