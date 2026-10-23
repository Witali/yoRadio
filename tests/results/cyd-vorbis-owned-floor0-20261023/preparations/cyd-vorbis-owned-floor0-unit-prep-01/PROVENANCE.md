# Source and claim boundaries

The actual production setup/ABI and their BSD COPYING are unchanged raw copies.
The four public Espressif declaration headers retain their original license
text and are compiled only for the ESP32 test project. No vendor archive,
implementation or stub is copied or linked.

The controlled allocation/bit-reader seams are extracted byte-for-byte from
the earlier owned-book unit, between `static unsigned current_case` and
`static uint8_t table_u8`. They are copied into an ordinary shared header;
only the enclosing protocol prefix belongs to the new floor unit.
`fixture_bits.py` reuses the exact bounded Reader/prefix definitions from the
independently reviewed equivalent-LSP witness. The new fixture syntax walker
uses those ordinary helpers and stops exactly after the floor book list.
It does not import the old witness, generator or any codec.

Local raw origins and snapshot hashes are in `source-pins.json`. Unmodified
controller/QMP/CMake/witness predecessors are kept in `provenance/`, alongside
exact source diffs. Metadata source assembly precedes the separate mandatory
independent raw syntax witness; neither constitutes actual production-C unit
execution. Pure synthetic semantic-control data is not a target transcript.

Header widths and floor book bounds follow
[Vorbis I6.2.1](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).
The public source context is
[Tremor floor0.c at0ad0141e864cfbb130db4f22e279d421832e7336](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/floor0.c).
No web bytes are assigned invented hashes. This unit calls our exact owned
production parser, rather than treating that public source as a replacement
or querying proprietary decoder memory.
