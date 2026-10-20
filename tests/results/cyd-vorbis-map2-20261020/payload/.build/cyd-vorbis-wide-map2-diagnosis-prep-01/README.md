# Wide lookup2: public source audit

The public dec_type3 construction is consistent with the pinned public Tremor
consumer. This review has not found an evidenced new setup correction. It does
not claim that the wide PCM problem is fixed, or establish the opaque vendor's
internal representation. No decoder, compiler, SDK, QEMU, PCM comparison, Git or
device operation ran in this preparation; the live root revert control was not
read or modified.

The root's completed25-case measurement remains **NONPASS**:
`.build/cyd-vorbis-format-expanded25-numeric-measurement-01/report.json`, SHA256
`8d3c6ff5ae60590b457a833cbf4eb208ed44fae2dd6d7802cc908d455fd2934a`.
The source-bound checked capture is `expanded25-capture-02`, session80043,
terminal chunk644c32; it captured25 cases/350 packets/623360 bytes with all nine
owned commands complete. These are existing bound records, not new execution.

| Cases | Root measured max absolute S16 error | Relevant relation |
| --- | ---: | --- |
| 8/9 sparse/dense dimension16, sequence0 | 65535 / 65535 | target equality fails |
| 10/11 sparse/dense dimension16, sequence1 | 65535 / 65535 | target equality fails |
| 12/13 single/twin dimension2, sequence0 | 1 / 1 | target equality passes |
| 14/15 single/twin dimension2, sequence1 | 1 / 1 | target equality passes |

All eight Xiph relations pass in the existing measurement. The original books8
remain within1; floor0 still fails independently. Bound2, every original25
output, both failed sparse/dense comparisons and full expanded NONPASS remain
unchanged. No failed case is omitted or reclassified.

## Source comparison

[Vorbis I3.2.1/3.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html) defines lookup2
as an explicit entry×dimension multiplicand list, including rows without a
Huffman codeword, followed by minimum/delta and optional vector accumulation.
The public format does not prescribe Tremor's internal byte-table layout.

The [fixture definitions](../../tests/vorbis_format_corpus/generate_map2_regression.py)
use dimension16/value_bits2/minimum−1/delta1 and sequence0/1. Sparse lengths are
`[1,0,2,3,0,3]`; active original rows are0/2/3/5. Dense lengths `[1,2,3,3]`
contain exactly those four rows. Their complete audio wires are equal. All
active entries are selected; vectors remain bounded integer spectra. These
construction facts and the independent Xiph equality are already recorded;
this audit does not compute or synthesize them again.

The local [setup.c](../../idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c)
SHA256 `6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c`
does the following:

- `decpack` returns the sequential used-entry index for dec_type3.
- `_make_words` maps both equivalent Huffman length lists to used indices0..3.
- The wide branch reads all original rows and stores active rows in that order.
  Sparse consumes96 scalars and retains64; dense consumes and retains64.
- With2×16+flag bits, the packed representation needs5 bytes, so it selects
  dec_type3. `q_pack=(q_bits+7)/8*dim` is16 bytes; each retained scalar is a byte.

That agrees with the pinned public
[Tremor codebook.c](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/codebook.c)
`decpack`, `vorbis_book_unpack` and `decode_map`: type3 indexes a row by
`entry*q_pack`, reads one-byte scalars when q_bits≤8, then applies minimum,
delta and sequence accumulation. The old public unpack's prefix-only read is
insufficient for sparse rows; the current full-read/compact branch repairs that
specific construction without changing these consumer semantics.

The local [codebook declaration](../../idf/esp32-cyd2usb-native/main/vorbis_repair_abi.h)
has the same member order/types as public
[Tremor codebook.h](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/codebook.h).
Existing ILP32 assertions constrain our declared layout. They do not prove every
vendor field interpretation or the vendor's dec_type3 implementation.

Unlike floor0's zero-minimum hypothesis, these books use minimum−1. Public
normalization predicts q_min=−2^30/point−30 and q_delta=2^28/point−28. Active
multiplicands0/2 fit the public signed32 product. There is no evidence here for
a wrong scale, byte stride, compact leaf index or scalar width in our source.
Changing q_pack units, switching indices back to original IDs or writing a
different scalar format would contradict the public consumer and would be a
backend guess. No such patch is proposed.

## Next unit gate: plan only

Do not use a live vendor handle or proprietary offsets. Test our own static
`repair_vorbis_book_unpack` at setup.c:364 on the original valid book bytes,
through a test translation unit or small controlled seam. No unit implementation
or execution is included here. Use the declared ILP32 ABI without disabling its
assertions to pretend a different host layout is equivalent.

1. Rehash the frozen setup/bitfield/matrix inputs. Position a public bit-reader
   at vector book1's sync field after scalar book0. Zero-initialize our codebook,
   as the real setup owner does, and keep input position/allocation facts.
2. Require dimension16, used_entries4, max_length3, dec_type3, nodeb1, leafw1,
   q_bits2, q_pack16, the normalized fields above and the declared sequence flag.
   Only logical `entries` should differ:6 sparse versus4 dense.
3. Read our owned returned arrays before cleanup. Expected decode-table bytes
   are `80 01 81 02 82 83`; codewords0/10/110/111 select compact rows0/1/2/3.
   q_val must be exactly these four16-byte rows in both books:
   `[2,0]×8`, `[0,2]×8`, `[2,2,0,0]×4`, `[0,0,2,2]×4`.
4. Use a pinned **public Tremor decode_map seam** on those returned structures
   and independently packed valid codewords. At explicit point0, sequence0
   expected rows are `[1,−1]×8`, `[−1,1]×8`, `[1,1,−1,−1]×4`,
   `[−1,−1,1,1]×4`; sequence1 gives `[1,0]×8`, `[−1,0]×8`,
   `[1,2,1,0]×4`, `[−1,−2,−1,0]×4`. Require exact values, bit consumption and
   sparse/dense equality. This point is an explicit public-unit contract, not
   an assumption about the opaque vendor's internal call arguments.
5. Clear through our owner once. Retain precise assertion/partial evidence if
   any gate fails; never call a decoder open or inspect a vendor handle.

If this gate fails, fix the demonstrated source difference narrowly and keep
the old failure evidence. If it passes, the field/leaf/vector construction has
an independent public consumer witness; the vendor interoperability/arithmetic
question remains open and cannot be answered by changing undocumented fields.
This does not itself qualify complete PCM, floor0, fullG6 or production use.

`source-pins.json` preserves local identities and primary URL/revision/blob
identities. Web raw bytes were not downloaded or assigned invented hashes.
`source-checks.json` records AST/raw-identity checks only. No new numeric or unit
qualification is claimed.
