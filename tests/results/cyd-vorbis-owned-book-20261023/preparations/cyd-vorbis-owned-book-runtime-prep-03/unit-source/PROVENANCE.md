# Source boundaries

`project/main/pinned/production/vorbis_repair/setup.c` and its adjacent ABI header
are raw byte copies of the actual reviewed production sources, not a reconstructed
parser. `book_unit.c` includes that entire translation unit and calls its static
`repair_vorbis_book_unpack` directly. The original BSD `COPYING` is retained.
All copied public Espressif headers retain their license text and are used only
for this ESP32-targeted project; no vendor archive is copied or linked.

The fixture matrices, bitfields and full raw setup bytes come unchanged from
the original frozen books8 and new8 source construction. `materialize.py` uses
ordinary stdlib imports. It never imports a generator, patches globals, invokes
a compiler or synthesizes PCM. It uses recorded expected vectors and raw bit
offsets. Their integer inverse quantization produces expected packed leaves;
the parser itself is never used to generate its expected data.

The bounded consumer in `book_unit.c` is an explicit adaptation of the public
Tremor `decode_packed_entry_number` and `decode_map` semantics from revision
[`0ad0141e864cfbb130db4f22e279d421832e7336`](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/codebook.c),
whose public `codebook.c` Gitiles blob is
`35aaeff81ed884aa02cd9232747bb7d8db5ec5d2`.
The codebook declaration is described by public
[`codebook.h`](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/codebook.h),
Gitiles blob `7519597ce7925373db219da74d1ad7d7cd6513c8`.
Web source raw bytes were not downloaded or assigned invented SHA256 values.

The consumer is not byte-identical upstream code. It supports only the actual
fixtures' node1/leaf1, node1/leaf2 and node4/leaf1 tables, decode types1/3,
q_bits2, finite nonzero minimum/delta and explicit point0. It adds owned-array
bounds and checked product range. These restrictions are documented test seams,
not production format restrictions. Its sole output is a VQ vector, never a
floor curve, residue synthesis, MDCT or PCM. Actual returned fields and raw
wide arrays are checked before that consumer, so vector checks do not substitute
for verifying our publication.

The normative vector rules are in
[Vorbis I3.2.1/3.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).
The independent expectations are construction metadata; their observed host
Xiph PCM qualification is separate historical evidence, not rerun or replaced
by this unit proposal. A passing future unit would not establish an opaque
vendor consumer contract, numeric PCM accuracy, floor0 or full G6.
