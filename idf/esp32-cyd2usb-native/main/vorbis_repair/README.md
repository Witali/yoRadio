# Isolated ESP32 Vorbis/Ogg bridge

The three checked setup/Ogg/output translation units are saved for stage 14.
The radio application's CMake, Kconfig and decoder registration do not enable
this bridge yet. The standalone target gate selects it explicitly. Ogg,
allocation-failure, format-coverage, SMP and actual-service qualification must
precede radio activation; a raw PCM fixture alone does not close those gates.

The donor is `idf/esp32c3-oled-native/main/vorbis_repair`. Its setup implementation
adapts Xiph.Org Tremor revision
[0ad0141e864cfbb130db4f22e279d421832e7336](https://android.googlesource.com/platform/external/tremor/+/0ad0141e864cfbb130db4f22e279d421832e7336/Tremor/),
with the BSD license retained in `COPYING`. Synthesis, MDCT, windows, residue
decoding and PCM conversion continue to use the pinned vendor archive. The
portable `floor1_render.h` replaces floor1 curve application through
`floor1_inverse2`, including the inverse-dB gain on short-endpoint tails.

The Xtensa CMake helper independently requires classic ESP32, the exact SDK
6.0.2 version tuple and both audited ESP32 codec 2.6.2 archive hashes. It adds
the exact three canonical files and their named linker wrappers. The ABI header
asserts ILP32 widths, field offsets, sizes and alignments with the target
compiler. The stripped vendor consumers corroborate selected fields; compiler
assertions are not proof of complete vendor type semantics or format coverage.

Checked setup publishes only a complete handle and frees partial children
through one owner chain. Ogg allocation failures are scoped per task, restoring
the previous scope after nesting. PCM capacity is checked before synthesis,
repeated undersized Ogg retries retain the pending packet, and a genuine final
byte adapts a separate empty EOF. These paths still require their own target
tests. Finite rate/block-size and floor-format regressions are recorded in the
transfer design; they do not establish full conformance.

The [floor1 renderer checkpoint](../../../../tests/results/vorbis-floor1-render-20261024/README.md)
compares every PCM16 sample with Xiph libvorbis for two eight-case banks on
both architectures at maximum error 1 under the project limit 2. A separate
old-tail image reproduces the original target vectors and their three large
errors. Same-image vendor/checked handles now share the renderer; their parity
does not provide an independent unchanged-vendor floor oracle. This adds no
ABI fields, allocations or changes to task cores, stacks or priorities.

See [the design and remaining gates](../../../../docs/CYD_VORBIS_TRANSFER_DESIGN.md)
and [the isolated target](../../../../tests/target/cyd_vorbis_qemu/README.md).

Checked raw open distinguishes actual positive-size allocation failure from
malformed setup failure using a task-local nested scope, restoring the previous
scope on every exit after validation. This preserves the public Espressif
`MEM_LACK` contract without new allocator calls, ABI fields or task bindings.
The [raw-open checkpoint](../../../../tests/results/vorbis-raw-open-oom-20261024/README.md)
covers all observed allocation positions in eight finite setups on both targets,
560 failures/recoveries per target, six malformed setups, four nested pairs and
two task-isolation scenarios. Full allocation/lifetime, Ogg, radio integration
and physical resource qualification remain open; TLS cost is not measured.

Lookup1 value counts use the exact integer root required by Vorbis I 9.2.3.
The previous unchecked power accumulators could overflow for positive encoded
fields, including entries2/dimension32 on ILP32. Both CYD and C3 now compare
against the entry bound before multiplication and use a converging integer
search. No dimension is clipped and no floating approximation is used. The
[arithmetic regression](../../../../tests/test-vorbis-quantvals.py) uses an
independent arbitrary-precision oracle; whole-source/native ABI compilation and
target arithmetic are separate from raw decoder/PCM and full G6 qualification.
