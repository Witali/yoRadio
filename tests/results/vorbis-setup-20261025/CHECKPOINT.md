# Complete owned setup and audio packet prefix

The [setup API](../../../idf/components/native_vorbis_numeric/include/native_vorbis_setup.h)
and [implementation](../../../idf/components/native_vorbis_numeric/setup.c)
now parse complete identification/setup headers and select an audio packet's
mode, block size and long-block window flags. The
[design](../../../docs/VORBIS_SETUP_DESIGN.md) records the public specification,
reference comparisons, storage representation and consuming-context boundary.
The component remains outside production decoder registration.

## Format and ownership

Identification retains full positive uint32 rates, channels 1..255, all 36
ordered block-size pairs 64..8192 and original signed32 bitrate hint patterns.
Setup handles 256 books and 64 time/floor/residue/mapping/mode descriptors,
both floors, all residues and mapping0's 256 possible coupling steps. It checks
book/link contexts, floor1's normative 65 unique posts, integer phrasebook
capacity, stage-vector partition divisibility and reserved/framing fields.
The ignored mapping time byte remains allowed and is retained verbatim.

Unsigned floor0 order/rate/Bark-map fields, including zero, are preserved at
this descriptor layer. Xiph rejects these zero values during setup; the
specification does not state those positive header minima. Active zero-domain
curve behavior remains a separate unresolved synthesis requirement. No
constant-floor result is invented. Reversed or oversized residue bounds also
remain metadata for later empty-range/clamping behavior.

The caller owns book views, active words, original multiplicands and a uint32
configuration pool sized by actual records. There is no maximum-sized union or
expanded classification map. A conservative configuration bound is 112960
words; full legal configurations can exceed an MCU's heap. Full validation and
object-byte RANGE/CAPACITY preflight precede materialization, with every
output/storage byte unchanged on refusal. Typed getters borrow immutable
configuration. Audio-prefix failure preserves its output and original cursor
position, with sticky EOP on truncation. One mode uses zero mode bits; short
blocks read no window flags.

The floor1 class getter takes an unchanged borrowed floor1 view from the same
setup argument; mixing views from different owners is outside that contract.

## Actual sanitized host campaign

All 300 rows and 60 guarded API controls pass strict GCC/ASan/UBSan. All four
nonce-owned commands terminate normally with exit 0 and reaped process groups.
The independent raw-bit/context parser and greedy-interval book oracle compare
every status, identification field, layout, nested book/word/multiplicand,
configuration word, getter value and audio prefix. Invalid rows remain in the
same complete result set; failed measurements are not dropped.
Actual refusals comprise 10 identification, 30 setup and three audio-prefix
cases. All 255 generated positive rows and both retained real-header rows are
accepted; no positive case is silently excluded by an unexpected parser error.

The corpus has 255 generated positive rows, 43 malformed rows and two retained
encoder-derived header/prefix cases. Successful setup rows contribute 855 book
configurations, 28270 raw configuration words and 26212 getter words. Actual
cutoff checks cover 67570 identification, 304814 setup and 775 consumed audio-
prefix bit positions, including output/storage/cursor preservation.

The retained [raw fixture](../../target/cyd_vorbis_format_qemu/main/fixture.h)
has source SHA256 `839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378`.
Its 23-byte identification body and 42-book setup body omit the normal seven-
byte header envelope. The new cases prepend only type+`vorbis`; every stored
body and selected audio byte remains unchanged. The
[origin README](../../target/cyd_vorbis_format_qemu/README.md) records an original
libvorbis encode at 192000 Hz/256+2048 blocks and the repository's preexisting
long-block exponent change to 8192. No new encoder/reference-decoder process,
Ogg runtime, EOF/reset or PCM comparison is performed here.

## Native capture and independent comparison

Each pinned SDK/QEMU campaign finishes 200 predeclared positive rows, 60 API
controls, 3551 ordered events and all nine owned commands with exit 0 and zero
build warnings. Actual ELF machine values are 94 (Xtensa) and 243 (RV32).
Coordinator core0 and worker core1/core0, priority3/stack16384 are isolated
test settings; production cores, priorities, stacks, display and audio paths
are unchanged. Dynamic guarded buffers/snapshots use actual per-case sizes,
avoiding an artificial Cartesian product of all format maxima in static DRAM.

Capture reports remain `CHECKED_SETUP_CAPTURED` with `passed=false` and numerical
qualification false. Separate comparison replays every one of the 300 host
rows, regenerates the complete corpus/predeclared native subset from original
fixture bytes, and accepts all 400 native rows: 1310 book configurations,
42580 configuration words and 39370 getter words, including every nested
codeword/multiplicand and audio prefix. The result is `FINITE_SETUP_QUALIFIED`.
The 43 malformed rows and per-input cutoff loops are host-only; native fixed
controls cover representative failures and its per-row cut counters remain 0.
The retained real-header cases are host-only as well.

All four component C units and public headers are compiled on both targets.
The largest own setup compiler frame is `setup_parse`, 2832 bytes on each;
materialization frames are 272/240 bytes and audio prefix96/96. These are
compiler per-function estimates, excluding callees and complete task high-water
or physical resource/performance measurements.

## Static analysis and legacy tools

Both eight-command cross-target Clang-Tidy module campaigns are retained. The
initial analyzer could not prove that every referenced floor1 class dimension
had been initialized. The final implementation counts partition occurrences
while reading them, then accumulates post counts during class decode; this
removes the deferred indexed read and reduces bounded scratch. Final setup,
codebook and quantization have zero warnings on Xtensa and RV32. Each target
retains the previously triaged floor0 widening warning: the signed32 product
is bounded because `high` is in 0..72. No full-application lint is claimed.

The four previous pure capture-reader suites pass 12/12/12/13 methods.
The new setup capture-reader suite passes 12 methods.
Reusable numeric/angle/quantization/codebook launchers now freeze setup source
dependencies without changing their CLI/protocol or historical checker pins.
Historical captures are not relabelled as executing these amended launchers.

## Remaining work

This is an owned configuration and prefix layer. Complete floor/residue packet
decoding, wide inverse coupling/floor multiplication/IMDCT/overlap, final PCM
conversion, header order/comment handling and public raw lifetime/retry/reset/
EOF/ownership integration remain required. Active zero-floor0 domains require
their own arithmetic/packet treatment. Historical full31 PCM NONPASS, G6/G8,
radio/physical acceptance and all explicitly deferred scopes remain open.
Isolated emulator images are test fixtures, not production firmware handoffs.
