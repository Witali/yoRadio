# Xiph residue0 stack and nominal EOP, 2026-10-26

The focused port passes **3997 new residue scenarios** under host ASan/UBSan
and ESP32 SDK/QEMU. All original **31 streams, 434 packets and 738560 PCM bytes**
remain bit-identical to the retained references: maximum error0, unchanged
bound2, all14 original relations. No case, packet, sample or format is omitted.
The [preceding resource checkpoint](../vorbis-xiph-resources-20261025/CHECKPOINT.md)
and [unchanged upstream baseline](../vorbis-xiph-20261025/CHECKPOINT.md) remain
separate historical evidence.

## Change and standard contract

The [exact new source fragment](../../../idf/components/native_vorbis_xiph_port/edits/codebook-residue0.after.c)
changes `vorbis_book_decodevs_add` to decode each packed VQ word once and scatter
its values directly. Its two old arrays used `step * (sizeof(long) +
sizeof(float *))` stack bytes: **32768 bytes on ESP32 for partition4096/dim1**,
before other frames. The new loop allocates neither stack arrays nor heap.
This is a source-derived old scratch size, not a measurement of an old task
successfully surviving the oversized allocation.

[Vorbis I sections8.6.2–8.6.3](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
define per-word scatter and nominal EOP returning the values decoded so far.
The original Xiph helper buffered a whole partition's entries and discarded
its earlier complete words if a later word failed. The port now retains those
complete words. The failed word contributes nothing; the return remains-1,
which the existing residue caller handles as nominal EOP. The bit cursor is
unchanged relative to the same scalar word walk. Successful per-destination
floating additions remain the same; actual decoder PCM and book value arrays
are separate allocations. No second entropy pass or new OOM status is added.

Existing empty-book no-op and positive-dimension/internal geometry assumptions
are preserved. This does not qualify all empty/zero-dimensional VQ contexts.
Nonmultiple helper inputs leave their trailing `n % dim` values untouched;
valid residue0 setup still requires divisibility.

The [port materializer](../../../idf/components/native_vorbis_xiph_port/prepare.py)
now applies9 unique exact edits to4 compiled units, retaining all116 original
baseline files. Its generated tree contains120 source files plus `PORTING.json`.
All22 original library units remain selected. No private vendor handle, binary
inspection or deferred vendor/Ogg scope is involved.

Base manifest: `897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
Port manifest: `d56dbee024e53940b5551bd53a52fcf5139cd6f90e2f01184c872da296abfeab`.
Generator: `c21b388ecf728b6c04b7a51fd913e68893fc4157dd67dcd668d6926a022ca458`.

## Tests and actual target evidence

The [new C fixture](../../native/vorbis_xiph_residue.c) derives its oracle from
literal Huffman words and original-entry quantizers. It inverts scatter by
destination, independently of the implementation's packed-index scatter loop.
Dense, sparse/remapped and singleton books cover dimensions1/2/3/7/16/255,
sequence0/1, nonzero initial output, counts0/1/2/5/17, all initial bit offsets,
all prefix-bit cutoffs for these small shapes, nonmultiple tails and empty-book
no-op. Partition4096/dim1 has full success and selected large-prefix truncations.
Input/output guards, complete untouched regions, reader state, zero allocation
attempts under an armed failure hook and live ownership are checked.

Host compiles22 library plus6 fixture units under ASan/UBSan with active
assertions. All32 owned Linux commands terminate, reap children and release
their owned groups. Execute stderr is empty. Existing11 arena scenarios,
200864 book checks and124754 bit probes also pass. The same fixture runs on
ESP32 SDK6.0.2 with **core1, priority3, stack16384**, coordinator core0. All9
owned native commands terminate normally, all28 selected compilation rows and
22 library stack records are bound, and all40 resource records pass. Every
original stream closes with zero tracked allocation count and bytes.

The helper's GCC own frame is **32 bytes, static**. The observed cumulative
remaining worker stack is at least14560 bytes; minimum free heap is107940 bytes.
Large static test arrays and allocator instrumentation consume RAM, so these
are isolated fixture observations, not production margins or measured savings.
They do not bound all decoder call trees, channels or formats.

The original codebook unit was separately compiled and linked with the exact
same other host objects and fixtures. It aborts at the new output-prefix
comparison, fixture line104, before any PCM capture. Its actual-6 child result,
source/object/binary and process records are saved. The first outer witness
postcheck expected the expression text, whereas the CHECK macro asserts its
local `ok` variable; that outer result1 is retained unchanged. A subsequent
pure evaluation binds the actual assertion line to its source and confirms
the expected regression without rerunning the executable.

Separate numerical replay accepts every native S16 sample and all14 relations.
The original comparator arithmetic remains AST-identical. Pure generation16,
protocol11 and PCM/binding12 tests pass. Clang-Tidy completes all28 actual units:
310 warnings, zero parse errors. The previous308 findings remain; the new two
are intentional binary float-object comparisons at fixture104/125. Bit identity
is the assertion being tested, including untouched destinations. No warning or
sanitizer was suppressed. The new decoder loop introduces no additional
Clang warning; the five inherited GCC warnings and narrow build adapters remain.

## Retained evidence and remaining work

[captures.zip](captures.zip) contains1378 members /14448508 bytes.
SHA256: `6c769601ab8e725bb936598f9e9c0ef8f6f36c2688be31def2cf1fe709c562c9`.
Manifest SHA256: `1eabd099b57397e4edaa7ec289aa094a05880250682442b53a9561d69f72f3cf`.
Sources, generated units, host objects/executables, original-codebook failure,
SDK images/ELF, raw logs/PCM, numerical replay, warnings and owned process
receipts are retained. These raw QEMU fixture images are not production firmware.

The [offline verifier](../../verify-vorbis-xiph-residue-checkpoint.py) passes
against the saved ZIP. It checks every member, exact edits, original failure,
raw resource/protocol and both complete PCM captures without a decoder, SDK,
compiler, extraction or external process. Publication receipts are beside this
file. This archive does not embed a complete external SDK/tool/libc dependency
closure or independently attest compiler execution.

Next: general allocation-failure propagation/recovery, remaining channel-sized
scratch, uint32 rates, floor0 amplitude widths and VQ numeric ranges, then public
runtime integration. The existing Espressif radio path and task affinities are
unchanged. Backend acceptance, physical timing/audio/heap, TLS reserves and
the other open transfer-plan gates remain; the board is not connected.
