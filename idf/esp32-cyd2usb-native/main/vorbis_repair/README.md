# Isolated ESP32 Vorbis/Ogg bridge

The three checked setup/Ogg/output translation units are saved for stage 14.
The radio application's CMake, Kconfig and decoder registration do not enable
this bridge yet. The standalone target gate selects it explicitly. Ogg,
allocation-failure, format-coverage, SMP and actual-service qualification must
precede radio activation; a raw PCM fixture alone does not close those gates.

The donor is `idf/esp32c3-oled-native/main/vorbis_repair`. Its setup implementation
adapts Xiph.Org Tremor revision
[0ad0141e864cfbb130db4f22e279d421832e7336](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/),
with the BSD license retained in `COPYING`. Synthesis, MDCT, windows, floor and
residue decoding and PCM arithmetic continue to use the pinned vendor archive.

The Xtensa CMake helper independently requires classic ESP32, the exact SDK
6.0.2 version tuple and both audited ESP32 codec 2.6.2 archive hashes. It adds
the exact three canonical files and nine named linker wrappers. The ABI header
asserts ILP32 widths, field offsets, sizes and alignments with the target
compiler. The stripped vendor consumers corroborate selected fields; compiler
assertions are not proof of complete vendor type semantics or format coverage.

Checked setup publishes only a complete handle and frees partial children
through one owner chain. Ogg allocation failures are scoped per task, restoring
the previous scope after nesting. PCM capacity is checked before synthesis,
repeated undersized Ogg retries retain the pending packet, and a genuine final
byte adapts a separate empty EOF. These paths still require their own target
tests. The donor's inherited rate/block-size limits are retained for now and
remain an explicit conformance item in the transfer design.

See [the design and remaining gates](../../../../docs/CYD_VORBIS_TRANSFER_DESIGN.md)
and [the isolated target](../../../../tests/target/cyd_vorbis_qemu/README.md).
