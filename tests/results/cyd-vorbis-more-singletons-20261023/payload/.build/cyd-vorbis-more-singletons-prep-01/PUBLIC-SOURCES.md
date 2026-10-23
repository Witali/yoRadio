# Primary public source basis

Consulted2026-10-23, source text only:

- https://xiph.org/vorbis/doc/Vorbis_I_spec.html — section3.2.1, Errata20150226:
  dense and sparse single-active-entry books, length1, one consumed bit, both
  branch values returning the sole used entry. The old zero-bit clarification
  is expressly superseded. Encoders are advised to emit the zero branch.
- The same specification, section3.2.1 lookup-type1/2 vector equations and
  section9.2.3 lookup1_values: lookup1 value count depends on declared entries
  and dimensions; lookup2 carries every original entry row even if unused.
- The same specification, sections8.6.2/8.6.3: both channel classwords precede
  per-channel vectors, and residue0 uses coordinate*step + vector placement.
- The same specification, section4.3.1 and appendixA: mode/window fields and
  complete header/audio Ogg encapsulation. The fourteen-mode finite profile
  and page layout are inherited from the existing reviewed construction.
- https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c — public
  Xiph libvorbis release tag v1.3.7, _make_words singleton handling and public
  lookup/vector math; consulted as corroboration, not executed or imported.
- https://xiph.org/ogg/doc/framing.html — complete packet lacing, page fields,
  direct CRC polynomial0x04c11db7, initial0, no final XOR, BOS/EOS and sequence.

These URLs and the release tag identify consulted primary references. Web tool
renderings were not downloaded into this preparation; no web-byte hashes or
unobserved download facts are claimed. source-pins.json hashes only actual local
original source bytes. The public setup storage-path intentions are derived from
the exact locally snapshotted owned setup.c, not from a private backend state.
