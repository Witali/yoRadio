# Unchanged Xiph ESP32 baseline, 2026-10-25

The ready upstream decoder passes **all 31 original cases with bit-identical
PCM**: 434 audio packets, 738560 bytes / 369280 signed16 samples and all 14
declared relations. Every case has maximum absolute error **0**, within the
unchanged project limit of 2. This includes all 16 cases rejected by the
[previous repair checkpoint](../vorbis-current-format31-20261024/CHECKPOINT.md).
The old repair's historical NONPASS remains unchanged; this is a separate
complete upstream candidate, not a reclassification of its results.

## Source and actual execution

[native_vorbis_xiph](../../../idf/components/native_vorbis_xiph/README.md)
retains 110 byte-identical source/provenance members of the official
libvorbis 1.3.7 and libogg 1.3.5 release archives. Their published SHA-256
identities, licenses, file hashes and placeholder-only platform type header
are preserved. The SDK compiles the official 20-unit base Vorbis target plus
libogg bitwise/framing. No custom transform, floor, residue or synthesis
implementation replaces upstream arithmetic.

The adapter defines HAVE_ALLOCA_H, links libm and disables fast math and floating
contraction. Actual GCC 15 diagnostics required a component-only
`-Wno-error=misleading-indentation` and file-scoped
`-Wno-error=maybe-uninitialized` for encoder-only lpc.c/psy.c. The five warnings
remain visible. The latter routines initialize their arrays for the positive
orders/sizes supplied by their upstream callers. No upstream C/header was
changed to resolve a diagnostic.

ESP-IDF 6.0.2, native Xtensa ELF machine94 and the pinned ESP32 QEMU execute the
public three-header/synthesis/blockin/pcmout/read sequence. Original complete
headers, comments, audio bytes, numbering, granules and EOS are retained.
Finite float PCM uses scale32768, explicit ties-to-even rounding, S16 clipping
and original L/R interleaving, matching the saved FFmpeg/libvorbis reference.
There is no sample trimming, shift, gain fit, resampling, synthetic tail or
discarded case. Input/PCM guards, unused output tails, metadata and API returns
are checked. Seventeen conversion controls and 2664 ordered capture records
complete. Source/data/ROM/tool identities, all 22 compile/dependency/stack-usage
rows, symbols, ELF, selected build outputs and nine owned command terminals
are retained. No Espressif codec archive or private decoder wrapper is linked.
Entry points are the [public raw caller](../../target/vorbis_xiph_qemu/main/main.c),
[capture controller](../../run-vorbis-xiph-qemu.py) and
[separate PCM comparator](../../test-vorbis-xiph-pcm.py).

Coordinator core0 and worker core1, priority3/stack16384, remain explicit. The
production application and its task settings are unchanged. The fixture's
cumulative minimum free heap is 225640 bytes; maximum observed open heap delta
is 44064 bytes; minimum remaining worker stack is 14596 bytes. These are isolated
emulator observations, not per-case transient peaks or production RAM margins.
Compiler frames do not bound complete dynamic call trees.

Capture report SHA-256:
`f82db17bc2699c12e5352a7f8d428801d7fcab1e0e3d23c32c252a8a6ac7d190`.
Independent numerical report SHA-256:
`ad3a08a3d0b51c12faebd6969fae3a8a6c6aa372ea7a48047398cca2279ebea2`.
Actual outer SDK/QEMU and comparison commands both terminate with exit0.

## Checks, failures and replay

Twelve protocol tests and nine numerical/receipt-selection unit tests pass.
An earlier eight-test version is retained as history. Clang-Tidy completes all
23 units without parse errors: 303 diagnostics comprise six SDK-header findings,
297 upstream findings and zero in the owned adapter. Most concern deliberate
floating conversions, pointer casts or encoder APIs. The concrete resource
findings below remain open.

The first native attempt fails during Windows sandbox DLL loading, before
compilation. Attempt2 rejects the three upstream indentation diagnostics;
attempt3 rejects the encoder LPC warning. A separate complete GCC probe exposes
the analogous encoder psychoacoustic warning. Its first two helper invocations
fail on dependency-option construction; their logs remain preserved. The first
Clang attempt mixes the SDK Picolibc overlays with bundled Newlib and fails;
the corrected explicit Clang builtin/Picolibc header selection completes.
Attempt4 compiles all units and completes every original case. No failed
attempt, original corpus or numerical threshold is overwritten.

[captures.zip](captures.zip) includes 1518 members, all actual PCM/reference
bytes, public release archives, frozen sources, reports, command streams and
selected binaries. [archive.json](archive.json) binds the ZIP and member
manifest. External executables and the complete SDK/header/binary dependency
closure are not embedded. [Publication receipts](publication/verify.json)
retain the actual offline verification terminal.

```powershell
python -B -X utf8 tests/verify-vorbis-xiph-checkpoint.py tests/results/vorbis-xiph-20261025/captures.zip
```

The verifier checks every saved member and upstream archive byte copy, reuses
only the pinned owned pure protocol reader, and independently recomputes all
direct S16 errors/packet spans and 14 relations. It launches no decoder, SDK,
compiler, QEMU or external process. Actual replay completes with exit0 and max0.

## Remaining production gates

Keep the existing Espressif Ogg/Vorbis radio path until these are addressed:

- `block.c:138` overwrites the arena pointer with unchecked realloc during
  synthesis/cleanup. Test allocation failure and recovery with valid streams;
  preserve the original allocation/state on failure.
- `sharedbook.c:355,367` creates two entry-sized stack arrays. A legal dense
  4096-entry length12 book needs at least 32768 bytes of simultaneous scratch
  on ESP32, beyond the 16KiB fixture worker. Test larger books and bound/move
  scratch allocation with controlled resource failure. This is source review,
  not a failure observed in the selected31.
- Check the other retained format cases and wide boundaries, including full
  uint32 rates, floor0 amplitude widths and VQ exponents. Upstream float/range
  limits do not establish universal Vorbis conformance from this finite corpus.
- Complete public raw/runtime integration and relevant lifecycle/resource
  gates before choosing a production decoder. Previously deferred vendor
  scopes stay deferred; this experiment adds no Ogg EOF/reset extension.
- Measure real CYD throughput, heap/stack margin and all audio backends once
  the board is connected. C3 and physical real-time performance are unqualified.

The reuse-first result supports continuing with this ready decoder and focused
integration/resource work. It does not require another custom IMDCT/synthesis
implementation or close the whole transfer plan.
