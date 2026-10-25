# Xiph resource port and original31 regression, 2026-10-25

The focused source port passes host ASan/UBSan and the ESP32 SDK/QEMU fixture.
Both runs reproduce every original 31 PCM byte exactly: **434 packets, 738560
bytes / 369280 signed16 samples, maximum error 0 and all 14 original relations**.
The project bound remains 2, with no trimming, shift, gain fit, discarded case
or synthetic tail. The [unchanged source baseline](../vorbis-xiph-20261025/CHECKPOINT.md)
remains separate and unchanged.

## Implemented changes

[native_vorbis_xiph_port](../../../idf/components/native_vorbis_xiph_port/README.md)
uses the same complete 20-unit Vorbis plus 2-unit Ogg source target. Its
[materializer](../../../idf/components/native_vorbis_xiph_port/prepare.py)
retains all 116 baseline files under `base/` and selects exactly three modified
translation units. Eight declared before/after fragments must match uniquely;
there is no fuzzy patching. `PORTING.json` binds all 119 generated source files
and the record itself is the 120th file. The original release source and licenses
remain byte-identical in the sibling component and generated baseline copy.

- `_vorbis_block_ripcord` frees the old reap chain and performs optional arena
  consolidation only with a representable positive growth size. On realloc
  failure it retains the current pointer/capacity; accounting is reset and the
  arena remains reusable. No failure inside `_vorbis_block_alloc` is covered
  by this change.
- Decode-book initialization moves `codep` and `sortindex` to checked heap
  storage, checks owned persistent allocations and cleans partial ownership.
  `_make_words` and `_book_unquantize` check sizes and allocation results.
  Zero-dimensional lookup2 scalar/unused books retain valid zero-write
  behavior with either NULL or non-NULL zero-sized allocation. An unsigned cast
  defines the existing first-table word shift without changing its intended
  32-bit word.
- The first actual sanitized original 31 run stops at libogg 1.3.5's signed byte
  shift (`241 << 25`) during a valid setup read. Four reader functions backport
  the 16 unsigned-long byte shifts already present in
  [official libogg 1.3.6](https://github.com/xiph/ogg/blob/v1.3.6/src/bitwise.c).
  The [read](https://xiph.org/ogg/doc/libogg/oggpack_read.html) and
  [look](https://xiph.org/ogg/doc/libogg/oggpack_look.html) state contracts are
  preserved. The rest of the pinned 1.3.5 library is retained.

Base manifest SHA:
`897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
Resource-port manifest SHA:
`9103e35103d6a19fc3532a82eacc48a9c951685033cb7759f6c79a517af4a079`.

## Meaningful resource tests

[Arena tests](../../native/vorbis_xiph_arena.c) cover 11 scenarios: failure with
multiple live reap blocks, retained bytes, allocation-free reuse, later actual
growth, close after failed growth, empty cleanup and overflow boundaries.
[Book tests](../../native/vorbis_xiph_books.c) complete 200864 checks, including
dense 4096 length12 scalar words, sparse original-entry remapping, lookup1/2,
sequence0/1, singleton/empty books and normal/forced-NULL zero-size policies.
All 61 selected hook-allocation ordinals across eight positive-dimensional
initialization scenarios are refused in turn, followed by cleanup and a
successful semantic reopen. The dense upper word 100000000000 must decode
original entry 2048. Expected values/words are independent hand-derived data.

[Bit tests](../../native/vorbis_xiph_bits.c) perform 124754 probes using a
bit-at-a-time LSB/MSB oracle, literal high-byte patterns, all available buffer
positions and widths 0..32, plus selected invalid widths -1/33 and end-of-packet
cases. Look must preserve position; read must advance correctly. This is not
a claim about all out-of-contract int widths.

The [host runner](../../test-vorbis-xiph-resources.py) compiles all 22 library
units and five fixture C units with ASan/UBSan and active assertions. All31
owned Linux commands have normal terminals, reaped children and vanished
owned groups. Sanitizer execution stderr is empty. The actual host markers
report11/200864/124754 and zero remaining hook ownership before/after the
original31 public raw synthesis run.

The [native caller](../../target/vorbis_xiph_port_qemu/main/main.c) runs the
same resource tests on **core1, priority3, stack16384**, with coordinator core0.
SDK6.0.2/Xtensa machine94 compiles all22 library plus5 fixture units. The
[controller](../../run-vorbis-xiph-port-qemu.py) checks exact generated source
selection, dependencies, allocator injection only into the library, symbols,
ELF and22 compiler stack records. No vendor archive, wrapper or second baseline
decoder is linked. Nine owned commands terminate normally. All38 resource
records pass, including zero live hook allocations/bytes after each of31
public cases and at final completion.

The separate [numerical checker](../../test-vorbis-xiph-port-pcm.py) replays
every raw protocol record and actual input/build/tool byte binding. Its pure
arithmetic is AST-identical to the earlier comparator. All369280 native S16
samples match the retained references exactly. Sixteen pure materializer,
eight protocol and twelve PCM/binding tests pass.

The observed cumulative native minimum free heap is180292 bytes and minimum
remaining worker stack14572 bytes. The selected dense4096 initialization thus
fits this16KiB worker. Its own compiler frame is64 bytes, static; neither
that frame nor the observed task minimum bounds all dynamic call trees.
Instrumentation adds static state and allocations, so these values are not
production margins or a measured memory saving. libc qsort may allocate/use
its own scratch outside `_ogg_*` injection; the failure sweep is not a complete
transitive libc allocation proof.

## Diagnostics, failed attempts and archive

Clang-Tidy completes all 27 units with 308 warnings and zero parse errors.
Six findings are SDK headers, 301 are upstream-derived, and one is the deliberate
test-hook `calloc(0,...)` used to exercise legal zero-size allocation behavior.
Arena/book/bit test files have zero findings. The five visible GCC diagnostics
are the same inherited block indentation and bounded encoder-only LPC/psy
warnings recorded in the unchanged baseline; narrow warning-as-error adapters
remain unchanged. No sanitizer or warning is hidden for a passing result.

The initial sanitizer halt and its complete source/binary/process records are
retained as NONPASS. The first protocol-suite attempt uses a sandbox default
temporary directory and fails cleanup with WinError5. The test-only fix creates
and verifies prefixed directories under the task's `.build`; it leaves native
inputs unchanged. The original test body and both receipts are retained.

Host report SHA:
`d3a89f3c90d9a558b940052e662674024ea20dda09e1c78a649e68466bc93b27`.
Native capture SHA:
`326771fd085f2d843132ed912bf44f9e91d91618e1689412ca133b24f816bdf8`.
Separate numerical report SHA:
`c52d1c9ce85a5c5a91a4a0905e8909d6230681e5ed85163b4ea564d5ea4ca085`.

[captures.zip](captures.zip) contains1777 members /17211263 bytes and has SHA
`d08775a7c267936ecc5e4eb0e867e118b443679670ab692bec000bbcb07ff742`.
[archive.json](archive.json) binds its complete member manifest.
The [offline verifier](../../verify-vorbis-xiph-resources-checkpoint.py) checks
every saved member, exact source changes and shared host/native source bodies,
owned process terminals, raw resource/API records and independently recomputed
PCM/packet/relation results. It launches no compiler, SDK, decoder, QEMU or
external process. Actual [publication replay](publication/verify.json) exits0
with max0. External runtime executables and the complete SDK/libc/header/binary
dependency closure are not embedded or claimed.

## Remaining work

These repairs do **not** establish general decoder OOM recovery or a complete
16KiB stack bound. Unchecked allocations remain in header/comment unpacking,
DSP/transform initialization, packet arenas, floor maps and residue lookup
construction. `vorbis_book_decodevs_add` separately has two partition-sized
stack arrays: a legal4096-scalar residue0 partition with dimension1 needs32KiB
of scratch on ESP32. Test/port that path and make public failure recovery
coherent before production selection. Full uint32 rate, floor0 amplitude/VQ
range coverage, other retained format cases and runtime integration remain.

Neither production radio nor task/display/audio settings are changed. Deferred
vendor scopes remain deferred. C3 and physical throughput/backend/heap-margin
acceptance remain open; this checkpoint qualifies only the stated source port,
selected resource cases and unchanged original31 PCM regression.
